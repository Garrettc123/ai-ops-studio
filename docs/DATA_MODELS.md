# AI Ops Studio: Data Models & Database Schemas

## Overview

This document describes the complete data model for AI Ops Studio, including database schemas, relationships, and design considerations.

## Core Entities

### 1. Organization & User Management

#### Organization
Represents a customer account or workspace.

```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  subscription_tier ENUM('starter', 'professional', 'business', 'enterprise') DEFAULT 'starter',
  status ENUM('active', 'suspended', 'cancelled') DEFAULT 'active',
  
  -- Billing Information
  billing_email VARCHAR(255),
  billing_address JSONB,
  payment_method_id VARCHAR(255),
  
  -- Usage Tracking
  monthly_execution_quota INT DEFAULT 500,
  monthly_executions_used INT DEFAULT 0,
  monthly_reset_date DATE,
  
  -- Configuration
  settings JSONB DEFAULT '{}',
  api_keys JSONB DEFAULT '{}',
  integrations JSONB DEFAULT '{}',
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT subscription_tier_check CHECK (subscription_tier IN ('starter', 'professional', 'business', 'enterprise'))
);

CREATE INDEX idx_organizations_status ON organizations(status);
CREATE INDEX idx_organizations_tier ON organizations(subscription_tier);
```

#### User
Represents individual users within an organization.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  email_verified_at TIMESTAMP,
  
  -- Authentication
  password_hash VARCHAR(255),
  auth_provider ENUM('email', 'google', 'microsoft', 'github') DEFAULT 'email',
  auth_provider_id VARCHAR(255),
  
  -- Profile
  full_name VARCHAR(255),
  avatar_url VARCHAR(255),
  
  -- Permissions
  role ENUM('owner', 'admin', 'member', 'viewer') DEFAULT 'member',
  permissions JSONB DEFAULT '[]',
  
  -- Security
  mfa_enabled BOOLEAN DEFAULT FALSE,
  mfa_secret VARCHAR(255),
  last_login TIMESTAMP,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  UNIQUE(organization_id, email)
);

CREATE INDEX idx_users_organization ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

### 2. Workflow Management

#### Workflow
Defines automated workflows composed of agents and connections.

```sql
CREATE TABLE workflows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Version Control
  version INT DEFAULT 1,
  status ENUM('draft', 'active', 'paused', 'archived') DEFAULT 'draft',
  
  -- Workflow Definition
  definition JSONB NOT NULL,  -- Contains agents, connections, variables, triggers
  
  -- Configuration
  execution_timeout INT DEFAULT 3600,  -- seconds
  max_retries INT DEFAULT 3,
  error_handling JSONB DEFAULT '{}',
  
  -- Analytics
  total_executions INT DEFAULT 0,
  successful_executions INT DEFAULT 0,
  failed_executions INT DEFAULT 0,
  average_duration FLOAT,
  average_cost DECIMAL(10, 4),
  
  -- Metadata
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_by UUID REFERENCES users(id),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  UNIQUE(organization_id, name, deleted_at)
);

CREATE INDEX idx_workflows_org ON workflows(organization_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created ON workflows(created_at DESC);
```

#### Agent
Configuration for individual agents within a workflow.

```sql
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  type ENUM('coordinator', 'specialist', 'analyzer', 'custom') DEFAULT 'specialist',
  name VARCHAR(255) NOT NULL,
  
  -- Configuration
  configuration JSONB NOT NULL,  -- model_settings, prompt_template, tools, memory_config
  position JSONB NOT NULL,  -- {x: int, y: int} for UI positioning
  
  -- Model Settings
  model_name VARCHAR(255) DEFAULT 'gpt-4',
  temperature DECIMAL(3, 2) DEFAULT 0.7,
  max_tokens INT DEFAULT 2048,
  
  -- Tool Access
  tools JSONB DEFAULT '[]',  -- Array of tool names
  tool_configs JSONB DEFAULT '{}',  -- Tool-specific configurations
  
  -- Metadata
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(workflow_id, name)
);

CREATE INDEX idx_agents_workflow ON agents(workflow_id);
CREATE INDEX idx_agents_type ON agents(type);
```

#### Workflow Execution
Records individual workflow executions.

```sql
CREATE TABLE workflow_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  workflow_version INT NOT NULL,
  
  -- Execution Status
  status ENUM('pending', 'running', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
  status_reason TEXT,
  
  -- Execution Details
  triggered_by ENUM('manual', 'schedule', 'webhook', 'api', 'internal') DEFAULT 'manual',
  triggered_by_user_id UUID REFERENCES users(id),
  external_trigger_id VARCHAR(255),
  
  -- Input/Output
  input_data JSONB DEFAULT '{}',
  output_data JSONB DEFAULT '{}',
  
  -- Timing
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  duration_ms INT,
  
  -- Costs & Limits
  total_tokens_used INT DEFAULT 0,
  estimated_cost DECIMAL(10, 4) DEFAULT 0,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB DEFAULT '{}',
  
  CONSTRAINT status_check CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX idx_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_executions_status ON workflow_executions(status);
CREATE INDEX idx_executions_org ON workflow_executions(organization_id);
CREATE INDEX idx_executions_created ON workflow_executions(created_at DESC);
```

#### Agent Execution
Records individual agent executions within a workflow run.

```sql
CREATE TABLE agent_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
  agent_id UUID NOT NULL REFERENCES agents(id),
  
  -- Execution Status
  status ENUM('queued', 'running', 'completed', 'failed', 'skipped') DEFAULT 'queued',
  status_reason TEXT,
  
  -- Input/Output
  input JSONB NOT NULL,
  output JSONB,
  
  -- Timing
  queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  duration_ms INT,
  
  -- Token Usage & Cost
  input_tokens INT DEFAULT 0,
  output_tokens INT DEFAULT 0,
  total_tokens INT DEFAULT 0,
  estimated_cost DECIMAL(10, 4) DEFAULT 0,
  
  -- Tracing & Debugging
  trace_data JSONB DEFAULT '{}',
  error_details JSONB,
  
  -- Metadata
  retry_count INT DEFAULT 0,
  parent_agent_execution_id UUID REFERENCES agent_executions(id),
  
  CONSTRAINT status_check CHECK (status IN ('queued', 'running', 'completed', 'failed', 'skipped'))
);

CREATE INDEX idx_agent_executions_workflow_exec ON agent_executions(workflow_execution_id);
CREATE INDEX idx_agent_executions_agent ON agent_executions(agent_id);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
```

### 3. Monitoring & Observability

#### Execution Log
Detailed logs for debugging and auditing.

```sql
CREATE TABLE execution_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_execution_id UUID NOT NULL REFERENCES agent_executions(id) ON DELETE CASCADE,
  workflow_execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
  
  -- Log Content
  level ENUM('debug', 'info', 'warning', 'error', 'critical') DEFAULT 'info',
  message TEXT NOT NULL,
  context JSONB DEFAULT '{}',
  
  -- Tracing
  trace_id VARCHAR(255),
  span_id VARCHAR(255),
  parent_span_id VARCHAR(255),
  
  -- Metadata
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  source VARCHAR(255),
  
  CONSTRAINT level_check CHECK (level IN ('debug', 'info', 'warning', 'error', 'critical'))
);

CREATE INDEX idx_logs_agent_exec ON execution_logs(agent_execution_id);
CREATE INDEX idx_logs_workflow_exec ON execution_logs(workflow_execution_id);
CREATE INDEX idx_logs_level ON execution_logs(level);
CREATE INDEX idx_logs_timestamp ON execution_logs(timestamp DESC);
CREATE INDEX idx_logs_trace ON execution_logs(trace_id);
```

#### Agent Metrics
Time-series metrics for agent performance.

```sql
CREATE TABLE agent_metrics (
  id BIGSERIAL PRIMARY KEY,
  agent_execution_id UUID REFERENCES agent_executions(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id),
  organization_id UUID REFERENCES organizations(id),
  
  -- Metric Details
  metric_type VARCHAR(255) NOT NULL,  -- 'latency', 'tokens', 'quality_score', 'error_rate'
  value FLOAT NOT NULL,
  unit VARCHAR(50),
  
  -- Dimensions for aggregation
  dimensions JSONB DEFAULT '{}',  -- agent_type, model_name, tool_used, etc.
  
  -- Timestamp
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT metric_value_check CHECK (value >= 0)
);

CREATE INDEX idx_metrics_agent_exec ON agent_metrics(agent_execution_id);
CREATE INDEX idx_metrics_agent ON agent_metrics(agent_id);
CREATE INDEX idx_metrics_org ON agent_metrics(organization_id);
CREATE INDEX idx_metrics_type ON agent_metrics(metric_type);
CREATE INDEX idx_metrics_timestamp ON agent_metrics(timestamp DESC);
```

#### Evaluation Results
Quality evaluation scores for agent outputs.

```sql
CREATE TABLE evaluation_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_execution_id UUID NOT NULL REFERENCES agent_executions(id) ON DELETE CASCADE,
  workflow_execution_id UUID REFERENCES workflow_executions(id),
  
  -- Evaluation Details
  evaluator_name VARCHAR(255) NOT NULL,  -- 'relevancy', 'helpfulness', 'clarity', etc.
  score DECIMAL(5, 2) NOT NULL,  -- 0-100
  passed BOOLEAN,  -- Threshold comparison
  
  -- Details & Explanation
  details JSONB DEFAULT '{}',  -- Evaluation-specific details
  explanation TEXT,
  
  -- Metadata
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT score_range CHECK (score >= 0 AND score <= 100)
);

CREATE INDEX idx_evaluations_agent_exec ON evaluation_results(agent_execution_id);
CREATE INDEX idx_evaluations_workflow_exec ON evaluation_results(workflow_execution_id);
CREATE INDEX idx_evaluations_evaluator ON evaluation_results(evaluator_name);
```

### 4. Integration & Triggers

#### Workflow Trigger
Defines how workflows are triggered.

```sql
CREATE TABLE workflow_triggers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  
  -- Trigger Type
  trigger_type ENUM('schedule', 'webhook', 'event', 'manual') DEFAULT 'manual',
  
  -- Schedule Trigger
  schedule_cron VARCHAR(255),  -- Cron expression
  
  -- Webhook Trigger
  webhook_url VARCHAR(255),
  webhook_secret VARCHAR(255),
  
  -- Event Trigger
  event_type VARCHAR(255),
  event_source VARCHAR(255),
  event_filter JSONB DEFAULT '{}',
  
  -- Configuration
  enabled BOOLEAN DEFAULT TRUE,
  max_concurrent_executions INT DEFAULT 1,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(workflow_id, trigger_type)
);

CREATE INDEX idx_triggers_workflow ON workflow_triggers(workflow_id);
CREATE INDEX idx_triggers_type ON workflow_triggers(trigger_type);
CREATE INDEX idx_triggers_enabled ON workflow_triggers(enabled);
```

#### Integration
Manages external integrations and API connections.

```sql
CREATE TABLE integrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  
  -- Integration Details
  integration_type VARCHAR(255) NOT NULL,  -- 'slack', 'salesforce', 'hubspot', etc.
  name VARCHAR(255),
  status ENUM('connected', 'disconnected', 'error') DEFAULT 'connected',
  
  -- Credentials (encrypted)
  credentials JSONB NOT NULL,  -- Encrypted via application layer
  
  -- Configuration
  config JSONB DEFAULT '{}',
  
  -- Metadata
  connected_at TIMESTAMP,
  last_used_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(organization_id, integration_type)
);

CREATE INDEX idx_integrations_org ON integrations(organization_id);
CREATE INDEX idx_integrations_type ON integrations(integration_type);
CREATE INDEX idx_integrations_status ON integrations(status);
```

### 5. Billing & Usage

#### Usage Record
Tracks usage for billing purposes.

```sql
CREATE TABLE usage_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  
  -- Usage Details
  usage_type VARCHAR(255) NOT NULL,  -- 'workflow_execution', 'api_call', 'tokens', etc.
  quantity INT NOT NULL,
  unit_price DECIMAL(10, 6),
  total_cost DECIMAL(10, 4),
  
  -- Period
  period_start DATE,
  period_end DATE,
  
  -- Metadata
  resource_id UUID,  -- workflow_execution_id, agent_execution_id, etc.
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT quantity_check CHECK (quantity >= 0),
  CONSTRAINT cost_check CHECK (total_cost >= 0)
);

CREATE INDEX idx_usage_org ON usage_records(organization_id);
CREATE INDEX idx_usage_type ON usage_records(usage_type);
CREATE INDEX idx_usage_period ON usage_records(period_start, period_end);
```

#### Invoice
Generated invoices for billing.

```sql
CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  
  -- Invoice Details
  invoice_number VARCHAR(255) NOT NULL UNIQUE,
  status ENUM('draft', 'sent', 'paid', 'overdue', 'cancelled') DEFAULT 'draft',
  
  -- Amounts
  subtotal DECIMAL(10, 2),
  tax DECIMAL(10, 2),
  total DECIMAL(10, 2),
  
  -- Dates
  issue_date DATE,
  due_date DATE,
  paid_date DATE,
  
  -- Items
  line_items JSONB NOT NULL,  -- Array of usage and charges
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoices_org ON invoices(organization_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
```

## Relationships & Constraints

### Entity Relationship Diagram

```
Organizations (1) ---> (N) Users
Organizations (1) ---> (N) Workflows
Organizations (1) ---> (N) Integrations
Organizations (1) ---> (N) Usage Records
Organizations (1) ---> (N) Invoices

Workflows (1) ---> (N) Agents
Workflows (1) ---> (N) Workflow Executions
Workflows (1) ---> (N) Workflow Triggers

Workflow Executions (1) ---> (N) Agent Executions
Workflow Executions (1) ---> (N) Evaluation Results
Workflow Executions (1) ---> (N) Execution Logs

Agents (1) ---> (N) Agent Executions

Agent Executions (1) ---> (N) Execution Logs
Agent Executions (1) ---> (N) Agent Metrics
Agent Executions (1) ---> (N) Evaluation Results
```

## Indexing Strategy

### Write-Heavy Tables
- `execution_logs`: Timestamp index for time-range queries
- `agent_metrics`: Timestamp + agent_id for real-time dashboards
- `workflow_executions`: Status + organization_id for filtering

### Read-Heavy Tables
- `users`: Email unique index for fast lookups
- `workflows`: Organization + name for uniqueness and filtering
- `agents`: Workflow + name for uniqueness

### Composite Indexes
- `workflow_executions(organization_id, created_at DESC)` for paginated lists
- `agent_executions(workflow_execution_id, status)` for status filtering
- `evaluation_results(agent_execution_id, evaluator_name)` for evaluation lookups

## Performance Considerations

### Partitioning Strategy

**Time-series tables** (1-year retention):
- `execution_logs`: Partition by month
- `agent_metrics`: Partition by month
- `evaluation_results`: Partition by month

```sql
-- Example partition
CREATE TABLE execution_logs_2025_01 PARTITION OF execution_logs
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### Archival Strategy
- Workflow executions older than 1 year moved to cold storage
- Logs older than 90 days compressed and archived
- Metrics aggregated into summary tables for historical analysis

## JSONB Field Specifications

### Workflow Definition
```json
{
  "agents": [
    {
      "id": "uuid",
      "name": "string",
      "type": "specialist|coordinator",
      "config": { ... }
    }
  ],
  "connections": [
    {
      "from_agent_id": "uuid",
      "to_agent_id": "uuid",
      "condition": "optional string"
    }
  ],
  "variables": {
    "var_name": "type"
  },
  "triggers": [...]
}
```

### Agent Configuration
```json
{
  "model_settings": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048
  },
  "prompt_template": "string",
  "tools": ["gmail", "slack"],
  "memory_config": {
    "type": "short_term|long_term",
    "max_messages": 10
  }
}
```

## Audit & Compliance

### Audit Logging
- All user actions logged in `audit_logs` table
- Changes to workflow definitions tracked
- Execution history retained for compliance
- PII data masked in logs

### Data Retention Policies
- Active user data: Indefinite (until deletion request)
- Workflow execution history: 1 year
- Logs: 90 days (7 days in hot storage, 83 in cold)
- Metrics: 2 years (aggregated)
- Audit logs: 3 years for compliance

---

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design context.
