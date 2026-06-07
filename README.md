# Zenith Hermes

Autonomous AI agent platform on Base network. Deploy, manage, and orchestrate intelligent agents with 56+ modular skills.

## Architecture

```
zenith-hermes/
├── backend/           # FastAPI backend + SQLite
│   ├── main.py        # API server + LLM integration
│   ├── static/        # Frontend SPA (served same-origin)
│   └── pyproject.toml
├── contracts/         # Solidity smart contracts (Foundry)
│   ├── src/
│   │   ├── ZNHToken.sol       # $ZNH ERC-20 token (1B supply)
│   │   ├── AgentRegistry.sol  # On-chain agent registry
│   │   ├── SkillRegistry.sol  # On-chain skill verification
│   │   └── ZNHStaking.sol     # Stake $ZNH, earn rewards
│   ├── script/
│   │   └── Deploy.s.sol       # Deployment script
│   └── foundry.toml
├── index.html         # Landing page (static)
├── docs.html          # Documentation
└── whitepaper.html    # Whitepaper v0.1
```

## Quick Start

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy aiosqlite httpx
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` — frontend + API served from same origin.

### Smart Contracts

```bash
cd contracts
forge install OpenZeppelin/openzeppelin-contracts@v5.1.0 --no-git
forge build
```

Deploy to Base Sepolia:
```bash
export DEPLOYER_PRIVATE_KEY=0x...
forge script script/Deploy.s.sol --rpc-url https://sepolia.base.org --broadcast
```

## Features

- **56 Modular Skills** across 8 categories (DeFi, Analytics, Social, Security, Trading, Automation, Governance, Utility)
- **AI Playground** — Real-time chat powered by LLM
- **Agent Factory** — Deploy custom agents with selected skills
- **MetaMask Integration** — Base network wallet connection
- **Dark/Light Theme** — Toggle with persistent preference
- **On-Chain Registry** — Agents and skills tracked on Base Sepolia

## Token: $ZNH

- **Supply:** 1,000,000,000 ZNH
- **Community:** 40% | **Ecosystem:** 25% | **Team:** 15% | **Treasury:** 10% | **Liquidity:** 10%
- **Staking:** Lock tiers (Flex, 30d, 90d, 180d, 365d) with multiplied rewards

## Tech Stack

- **Frontend:** Single-file SPA (HTML/CSS/JS), Space Grotesk + Inter + JetBrains Mono
- **Backend:** Python, FastAPI, SQLAlchemy, aiosqlite
- **Contracts:** Solidity 0.8.20, Foundry, OpenZeppelin v5
- **Network:** Base (mainnet: 8453, testnet: Base Sepolia 84532)

## License

MIT
