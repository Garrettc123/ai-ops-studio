"""Temporal Workflow Integration for Durable Execution."""

from datetime import timedelta
from typing import Dict, Any
import asyncio


class TemporalWorkflowConfig:
    """Configuration for Temporal workflows."""
    
    def __init__(
        self,
        workflow_id: str,
        task_queue: str = "default",
        execution_timeout: int = 3600,
        retry_policy: Dict[str, Any] = None
    ):
        self.workflow_id = workflow_id
        self.task_queue = task_queue
        self.execution_timeout = timedelta(seconds=execution_timeout)
        self.retry_policy = retry_policy or {
            "initial_interval": timedelta(seconds=1),
            "maximum_interval": timedelta(seconds=100),
            "maximum_attempts": 3,
            "backoff_coefficient": 2.0
        }


class TemporalWorkflow:
    """Base class for Temporal workflows."""
    
    def __init__(self, config: TemporalWorkflowConfig):
        self.config = config
        self.activities: Dict[str, callable] = {}
    
    def register_activity(self, name: str, func: callable) -> None:
        """Register activity function.
        
        Args:
            name: Activity name
            func: Activity function
        """
        self.activities[name] = func
    
    async def execute_activity(
        self,
        activity_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute registered activity.
        
        Args:
            activity_name: Name of activity
            params: Activity parameters
            
        Returns:
            Activity result
        """
        if activity_name not in self.activities:
            raise ValueError(f"Activity {activity_name} not registered")
        
        activity = self.activities[activity_name]
        
        # Execute with retry logic
        attempts = 0
        max_attempts = self.config.retry_policy["maximum_attempts"]
        
        while attempts < max_attempts:
            try:
                result = await activity(params)
                return {"status": "success", "result": result}
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    return {"status": "failed", "error": str(e)}
                
                # Exponential backoff
                backoff = self.config.retry_policy["backoff_coefficient"] ** attempts
                await asyncio.sleep(backoff)
        
        return {"status": "failed", "error": "Max attempts exceeded"}
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow. Must be implemented by subclass.
        
        Args:
            input_data: Workflow input
            
        Returns:
            Workflow result
        """
        raise NotImplementedError("Subclass must implement run method")


class DataProcessingWorkflow(TemporalWorkflow):
    """Example data processing workflow."""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data processing workflow.
        
        Args:
            input_data: Data to process
            
        Returns:
            Processing result
        """
        results = {}
        
        # Activity 1: Extract data
        extract_result = await self.execute_activity(
            "extract",
            {"source": input_data.get("source")}
        )
        results["extract"] = extract_result
        
        if extract_result["status"] != "success":
            return {"status": "failed", "step": "extract"}
        
        # Activity 2: Transform data
        transform_result = await self.execute_activity(
            "transform",
            {"data": extract_result["result"]}
        )
        results["transform"] = transform_result
        
        if transform_result["status"] != "success":
            return {"status": "failed", "step": "transform"}
        
        # Activity 3: Load data
        load_result = await self.execute_activity(
            "load",
            {"data": transform_result["result"]}
        )
        results["load"] = load_result
        
        return {
            "status": "completed",
            "results": results
        }
