"""Tests for agent framework."""

import pytest
import asyncio
from src.agents.base_agent import BaseAgent, AgentMessage, AgentStatus
from src.agents.specialized.data_agent import DataAgent
from src.agents.specialized.api_agent import APIAgent
from src.agents.orchestrator import AgentOrchestrator, WorkflowNode


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    async def execute(self, task):
        await asyncio.sleep(0.1)
        return {"status": "completed", "result": "mock_result"}


@pytest.mark.asyncio
async def test_agent_creation():
    """Test creating an agent."""
    agent = MockAgent(
        agent_id="test-agent-1",
        name="Test Agent",
        capabilities=["test"]
    )
    
    assert agent.agent_id == "test-agent-1"
    assert agent.name == "Test Agent"
    assert agent.state.status == AgentStatus.IDLE


@pytest.mark.asyncio
async def test_agent_message_passing():
    """Test message passing between agents."""
    agent1 = MockAgent("agent-1", "Agent 1", ["test"])
    agent2 = MockAgent("agent-2", "Agent 2", ["test"])
    
    message = await agent1.send_message(
        recipient_id="agent-2",
        content={"task": "process_data"},
        message_type="task"
    )
    
    await agent2.receive_message(message)
    
    assert len(agent2.message_queue) == 1
    assert message.sender_id == "agent-1"
    assert message.recipient_id == "agent-2"


@pytest.mark.asyncio
async def test_data_agent():
    """Test data processing agent."""
    agent = DataAgent("data-agent-1")
    
    result = await agent.execute({
        "operation": "filter",
        "data": [1, 2, 3, 4, 5],
        "filter_config": {}
    })
    
    assert result["status"] == "success"
    assert result["operation"] == "filter"


@pytest.mark.asyncio
async def test_api_agent():
    """Test API integration agent."""
    agent = APIAgent("api-agent-1")
    
    result = await agent.execute({
        "action": "api_call",
        "endpoint": "https://api.example.com/data",
        "method": "GET"
    })
    
    assert result["success"] is True
    assert result["action"] == "api_call"


@pytest.mark.asyncio
async def test_orchestrator():
    """Test agent orchestrator."""
    orchestrator = AgentOrchestrator()
    
    agent1 = MockAgent("mock-1", "Mock 1", ["task_a"])
    agent2 = MockAgent("mock-2", "Mock 2", ["task_b"])
    
    orchestrator.register_agent(agent1)
    orchestrator.register_agent(agent2)
    
    status = orchestrator.get_system_status()
    assert status["total_agents"] == 2


@pytest.mark.asyncio
async def test_workflow_execution():
    """Test workflow execution with dependencies."""
    orchestrator = AgentOrchestrator()
    
    agent = MockAgent("workflow-agent", "Workflow Agent", ["step_a", "step_b"])
    orchestrator.register_agent(agent)
    
    nodes = [
        WorkflowNode(
            node_id="step-1",
            agent_type="step_a",
            task_config={"task": "first"},
            dependencies=[]
        ),
        WorkflowNode(
            node_id="step-2",
            agent_type="step_b",
            task_config={"task": "second"},
            dependencies=["step-1"]
        )
    ]
    
    orchestrator.create_workflow("test-workflow", nodes)
    results = await orchestrator.execute_workflow("test-workflow", {})
    
    assert "step-1" in results
    assert "step-2" in results
