<p align="center">
  <img src="https://img.shields.io/badge/Base-Sepolia-0052FF?style=for-the-badge&logo=ethereum&logoColor=white" />
  <img src="https://img.shields.io/badge/Solidity-0.8.20-363636?style=for-the-badge&logo=solidity&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<h1 align="center">Zenith Hermes</h1>

<p align="center">
  <strong>Autonomous AI Agent Infrastructure on Base Network</strong>
</p>

<p align="center">
  Build, deploy, and orchestrate intelligent agents with 56+ composable skill modules.
  <br />
  The missing runtime layer between LLMs and on-chain execution.
</p>

<p align="center">
  <a href="https://zenith-hermes.com">Website</a> •
  <a href="https://twitter.com/zenith_hermes">Twitter</a> •
  <a href="#documentation">Docs</a> •
  <a href="#smart-contracts">Contracts</a>
</p>

---

## Overview

Zenith Hermes is a modular infrastructure protocol for autonomous AI agents on Base. It provides the execution layer that connects LLM intelligence to on-chain actions through composable skill modules.

**The Problem:** AI models can analyze markets, identify opportunities, and generate strategies — but they have no native way to execute on-chain. Every team rebuilds the same infrastructure: RPC connections, protocol integrations, gas management, error recovery.

**The Solution:** A shared, composable runtime. Pick skills, configure parameters, deploy an agent. The protocol handles execution, state, and chain interactions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ZENITH HERMES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────────┐    ┌────────────────────┐   │
│  │  Agent   │───▶│   Runtime    │───▶│   Base Network     │   │
│  │  Config  │    │  (56 Skills) │    │   (Execution)      │   │
│  └──────────┘    └──────────────┘    └────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              On-Chain Registries                          │  │
│  │  Agent Registry • Skill Registry • Staking • $ZNH Token │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Smart Contracts

Deployed on **Base Sepolia** (Chain ID: 84532):

| Contract | Address | Description |
|----------|---------|-------------|
| **ZNH Token** | [`0x05372b6850FFA3aed775B643AB9537fB8d1bBD1D`](https://sepolia.basescan.org/address/0x05372b6850FFA3aed775B643AB9537fB8d1bBD1D) | ERC-20 governance token (1B supply) |
| **Agent Registry** | [`0xcF0609e151F2bD004Ac38644dC9343990467F09C`](https://sepolia.basescan.org/address/0xcF0609e151F2bD004Ac38644dC9343990467F09C) | On-chain agent identity & tracking |
| **Skill Registry** | [`0xEf2Cc3eAb6BAebB0035720e3f60628Ee943bA314`](https://sepolia.basescan.org/address/0xEf2Cc3eAb6BAebB0035720e3f60628Ee943bA314) | Verified composable skill modules |
| **ZNH Staking** | [`0xa960897e25C126D0fF44Ed06a2a26Fad3BEe85Dc`](https://sepolia.basescan.org/address/0xa960897e25C126D0fF44Ed06a2a26Fad3BEe85Dc) | Stake $ZNH, earn protocol fees |

### Contract Architecture

```solidity
// Composable skill-based agent deployment
AgentRegistry.registerAgent(name, model, skillIds[])
SkillRegistry.verifySkill(skillId, proof)
ZNHStaking.stake(amount, lockTier) // Flex | 30d | 90d | 180d | 365d
```

## Features

### Skill Modules (56 Skills, 8 Categories)

| Category | Skills | Examples |
|----------|--------|----------|
| **DeFi** | 8 | Uniswap V3 routing, Aave lending, Compound yield |
| **Analytics** | 7 | Price tracking, whale monitoring, volume analysis |
| **Trading** | 8 | Limit orders, DCA, arbitrage detection |
| **Social** | 6 | Sentiment analysis, Twitter monitoring, community alerts |
| **Security** | 7 | Contract auditing, rug detection, permission scanning |
| **Automation** | 7 | Cron scheduling, conditional triggers, auto-rebalance |
| **Governance** | 6 | Proposal tracking, vote delegation, quorum monitoring |
| **Utility** | 7 | Gas optimization, ENS resolution, multi-chain bridge |

### Platform Capabilities

- **AI Playground** — Real-time conversational interface powered by LLM
- **Agent Factory** — Visual agent builder with skill composition
- **On-Chain Registry** — Immutable agent/skill records on Base
- **Staking Protocol** — Lock $ZNH across 5 tiers for multiplied rewards
- **MetaMask Integration** — Native Base network wallet connection
- **Dark/Light Modes** — Persistent user preference

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (optional, for contract tooling)
- [Foundry](https://getfoundry.sh/) (for smart contract development)

### Backend + Frontend

```bash
git clone https://github.com/zenith-hermes/zenith-hermes.git
cd zenith-hermes/backend

python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy aiosqlite httpx

uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` — full platform served from single origin.

### Smart Contracts

```bash
cd contracts
forge install OpenZeppelin/openzeppelin-contracts@v5.1.0 --no-git
forge build
```

Deploy to Base Sepolia:
```bash
export DEPLOYER_PRIVATE_KEY=0x...
forge script script/Deploy.s.sol \
  --rpc-url https://sepolia.base.org \
  --broadcast \
  --verify
```

## Tokenomics — $ZNH

| Allocation | Percentage | Vesting |
|-----------|-----------|---------|
| Community & Rewards | 40% | Linear 24mo |
| Ecosystem Development | 25% | Linear 18mo |
| Team & Contributors | 15% | 6mo cliff + 24mo linear |
| Treasury | 10% | Governance-controlled |
| Liquidity Provision | 10% | Immediate |

**Total Supply:** 1,000,000,000 ZNH

### Staking Tiers

| Tier | Lock Period | Reward Multiplier |
|------|-----------|-------------------|
| Flex | None | 1.0x |
| Bronze | 30 days | 1.5x |
| Silver | 90 days | 2.0x |
| Gold | 180 days | 3.0x |
| Diamond | 365 days | 5.0x |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Single-file SPA, CSS Grid, Web3.js |
| Backend | Python, FastAPI, SQLAlchemy, aiosqlite |
| AI | LLM integration (pluggable provider) |
| Contracts | Solidity 0.8.20, Foundry, OpenZeppelin v5 |
| Network | Base (mainnet: 8453, testnet: Sepolia 84532) |
| Typography | Space Grotesk, Inter, JetBrains Mono |

## Project Structure

```
zenith-hermes/
├── backend/
│   ├── main.py              # FastAPI server + LLM + database
│   ├── static/
│   │   └── index.html       # Frontend SPA (all UI + logic)
│   └── pyproject.toml       # Python dependencies
├── contracts/
│   ├── src/
│   │   ├── ZNHToken.sol     # ERC-20 governance token
│   │   ├── AgentRegistry.sol
│   │   ├── SkillRegistry.sol
│   │   └── ZNHStaking.sol
│   ├── script/
│   │   └── Deploy.s.sol     # Foundry deployment script
│   ├── foundry.toml
│   └── remappings.txt
├── index.html               # Static landing page
├── docs.html                # Documentation
└── whitepaper.html          # Protocol whitepaper v0.1
```

## Documentation

- **[Live Platform](https://zenith-hermes.com)** — Full application
- **[Documentation](https://zenith-hermes.com/docs.html)** — API reference & guides
- **[Whitepaper](https://zenith-hermes.com/whitepaper.html)** — Protocol specification v0.1

## Roadmap

- [x] Core platform (Frontend + Backend + AI)
- [x] Smart contract deployment (Base Sepolia)
- [x] 56 skill modules across 8 categories
- [x] Staking protocol with tiered rewards
- [ ] Mainnet deployment (Base)
- [ ] Skill marketplace with creator incentives
- [ ] Cross-chain agent execution
- [ ] Governance module (proposal + voting)
- [ ] SDK for third-party skill development

## Contributing

Contributions welcome. Please read the [documentation](https://zenith-hermes.com/docs.html) before submitting PRs.

```bash
# Fork & clone
git clone https://github.com/YOUR_USERNAME/zenith-hermes.git

# Create feature branch
git checkout -b feature/your-feature

# Make changes & test
uvicorn main:app --reload

# Submit PR
```

## Security

If you discover a vulnerability, please report it privately via [Twitter DM](https://twitter.com/zenith_hermes) or open a confidential issue. Do not disclose publicly until patched.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built on Base. Powered by composable intelligence.</strong>
  <br /><br />
  <a href="https://twitter.com/zenith_hermes">Twitter</a> •
  <a href="https://zenith-hermes.com">Website</a> •
  <a href="https://github.com/zenith-hermes/zenith-hermes">GitHub</a>
</p>
