"""LangGraph Integration Demo."""

import asyncio
from src.workflows.langgraph_engine import LangGraphWorkflowEngine, AgentState


async def demo_sequential_workflow():
    """Demonstrate sequential agent workflow."""
    engine = LangGraphWorkflowEngine()
    
    # Create workflow with 3 agents
    workflow = engine.create_sequential_workflow(
        workflow_id="demo-sequential",
        agents=["analyzer", "validator", "executor"]
    )
    
    print("Executing Sequential Workflow...")
    print("="*60)
    
    # Execute workflow
    initial_state = {
        "data": {
            "input": "Sample data for processing",
            "priority": "high"
        }
    }
    
    result = await engine.execute_workflow(
        "demo-sequential",
        initial_state
    )
    
    print(f"Status: {result['status']}")
    print(f"Workflow ID: {result['workflow_id']}")
    print(f"\nResults:")
    for key, value in result['results'].items():
        print(f"  {key}: {value}")
    
    print(f"\nMessages ({len(result['messages'])}):")
    for msg in result['messages']:
        print(f"  [{msg['agent']}] {msg['action']} at {msg['timestamp']}")
    
    return result


async def demo_conditional_workflow():
    """Demonstrate conditional routing workflow."""
    engine = LangGraphWorkflowEngine()
    
    def process_node(state: AgentState) -> AgentState:
        state["results"]["processed"] = True
        return state
    
    def validate_node(state: AgentState) -> AgentState:
        state["results"]["validated"] = True
        return state
    
    def router(state: AgentState) -> str:
        """Route based on state."""
        if state.get("data", {}).get("validate"):
            return "validate"
        return "process"
    
    nodes = {
        "process": process_node,
        "validate": validate_node
    }
    
    workflow = engine.create_conditional_workflow(
        workflow_id="demo-conditional",
        nodes=nodes,
        router=router
    )
    
    print("\nExecuting Conditional Workflow...")
    print("="*60)
    
    initial_state = {
        "data": {
            "validate": True
        }
    }
    
    result = await engine.execute_workflow(
        "demo-conditional",
        initial_state
    )
    
    print(f"Status: {result['status']}")
    print(f"Results: {result['results']}")
    
    return result


async def main():
    """Run all demos."""
    print("\nLANGGRAPH WORKFLOW ENGINE DEMO")
    print("="*60)
    
    await demo_sequential_workflow()
    await demo_conditional_workflow()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
