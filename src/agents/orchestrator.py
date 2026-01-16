"""Agent Orchestrator using LangGraph."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
from .base_agent import BaseAgent, AgentMessage, AgentStatus


@dataclass
class WorkflowNode:
    """Node in agent workflow graph."""
    node_id: str
    agent_type: str
    task_config: Dict[str, Any]
    dependencies: List[str]
    timeout: int = 300  # seconds


class AgentOrchestrator:
    """Orchestrates multi-agent workflows using graph-based execution."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, List[WorkflowNode]] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register agent with orchestrator.
        
        Args:
            agent: Agent to register
        """
        self.agents[agent.agent_id] = agent
    
    def create_workflow(
        self,
        workflow_id: str,
        nodes: List[WorkflowNode]
    ) -> None:
        """Create workflow graph.
        
        Args:
            workflow_id: Unique workflow identifier
            nodes: List of workflow nodes
        """
        self.workflows[workflow_id] = nodes
    
    async def execute_workflow(
        self,
        workflow_id: str,
        initial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute workflow with dependency resolution.
        
        Args:
            workflow_id: Workflow to execute
            initial_data: Initial workflow data
            
        Returns:
            Workflow execution results
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        nodes = self.workflows[workflow_id]
        results = {}
        completed = set()
        
        # Build dependency graph
        while len(completed) < len(nodes):
            for node in nodes:
                if node.node_id in completed:
                    continue
                
                # Check if dependencies are satisfied
                if all(dep in completed for dep in node.dependencies):
                    # Execute node
                    agent = self._find_agent_for_node(node)
                    if agent:
                        try:
                            task_data = node.task_config.copy()
                            task_data["initial_data"] = initial_data
                            task_data["dependency_results"] = {
                                dep: results.get(dep) for dep in node.dependencies
                            }
                            
                            result = await asyncio.wait_for(
                                agent.execute(task_data),
                                timeout=node.timeout
                            )
                            
                            results[node.node_id] = result
                            completed.add(node.node_id)
                            
                            self.execution_history.append({
                                "workflow_id": workflow_id,
                                "node_id": node.node_id,
                                "agent_id": agent.agent_id,
                                "status": "success"
                            })
                        except asyncio.TimeoutError:
                            results[node.node_id] = {"error": "timeout"}
                            completed.add(node.node_id)
                        except Exception as e:
                            results[node.node_id] = {"error": str(e)}
                            completed.add(node.node_id)
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy loop
        
        return results
    
    def _find_agent_for_node(self, node: WorkflowNode) -> Optional[BaseAgent]:
        """Find suitable agent for workflow node.
        
        Args:
            node: Workflow node
            
        Returns:
            Agent capable of handling node task
        """
        for agent in self.agents.values():
            if agent.can_handle(node.agent_type):
                if agent.state.status == AgentStatus.IDLE:
                    return agent
        return None
    
    async def route_message(
        self,
        message: AgentMessage
    ) -> None:
        """Route message to appropriate agent.
        
        Args:
            message: Message to route
        """
        if message.recipient_id in self.agents:
            agent = self.agents[message.recipient_id]
            await agent.receive_message(message)
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow status information
        """
        history = [h for h in self.execution_history if h["workflow_id"] == workflow_id]
        return {
            "workflow_id": workflow_id,
            "total_nodes": len(self.workflows.get(workflow_id, [])),
            "completed_nodes": len(history),
            "history": history
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status.
        
        Returns:
            System status information
        """
        agent_statuses = [agent.get_status() for agent in self.agents.values()]
        
        return {
            "total_agents": len(self.agents),
            "active_workflows": len(self.workflows),
            "agents": agent_statuses,
            "total_executions": len(self.execution_history)
        }
