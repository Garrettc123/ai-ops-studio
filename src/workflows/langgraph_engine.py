"""LangGraph State Management and Workflow Engine."""

from typing import Dict, Any, List, TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator
from datetime import datetime


class AgentState(TypedDict):
    """Typed state for LangGraph workflows."""
    messages: Annotated[Sequence[Dict[str, Any]], operator.add]
    current_agent: str
    workflow_id: str
    data: Dict[str, Any]
    results: Dict[str, Any]
    error: str | None
    status: str


class LangGraphWorkflowEngine:
    """LangGraph-based workflow execution engine."""
    
    def __init__(self):
        self.memory = MemorySaver()
        self.workflows: Dict[str, StateGraph] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def create_sequential_workflow(
        self,
        workflow_id: str,
        agents: List[str]
    ) -> StateGraph:
        """Create sequential agent workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            agents: List of agent names in execution order
            
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        for agent_name in agents:
            workflow.add_node(
                agent_name,
                self._create_agent_node(agent_name)
            )
        
        # Set entry point
        workflow.set_entry_point(agents[0])
        
        # Connect agents sequentially
        for i in range(len(agents) - 1):
            workflow.add_edge(agents[i], agents[i + 1])
        
        # Connect last agent to END
        workflow.add_edge(agents[-1], END)
        
        # Compile with checkpointing
        compiled = workflow.compile(checkpointer=self.memory)
        self.workflows[workflow_id] = compiled
        
        return compiled
    
    def create_conditional_workflow(
        self,
        workflow_id: str,
        nodes: Dict[str, callable],
        router: callable
    ) -> StateGraph:
        """Create workflow with conditional routing.
        
        Args:
            workflow_id: Unique workflow identifier
            nodes: Dictionary of node names to functions
            router: Function that determines next node
            
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(AgentState)
        
        # Add all nodes
        for node_name, node_func in nodes.items():
            workflow.add_node(node_name, node_func)
        
        # Set entry point (first node)
        first_node = list(nodes.keys())[0]
        workflow.set_entry_point(first_node)
        
        # Add conditional routing
        workflow.add_conditional_edges(
            first_node,
            router,
            {name: name for name in nodes.keys()}
        )
        
        # Compile
        compiled = workflow.compile(checkpointer=self.memory)
        self.workflows[workflow_id] = compiled
        
        return compiled
    
    def _create_agent_node(self, agent_name: str) -> callable:
        """Create node function for agent.
        
        Args:
            agent_name: Name of agent
            
        Returns:
            Node function
        """
        def agent_node(state: AgentState) -> AgentState:
            """Execute agent task."""
            # Update current agent
            state["current_agent"] = agent_name
            
            # Add message
            state["messages"].append({
                "agent": agent_name,
                "timestamp": datetime.utcnow().isoformat(),
                "action": "processing"
            })
            
            # Process based on agent type
            if agent_name == "analyzer":
                state["results"]["analysis"] = "Data analyzed"
            elif agent_name == "validator":
                state["results"]["validation"] = "Data validated"
            elif agent_name == "executor":
                state["results"]["execution"] = "Task executed"
            
            state["status"] = "in_progress"
            return state
        
        return agent_node
    
    async def execute_workflow(
        self,
        workflow_id: str,
        initial_state: Dict[str, Any],
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute workflow with state management.
        
        Args:
            workflow_id: Workflow to execute
            initial_state: Initial workflow state
            config: Execution configuration
            
        Returns:
            Final workflow state
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        # Prepare state
        state = AgentState(
            messages=[],
            current_agent="",
            workflow_id=workflow_id,
            data=initial_state.get("data", {}),
            results={},
            error=None,
            status="started"
        )
        
        # Execute workflow
        config = config or {"configurable": {"thread_id": workflow_id}}
        
        try:
            final_state = await workflow.ainvoke(state, config)
            final_state["status"] = "completed"
            
            self.execution_history.append({
                "workflow_id": workflow_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "results": final_state["results"]
            })
            
            return final_state
        except Exception as e:
            error_state = {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.execution_history.append(error_state)
            return error_state
    
    def get_workflow_state(
        self,
        workflow_id: str,
        checkpoint_id: str = None
    ) -> Dict[str, Any]:
        """Retrieve workflow state from checkpoint.
        
        Args:
            workflow_id: Workflow identifier
            checkpoint_id: Optional checkpoint ID
            
        Returns:
            Workflow state
        """
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        # Get state from memory
        config = {"configurable": {"thread_id": workflow_id}}
        
        try:
            state = self.memory.get(config)
            return state if state else {"status": "not_started"}
        except Exception as e:
            return {"error": str(e)}
    
    def list_workflows(self) -> List[str]:
        """List all registered workflows.
        
        Returns:
            List of workflow IDs
        """
        return list(self.workflows.keys())
