# AI Ops Studio

> Enterprise-grade AI-powered workflow automation platform with multi-agent orchestration, Temporal workflows, and comprehensive observability.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)

## 🚀 Overview

AI Ops Studio is a production-ready SaaS platform that enables businesses to automate complex workflows using AI agents powered by Anthropic Claude. The platform orchestrates multi-step processes across sales, operations, analytics, and custom domains.

### Key Features

✨ **Multi-Agent System** - Supervisor, Sales, Operations, Analytics, and Custom agents
🔄 **Workflow Orchestration** - Temporal-based deterministic workflows with state management
🧠 **RAG Integration** - Context-aware retrieval with Pinecone vector database
📊 **Real-Time Monitoring** - OpenTelemetry, Prometheus, and Grafana integration
🔒 **Enterprise Security** - End-to-end encryption, RBAC, audit logging, SOC 2 compliance
💰 **Cost Optimization** - Smart model selection and token usage optimization
🏢 **Multi-Tenancy** - Database and application-level tenant isolation
⚡ **Production Ready** - Comprehensive error handling, retries, and circuit breakers
📈 **Auto-Scaling** - Kubernetes HPA with intelligent scaling policies
🔍 **Observability** - Distributed tracing, metrics, and structured logging

## 📚 Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Complete Implementation Guide](./docs/01-complete-implementation.md)** (40,000+ words)
  - Architecture overview
  - API specifications
  - Database schema
  - Security implementation
  - Go-to-market strategy

- **[Advanced Features](./docs/02-advanced-implementation.md)** (40,000+ words)
  - Infrastructure as Code (Terraform)
  - Multi-tenancy implementation
  - Custom agent builder
  - RAG implementation
  - Cost optimization

- **[Service Implementations](./docs/03-services-implementation.md)** (40,000+ words)
  - API Gateway (Express.js)
  - Orchestration Service (Temporal)
  - Agent Runtime (Python/FastAPI)
  - Integration handlers
  - Frontend components

- **[DevOps & Deployment](./docs/04-devops-deployment.md)** (40,000+ words)
  - Docker & Kubernetes
  - Testing strategies
  - Deployment runbooks
  - Monitoring & alerting
  - Troubleshooting guide

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│              Workflow Builder | Execution Monitor           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  API Gateway (Express.js)                    │
│         REST APIs | GraphQL | WebSocket | Auth              │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
│ Orchestrator │ │  Agent   │ │Integration │
│  (Temporal)  │ │ Runtime  │ │  Service   │
│              │ │(FastAPI) │ │            │
└──────┬───────┘ └────┬─────┘ └─────┬──────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────┐ ┌─────▼──────┐
│  PostgreSQL  │ │ Redis  │ │  Pinecone  │
│   (Primary)  │ │(Cache) │ │   (RAG)    │
└──────────────┘ └────────┘ └────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Languages**: TypeScript, Python 3.11
- **Frameworks**: Express.js, FastAPI
- **Orchestration**: Temporal.io
- **AI/ML**: Anthropic Claude, LangGraph, LangChain
- **Databases**: PostgreSQL 15, Redis 7, Pinecone

### Frontend
- **Framework**: React 18 with TypeScript
- **State Management**: React Query, Zustand
- **UI**: Tailwind CSS, shadcn/ui
- **Visualization**: ReactFlow, Recharts

### Infrastructure
- **Container**: Docker
- **Orchestration**: Kubernetes (GKE)
- **IaC**: Terraform
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, OpenTelemetry
- **Secrets**: HashiCorp Vault

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Garrettc123/ai-ops-studio.git
   cd ai-ops-studio
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   npm run migrate
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:3000/api
   - Temporal UI: http://localhost:8080
   - Grafana: http://localhost:3001

### Environment Variables

```env
# Application
NODE_ENV=development
API_VERSION=v1

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aiopsstudio

# Redis
REDIS_URL=redis://localhost:6379

# AI/ML
ANTHROPIC_API_KEY=your_anthropic_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-west1-gcp

# Authentication
JWT_SECRET=your_jwt_secret_key
REFRESH_TOKEN_SECRET=your_refresh_token_secret

# Temporal
TEMPORAL_ADDRESS=localhost:7233

# Monitoring
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## 📦 Project Structure

```
ai-ops-studio/
├── docs/                          # Comprehensive documentation
│   ├── 01-complete-implementation.md
│   ├── 02-advanced-implementation.md
│   ├── 03-services-implementation.md
│   └── 04-devops-deployment.md
├── services/                      # Microservices
│   ├── api-gateway/              # Express.js API Gateway
│   ├── orchestrator/             # Temporal workflow orchestrator
│   ├── agent-runtime/            # Python agent execution runtime
│   ├── integration-service/      # External integrations
│   └── notification-service/     # Notification handler
├── frontend/                      # React web application
│   └── web-app/
├── infrastructure/                # Infrastructure as Code
│   ├── terraform/                # Terraform configurations
│   ├── kubernetes/               # K8s manifests
│   └── scripts/                  # Deployment scripts
├── tests/                         # Test suites
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── load/
├── .github/                       # GitHub Actions workflows
│   └── workflows/
├── docker-compose.yml             # Local development setup
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
npm run test

# Unit tests
npm run test:unit

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Load tests
npm run test:load

# Coverage report
npm run test:coverage
```

## 🚢 Deployment

### Staging
```bash
./infrastructure/scripts/deploy.sh staging v1.0.0
```

### Production
```bash
./infrastructure/scripts/deploy.sh production v1.0.0
```

See [Deployment Guide](./docs/04-devops-deployment.md) for detailed instructions.

## 📊 Monitoring & Observability

- **Metrics**: Prometheus scrapes metrics from all services
- **Traces**: OpenTelemetry distributed tracing
- **Logs**: Structured logging with correlation IDs
- **Dashboards**: Pre-configured Grafana dashboards
- **Alerts**: Prometheus AlertManager with Slack integration

## 🔒 Security

- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: AES-256-GCM for data at rest, TLS 1.3 in transit
- **Secrets Management**: HashiCorp Vault integration
- **Audit Logging**: Comprehensive audit trail
- **Compliance**: SOC 2, GDPR, HIPAA ready

## 💰 Pricing Tiers

| Tier | Price | Workflows | Executions | Users | Support |
|------|-------|-----------|------------|-------|----------|
| **Starter** | $49/mo | 10 | 1,000/mo | 3 | Email |
| **Professional** | $199/mo | 50 | 10,000/mo | 10 | Priority |
| **Business** | $499/mo | Unlimited | 50,000/mo | 25 | Dedicated |
| **Enterprise** | Custom | Unlimited | Unlimited | Unlimited | White-glove |

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude API
- **Temporal.io** for workflow orchestration
- **LangChain** for agent framework
- **The Open Source Community** for amazing tools

## 📞 Support

- **Documentation**: [Full docs](./docs/)
- **Issues**: [GitHub Issues](https://github.com/Garrettc123/ai-ops-studio/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Garrettc123/ai-ops-studio/discussions)
- **Email**: support@aiopsstudio.com

## 🗺️ Roadmap

### Q1 2026
- [ ] Enhanced custom agent builder with visual programming
- [ ] Multi-modal agent support (vision, audio)
- [ ] Advanced workflow templates marketplace
- [ ] Mobile app (iOS/Android)

### Q2 2026
- [ ] Fine-tuning custom models
- [ ] Advanced analytics & BI dashboards
- [ ] Workflow versioning & rollback
- [ ] Multi-cloud support (AWS, Azure)

### Q3 2026
- [ ] Agent collaboration framework
- [ ] Real-time collaborative editing
- [ ] Advanced cost allocation
- [ ] White-label solution

---

**Built with ❤️ by the AI Ops Studio Team**

*Empowering businesses to automate intelligently.*