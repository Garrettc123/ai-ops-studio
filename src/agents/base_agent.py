"""Base Agent Class for Multi-Agent System."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class AgentStatus(Enum):
    """Agent lifecycle status."""
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    message_type: str = "task"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 5  # 1-10, 1 = highest
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority
        }


@dataclass
class AgentState:
    """Agent state for tracking."""
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[Dict[str, Any]] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_to_history(self, event: Dict[str, Any]) -> None:
        """Add event to agent history."""
        event["timestamp"] = datetime.utcnow().isoformat()
        self.history.append(event)


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: List[str],
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.config = config or {}
        self.state = AgentState(agent_id=agent_id)
        self.message_queue: List[AgentMessage] = []
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task. Must be implemented by subclasses.
        
        Args:
            task: Task configuration and parameters
            
        Returns:
            Task execution results
        """
        pass
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle task type.
        
        Args:
            task_type: Type of task to check
            
        Returns:
            True if agent has capability
        """
        return task_type in self.capabilities
    
    async def receive_message(self, message: AgentMessage) -> None:
        """Receive message from another agent.
        
        Args:
            message: Incoming message
        """
        self.message_queue.append(message)
        self.state.add_to_history({
            "event": "message_received",
            "message_id": message.message_id,
            "sender": message.sender_id
        })
    
    async def send_message(
        self,
        recipient_id: str,
        content: Dict[str, Any],
        message_type: str = "task",
        priority: int = 5
    ) -> AgentMessage:
        """Send message to another agent.
        
        Args:
            recipient_id: Target agent ID
            content: Message content
            message_type: Type of message
            priority: Message priority (1-10)
            
        Returns:
            Created message
        """
        message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            content=content,
            message_type=message_type,
            priority=priority
        )
        
        self.state.add_to_history({
            "event": "message_sent",
            "message_id": message.message_id,
            "recipient": recipient_id
        })
        
        return message
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status.
        
        Returns:
            Status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.state.status.value,
            "capabilities": self.capabilities,
            "queue_size": len(self.message_queue),
            "current_task": self.state.current_task
        }
    
    async def process_queue(self) -> None:
        """Process all messages in queue."""
        while self.message_queue:
            message = self.message_queue.pop(0)
            await self.handle_message(message)
    
    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming message. Can be overridden.
        
        Args:
            message: Message to handle
        """
        if message.message_type == "task":
            self.state.status = AgentStatus.BUSY
            self.state.current_task = message.content
            
            try:
                result = await self.execute(message.content)
                self.state.status = AgentStatus.COMPLETED
                self.state.current_task = None
                
                # Send result back to sender
                await self.send_message(
                    recipient_id=message.sender_id,
                    content={"status": "success", "result": result},
                    message_type="result"
                )
            except Exception as e:
                self.state.status = AgentStatus.FAILED
                self.state.add_to_history({
                    "event": "task_failed",
                    "error": str(e)
                })
