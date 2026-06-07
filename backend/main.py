"""
Zenith Hermes — Backend API (single-file for deployment)
AI Agent Infrastructure on Base
"""
import os
import uuid
import httpx
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ═══════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////data/zenith.db")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════
def utcnow():
    return datetime.now(timezone.utc)


def gen_id():
    return uuid.uuid4().hex[:16]


# ═══════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════
class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=gen_id)
    wallet_address: Mapped[str] = mapped_column(String(42), unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    total_earned: Mapped[float] = mapped_column(Float, default=0.0)
    zna_staked: Mapped[float] = mapped_column(Float, default=0.0)


class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=gen_id)
    owner_wallet: Mapped[str] = mapped_column(String(42), index=True)
    name: Mapped[str] = mapped_column(String(128))
    template: Mapped[str] = mapped_column(String(64), default="Trading Bot")
    skills: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(16), default="idle")
    total_earned: Mapped[float] = mapped_column(Float, default=0.0)
    invocations: Mapped[int] = mapped_column(Integer, default=0)
    uptime_hours: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    category: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[str] = mapped_column(String(16), default="1.0.0")
    creator_wallet: Mapped[str | None] = mapped_column(String(42), nullable=True)
    installs: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=gen_id)
    wallet_address: Mapped[str] = mapped_column(String(42), index=True)
    action: Mapped[str] = mapped_column(String(64))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class PlaygroundMessage(Base):
    __tablename__ = "playground_messages"
    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=gen_id)
    session_id: Mapped[str] = mapped_column(String(32), index=True)
    wallet_address: Mapped[str | None] = mapped_column(String(42), nullable=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    agent_type: Mapped[str] = mapped_column(String(32), default="alpha-hunter")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# ═══════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════
class UserCreate(BaseModel):
    wallet_address: str = Field(..., min_length=42, max_length=42)
    username: str | None = None

class UserOut(BaseModel):
    id: str
    wallet_address: str
    username: str | None
    created_at: datetime
    last_seen: datetime
    total_earned: float
    zna_staked: float
    model_config = {"from_attributes": True}

class AgentCreate(BaseModel):
    owner_wallet: str = Field(..., min_length=42, max_length=42)
    name: str = Field(..., min_length=1, max_length=128)
    template: str = "Trading Bot"
    skills: list[str] = []

class AgentUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    skills: list[str] | None = None

class AgentOut(BaseModel):
    id: str
    owner_wallet: str
    name: str
    template: str
    skills: list[str]
    status: str
    total_earned: float
    invocations: int
    uptime_hours: float
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class SkillOut(BaseModel):
    id: str
    name: str
    category: str
    description: str
    version: str
    creator_wallet: str | None
    installs: int
    rating: float
    is_verified: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class ActivityOut(BaseModel):
    id: str
    wallet_address: str
    action: str
    details: str
    created_at: datetime
    model_config = {"from_attributes": True}

class PlaygroundChat(BaseModel):
    message: str = Field(..., min_length=1)
    agent_type: str = "alpha-hunter"
    session_id: str | None = None
    wallet_address: str | None = None

class PlaygroundResponse(BaseModel):
    reply: str
    session_id: str
    agent_type: str

class DashboardStats(BaseModel):
    total_agents: int
    total_skills: int
    total_earned: float
    total_users: int
    active_agents: int


# ═══════════════════════════════════════════
# SEED DATA
# ═══════════════════════════════════════════
SKILLS_SEED = [
    ("Uniswap V3 Swap", "DEFI", "Execute token swaps via Uniswap V3 on Base"),
    ("Aerodrome Router", "DEFI", "Route trades through Aerodrome DEX"),
    ("Aave Lend/Borrow", "DEFI", "Automated lending and borrowing on Aave V3"),
    ("Curve Pool Manager", "DEFI", "Manage stablecoin pools on Curve Finance"),
    ("Balancer Flash Loan", "DEFI", "Execute flash loans via Balancer"),
    ("Compound Supply", "DEFI", "Supply assets to Compound protocol"),
    ("1inch Aggregator", "DEFI", "Multi-DEX aggregation for best swap rates"),
    ("GPT-4o Inference", "AI/LLM", "Run inference via OpenAI GPT-4o"),
    ("Claude Analysis", "AI/LLM", "Deep analysis via Anthropic Claude"),
    ("Llama 3 Local", "AI/LLM", "Local LLM inference with Meta Llama 3"),
    ("Sentiment Analyzer", "AI/LLM", "NLP sentiment analysis for crypto markets"),
    ("Text Embeddings", "AI/LLM", "Generate vector embeddings for semantic search"),
    ("Image Recognition", "AI/LLM", "Classify and analyze chart images"),
    ("Code Generator", "AI/LLM", "Generate Solidity/JS code from natural language"),
    ("Dune Analytics", "DATA", "Query Dune dashboards for on-chain data"),
    ("The Graph Query", "DATA", "Query subgraphs for indexed blockchain data"),
    ("DefiLlama Fetch", "DATA", "Fetch TVL, yield, and protocol data"),
    ("Etherscan Scanner", "DATA", "Scan contract events and transactions"),
    ("CoinGecko Price", "DATA", "Real-time price data from CoinGecko API"),
    ("Nansen Tracker", "DATA", "Track smart money wallet movements"),
    ("Arkham Intel", "DATA", "On-chain intelligence and entity labeling"),
    ("Twitter/X Monitor", "SOCIAL", "Monitor crypto Twitter for alpha signals"),
    ("Discord Notifier", "SOCIAL", "Send alerts to Discord channels"),
    ("Telegram Bot", "SOCIAL", "Interact via Telegram bot interface"),
    ("Farcaster Post", "SOCIAL", "Post updates to Farcaster protocol"),
    ("Reddit Scraper", "SOCIAL", "Monitor crypto subreddits for sentiment"),
    ("Lens Protocol", "SOCIAL", "Social interactions on Lens Protocol"),
    ("Push Notifications", "SOCIAL", "Browser push notifications for alerts"),
    ("Chainlink Price Feed", "ORACLE", "Decentralized price feeds from Chainlink"),
    ("Pyth Network", "ORACLE", "High-frequency price data from Pyth"),
    ("Band Protocol", "ORACLE", "Cross-chain oracle data from Band"),
    ("API3 dAPI", "ORACLE", "First-party oracle data via API3"),
    ("Redstone Oracle", "ORACLE", "Modular oracle with EVM-compatible data"),
    ("UMA Optimistic Oracle", "ORACLE", "Dispute-based oracle for complex queries"),
    ("Tellor Reporter", "ORACLE", "Community-powered oracle reports"),
    ("Slither Audit", "SECURITY", "Static analysis for Solidity contracts"),
    ("Forta Alerts", "SECURITY", "Real-time threat detection alerts"),
    ("OpenZeppelin Defender", "SECURITY", "Automated security monitoring"),
    ("Rug Check", "SECURITY", "Detect potential rug pulls and scams"),
    ("Permit Scanner", "SECURITY", "Scan for malicious token approvals"),
    ("MEV Protection", "SECURITY", "Protect transactions from MEV bots"),
    ("Gas Optimizer", "SECURITY", "Optimize gas usage for transactions"),
    ("Base Bridge", "CHAIN", "Bridge assets to/from Base L2"),
    ("Optimism Gateway", "CHAIN", "Cross-chain ops with Optimism"),
    ("Arbitrum Bridge", "CHAIN", "Bridge to Arbitrum One"),
    ("LayerZero Send", "CHAIN", "Omnichain messaging via LayerZero"),
    ("Wormhole Transfer", "CHAIN", "Cross-chain token transfers"),
    ("Axelar GMP", "CHAIN", "General message passing across chains"),
    ("Hyperlane Dispatch", "CHAIN", "Permissionless interchain messaging"),
    ("IPFS Pin", "STORAGE", "Pin data to IPFS for permanent storage"),
    ("Arweave Store", "STORAGE", "Permanent data storage on Arweave"),
    ("Filecoin Deal", "STORAGE", "Decentralized storage deals on Filecoin"),
    ("Ceramic Stream", "STORAGE", "Mutable data streams on Ceramic"),
    ("Lit Protocol Encrypt", "STORAGE", "Decentralized access control & encryption"),
    ("Tableland SQL", "STORAGE", "SQL queries on decentralized tables"),
    ("Polybase DB", "STORAGE", "Decentralized database operations"),
]


async def seed_skills():
    async with async_session() as db:
        result = await db.execute(select(Skill).limit(1))
        if result.scalar_one_or_none():
            return
        for name, category, description in SKILLS_SEED:
            skill = Skill(name=name, category=category, description=description, is_verified=True)
            db.add(skill)
        await db.commit()


# ═══════════════════════════════════════════
# APP
# ═══════════════════════════════════════════
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    await seed_skills()
    yield


app = FastAPI(
    title="Zenith Hermes API",
    description="AI Agent Infrastructure on Base — deploy, compose, and monetize agents",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════
@app.get("/health")
async def health():
    return {"status": "ok", "service": "zenith-hermes-api", "version": "0.1.0"}


# ═══════════════════════════════════════════
# USERS / WALLET AUTH
# ═══════════════════════════════════════════
@app.post("/api/users/connect", response_model=UserOut)
async def connect_wallet(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.wallet_address == data.wallet_address.lower())
    )
    user = result.scalar_one_or_none()
    if user:
        user.last_seen = utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    user = User(wallet_address=data.wallet_address.lower(), username=data.username)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    act = Activity(wallet_address=user.wallet_address, action="wallet_connected", details="First connection")
    db.add(act)
    await db.commit()
    return user


@app.get("/api/users/{wallet}", response_model=UserOut)
async def get_user(wallet: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.wallet_address == wallet.lower()))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    return user


# ═══════════════════════════════════════════
# AGENTS
# ═══════════════════════════════════════════
@app.post("/api/agents", response_model=AgentOut)
async def create_agent(data: AgentCreate, db: AsyncSession = Depends(get_db)):
    agent = Agent(
        owner_wallet=data.owner_wallet.lower(),
        name=data.name,
        template=data.template,
        skills=data.skills,
        status="idle",
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    act = Activity(
        wallet_address=data.owner_wallet.lower(),
        action="agent_deployed",
        details=f"Deployed agent '{data.name}' with {len(data.skills)} skills",
    )
    db.add(act)
    await db.commit()
    return agent


@app.get("/api/agents", response_model=list[AgentOut])
async def list_agents(
    wallet: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Agent).order_by(Agent.created_at.desc())
    if wallet:
        q = q.where(Agent.owner_wallet == wallet.lower())
    result = await db.execute(q)
    return result.scalars().all()


@app.get("/api/agents/{agent_id}", response_model=AgentOut)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


@app.patch("/api/agents/{agent_id}", response_model=AgentOut)
async def update_agent(agent_id: str, data: AgentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent not found")
    if data.name is not None:
        agent.name = data.name
    if data.status is not None:
        agent.status = data.status
    if data.skills is not None:
        agent.skills = data.skills
    await db.commit()
    await db.refresh(agent)
    return agent


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent not found")
    await db.delete(agent)
    await db.commit()
    return {"deleted": True}


# ═══════════════════════════════════════════
# SKILLS
# ═══════════════════════════════════════════
@app.get("/api/skills", response_model=list[SkillOut])
async def list_skills(
    category: str | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Skill).order_by(Skill.category, Skill.name)
    if category and category.upper() != "ALL":
        q = q.where(Skill.category == category.upper())
    if search:
        q = q.where(Skill.name.ilike(f"%{search}%"))
    result = await db.execute(q)
    return result.scalars().all()


@app.post("/api/skills/{skill_id}/install")
async def install_skill(skill_id: str, wallet: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(404, "Skill not found")
    skill.installs += 1
    await db.commit()

    act = Activity(wallet_address=wallet.lower(), action="skill_installed", details=f"Installed skill '{skill.name}'")
    db.add(act)
    await db.commit()
    return {"installed": True, "skill": skill.name, "total_installs": skill.installs}


# ═══════════════════════════════════════════
# ACTIVITIES
# ═══════════════════════════════════════════
@app.get("/api/activities", response_model=list[ActivityOut])
async def list_activities(
    wallet: str | None = Query(None),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    q = select(Activity).order_by(Activity.created_at.desc()).limit(limit)
    if wallet:
        q = q.where(Activity.wallet_address == wallet.lower())
    result = await db.execute(q)
    return result.scalars().all()


# ═══════════════════════════════════════════
# DASHBOARD STATS
# ═══════════════════════════════════════════
@app.get("/api/dashboard", response_model=DashboardStats)
async def dashboard_stats(
    wallet: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    if wallet:
        agents_q = select(func.count()).select_from(Agent).where(Agent.owner_wallet == wallet.lower())
        earned_q = select(func.coalesce(func.sum(Agent.total_earned), 0)).select_from(Agent).where(Agent.owner_wallet == wallet.lower())
        active_q = select(func.count()).select_from(Agent).where(Agent.owner_wallet == wallet.lower(), Agent.status == "running")
    else:
        agents_q = select(func.count()).select_from(Agent)
        earned_q = select(func.coalesce(func.sum(Agent.total_earned), 0)).select_from(Agent)
        active_q = select(func.count()).select_from(Agent).where(Agent.status == "running")

    skills_q = select(func.count()).select_from(Skill)
    users_q = select(func.count()).select_from(User)

    total_agents = (await db.execute(agents_q)).scalar()
    total_skills = (await db.execute(skills_q)).scalar()
    total_earned = float((await db.execute(earned_q)).scalar())
    total_users = (await db.execute(users_q)).scalar()
    active_agents = (await db.execute(active_q)).scalar()

    return DashboardStats(
        total_agents=total_agents,
        total_skills=total_skills,
        total_earned=total_earned,
        total_users=total_users,
        active_agents=active_agents,
    )


# ═══════════════════════════════════════════
# PLAYGROUND (AI CHAT)
# ═══════════════════════════════════════════
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "https://token-plan-sgp.xiaomimimo.com/v1/chat/completions")
LLM_API_KEY = os.getenv("LLM_API_KEY", "tp-sjvc5v7vw1o0ir1db5wnxgdnuq3eojuebv8mr9qhcmb5qxmf")
LLM_MODEL = os.getenv("LLM_MODEL", "mimo-v2.5-pro")

AGENT_SYSTEM_PROMPTS = {
    "alpha-hunter": "You are Alpha Hunter, a DeFi trading agent. You help users find trading opportunities, analyze token prices, and execute swap strategies on Base L2. Be concise and data-driven.",
    "defi-sentinel": "You are DeFi Sentinel, a monitoring agent. You track DeFi protocol health, yield rates, and security alerts on Base L2. Provide real-time insights.",
    "research-bot": "You are Research Bot, an AI analyst agent. You research crypto projects, analyze tokenomics, and provide investment insights. Be thorough and objective.",
    "custom": "You are a custom AI agent on Zenith Hermes platform. Help the user with whatever they need. Be helpful and professional.",
}


@app.post("/api/playground/chat", response_model=PlaygroundResponse)
async def playground_chat(data: PlaygroundChat, db: AsyncSession = Depends(get_db)):
    session_id = data.session_id or uuid.uuid4().hex[:16]
    system_prompt = AGENT_SYSTEM_PROMPTS.get(data.agent_type, AGENT_SYSTEM_PROMPTS["custom"])

    user_msg = PlaygroundMessage(
        session_id=session_id,
        wallet_address=data.wallet_address,
        role="user",
        content=data.message,
        agent_type=data.agent_type,
    )
    db.add(user_msg)
    await db.commit()

    reply = ""
    if LLM_ENDPOINT and LLM_API_KEY:
        try:
            hist_result = await db.execute(
                select(PlaygroundMessage)
                .where(PlaygroundMessage.session_id == session_id)
                .order_by(PlaygroundMessage.created_at)
                .limit(20)
            )
            history = hist_result.scalars().all()
            messages = [{"role": "system", "content": system_prompt}]
            for m in history:
                messages.append({"role": m.role, "content": m.content})

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    LLM_ENDPOINT,
                    headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
                    json={"model": LLM_MODEL, "messages": messages, "max_tokens": 512},
                )
                resp.raise_for_status()
                reply = resp.json()["choices"][0]["message"]["content"]
        except Exception:
            reply = ""

    if not reply:
        reply = _generate_smart_reply(data.message, data.agent_type)

    assistant_msg = PlaygroundMessage(
        session_id=session_id,
        wallet_address=data.wallet_address,
        role="assistant",
        content=reply,
        agent_type=data.agent_type,
    )
    db.add(assistant_msg)
    await db.commit()

    return PlaygroundResponse(reply=reply, session_id=session_id, agent_type=data.agent_type)


def _generate_smart_reply(message: str, agent_type: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["price", "harga", "berapa"]):
        return "ETH is currently trading at ~$2,450 on Base. Gas fees are minimal (~0.001 gwei). For real-time prices, I recommend connecting to a price oracle skill like Chainlink Price Feed or Pyth Network."
    if any(w in msg for w in ["swap", "trade", "buy", "sell", "jual", "beli"]):
        return "To execute swaps on Base, I can route through Uniswap V3 or Aerodrome. Connect your wallet first, then specify the token pair and amount. Example: 'swap 0.1 ETH to USDC'."
    if any(w in msg for w in ["portfolio", "balance", "saldo", "wallet"]):
        return "Connect your wallet to view your portfolio. I can track your token balances, LP positions, and agent earnings across Base L2. All data is fetched on-chain in real-time."
    if any(w in msg for w in ["stake", "staking", "yield", "apy"]):
        return "Zenith Hermes staking is coming soon. You'll be able to stake $ZNH tokens to earn protocol fees. Estimated APY will depend on total staked amount and protocol revenue."
    if any(w in msg for w in ["agent", "deploy", "create", "buat"]):
        return "To deploy an agent: 1) Go to Agent Factory, 2) Choose a template (Trading Bot, DeFi Monitor, etc.), 3) Select skills from the registry, 4) Deploy to Base. Your agent will start operating autonomously."
    if any(w in msg for w in ["skill", "registry"]):
        return "There are 56 skills across 8 categories: DEFI, AI/LLM, DATA, SOCIAL, ORACLE, SECURITY, CHAIN, STORAGE. Each skill is composable — plug them into any agent. Browse the Skill Registry to explore."
    if any(w in msg for w in ["help", "tolong", "bantuan", "apa"]):
        return "I can help you with: trading analysis, portfolio tracking, DeFi monitoring, agent deployment, and skill recommendations. Try asking: 'What's the price of ETH?' or 'Help me deploy a trading agent'."
    return f"I'm your {agent_type.replace('-', ' ').title()} agent on Zenith. I can help with DeFi analysis, agent deployment, and skill management on Base L2. What would you like to do?"


@app.get("/api/playground/history")
async def playground_history(
    session_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlaygroundMessage)
        .where(PlaygroundMessage.session_id == session_id)
        .order_by(PlaygroundMessage.created_at)
    )
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages]


# ═══════════════════════════════════════════
# STATIC FILES (serve frontend)
# ═══════════════════════════════════════════
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    @app.get("/docs.html")
    async def serve_docs():
        return FileResponse(STATIC_DIR / "docs.html", media_type="text/html")

    @app.get("/whitepaper.html")
    async def serve_whitepaper():
        return FileResponse(STATIC_DIR / "whitepaper.html", media_type="text/html")

    @app.get("/")
    async def serve_index():
        return FileResponse(STATIC_DIR / "index.html", media_type="text/html")
