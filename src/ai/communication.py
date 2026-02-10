"""
Agent Communication Protocol for Multi-Agent Rescue System

Implements a message-passing framework enabling explicit coordination between agents.
Supports Contract Net Protocol (CNP) for task allocation and coalition formation.

Message Types:
- TASK_REQUEST: Announce task availability (survivors needing rescue)
- TASK_BID: Agent proposes capability to handle task
- TASK_AWARD: Task manager assigns task to winning bidder
- HELP_REQUEST: Agent requests assistance from others
- STATUS_UPDATE: Periodic state broadcast
- COALITION_INVITE: Request to form multi-agent team
- COALITION_ACCEPT/REJECT: Response to coalition invitation

Author: Enhanced Multi-Agent System
Date: February 2026
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import time


class MessageType(Enum):
    """Types of messages agents can exchange."""
    TASK_REQUEST = "task_request"     # Call for proposals (CFP)
    TASK_BID = "task_bid"             # Proposal submission
    TASK_AWARD = "task_award"         # Task assignment
    TASK_REJECT = "task_reject"       # Bid rejection
    HELP_REQUEST = "help_request"     # Request assistance
    STATUS_UPDATE = "status_update"   # Periodic state broadcast
    COALITION_INVITE = "coalition_invite"  # Form team
    COALITION_ACCEPT = "coalition_accept"  # Join team
    COALITION_REJECT = "coalition_reject"  # Decline team
    TASK_COMPLETE = "task_complete"   # Task finished notification
    CANCEL_TASK = "cancel_task"       # Task cancellation


@dataclass
class Message:
    """
    Represents a single message between agents.
    
    Attributes:
        msg_type: Type of message
        sender_id: ID of sending agent
        receiver_id: ID of receiving agent (None for broadcast)
        content: Message payload (type-specific data)
        timestamp: When message was created
        priority: Message priority (higher = more urgent)
        ttl: Time-to-live (messages expire after this many timesteps)
    """
    msg_type: MessageType
    sender_id: int
    receiver_id: Optional[int]  # None = broadcast
    content: Dict[str, Any]
    timestamp: int = 0
    priority: float = 0.0
    ttl: int = 10  # Messages expire after 10 timesteps
    
    def is_expired(self, current_time: int) -> bool:
        """Check if message has expired."""
        return current_time - self.timestamp > self.ttl
    
    def __lt__(self, other):
        """Enable priority queue sorting (higher priority first)."""
        return self.priority > other.priority


@dataclass
class TaskBid:
    """
    Represents an agent's bid for a task.
    
    Attributes:
        agent_id: Bidding agent ID
        task_id: Task identifier (e.g., survivor position)
        cost: Estimated cost to complete task (lower is better)
        capability: Agent's capability score for this task type
        risk: Estimated risk of task execution
        expected_time: Estimated timesteps to completion
        current_load: Agent's current task count
    """
    agent_id: int
    task_id: Tuple[int, int]  # Survivor position
    cost: float
    capability: float = 1.0
    risk: float = 0.0
    expected_time: int = 0
    current_load: int = 0
    
    def score(self, cost_weight: float = 0.6, risk_weight: float = 0.4) -> float:
        """
        Calculate bid quality score (lower is better).
        
        Args:
            cost_weight: Weight for cost component
            risk_weight: Weight for risk component
            
        Returns:
            Combined score for bid evaluation
        """
        # Normalize cost and risk to [0, 1] range
        # Add small penalty for current load
        load_penalty = self.current_load * 0.1
        return (cost_weight * self.cost + 
                risk_weight * self.risk * 100 + 
                load_penalty)


class CommunicationNetwork:
    """
    Manages message passing between agents with range limitations.
    
    Implements a communication network where agents can only send/receive
    messages within a certain range. Supports both directed and broadcast messages.
    """
    
    def __init__(self, communication_range: float = 15.0, enable_broadcast: bool = True):
        """
        Initialize communication network.
        
        Args:
            communication_range: Maximum distance for message transmission
            enable_broadcast: Allow broadcast messages (unlimited range)
        """
        self.communication_range = communication_range
        self.enable_broadcast = enable_broadcast
        self.message_queues: Dict[int, List[Message]] = {}  # agent_id -> messages
        self.message_history: List[Message] = []  # For analysis/visualization
        self.current_timestep = 0
        
    def register_agent(self, agent_id: int):
        """Register an agent in the communication network."""
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = []
    
    def send_message(self, message: Message, agent_positions: Dict[int, Tuple[int, int]]):
        """
        Send a message, respecting range limitations.
        
        Args:
            message: Message to send
            agent_positions: Current positions of all agents {agent_id: (x, y)}
        """
        message.timestamp = self.current_timestep
        
        # Broadcast message - all agents receive
        if message.receiver_id is None and self.enable_broadcast:
            for agent_id in self.message_queues.keys():
                if agent_id != message.sender_id:  # Don't send to self
                    self.message_queues[agent_id].append(message)
            self.message_history.append(message)
            return
        
        # Directed message - check range
        if message.receiver_id is not None:
            sender_pos = agent_positions.get(message.sender_id)
            receiver_pos = agent_positions.get(message.receiver_id)
            
            if sender_pos and receiver_pos:
                distance = self._manhattan_distance(sender_pos, receiver_pos)
                
                # Within range - deliver message
                if distance <= self.communication_range:
                    self.message_queues[message.receiver_id].append(message)
                    self.message_history.append(message)
                # Out of range - message dropped (could add logging here)
    
    def receive_messages(self, agent_id: int, msg_type: Optional[MessageType] = None) -> List[Message]:
        """
        Retrieve messages for an agent, optionally filtered by type.
        
        Args:
            agent_id: Agent ID requesting messages
            msg_type: Optional filter for message type
            
        Returns:
            List of messages for the agent
        """
        if agent_id not in self.message_queues:
            return []
        
        # Remove expired messages
        self.message_queues[agent_id] = [
            msg for msg in self.message_queues[agent_id]
            if not msg.is_expired(self.current_timestep)
        ]
        
        messages = self.message_queues[agent_id]
        
        # Filter by type if specified
        if msg_type:
            messages = [msg for msg in messages if msg.msg_type == msg_type]
        
        # Clear retrieved messages (single delivery)
        if msg_type:
            self.message_queues[agent_id] = [
                msg for msg in self.message_queues[agent_id]
                if msg.msg_type != msg_type
            ]
        else:
            self.message_queues[agent_id] = []
        
        return messages
    
    def peek_messages(self, agent_id: int, msg_type: Optional[MessageType] = None) -> List[Message]:
        """
        View messages without removing them from queue.
        
        Args:
            agent_id: Agent ID
            msg_type: Optional filter for message type
            
        Returns:
            List of messages (queue not modified)
        """
        if agent_id not in self.message_queues:
            return []
        
        messages = self.message_queues[agent_id]
        
        if msg_type:
            messages = [msg for msg in messages if msg.msg_type == msg_type]
        
        return messages
    
    def advance_timestep(self):
        """Increment timestep counter and clean up expired messages."""
        self.current_timestep += 1
        
        # Remove expired messages from all queues
        for agent_id in self.message_queues:
            self.message_queues[agent_id] = [
                msg for msg in self.message_queues[agent_id]
                if not msg.is_expired(self.current_timestep)
            ]
    
    def get_message_count(self, agent_id: int) -> int:
        """Get number of pending messages for an agent."""
        return len(self.message_queues.get(agent_id, []))
    
    def get_network_stats(self) -> Dict[str, Any]:
        """
        Get communication network statistics.
        
        Returns:
            Dictionary with network metrics
        """
        total_messages = len(self.message_history)
        messages_by_type = {}
        
        for msg in self.message_history:
            msg_type = msg.msg_type.value
            messages_by_type[msg_type] = messages_by_type.get(msg_type, 0) + 1
        
        pending_messages = sum(len(queue) for queue in self.message_queues.values())
        
        return {
            'total_messages_sent': total_messages,
            'messages_by_type': messages_by_type,
            'pending_messages': pending_messages,
            'registered_agents': len(self.message_queues),
            'current_timestep': self.current_timestep
        }
    
    def clear_history(self):
        """Clear message history (for memory management in long simulations)."""
        self.message_history = []
    
    @staticmethod
    def _manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class ContractNetProtocol:
    """
    Implements Contract Net Protocol (CNP) for task allocation.
    
    CNP Process:
    1. Manager announces task (TASK_REQUEST)
    2. Agents submit bids (TASK_BID)
    3. Manager evaluates bids and awards task (TASK_AWARD)
    4. Winning agent executes task
    5. Agent reports completion (TASK_COMPLETE)
    """
    
    def __init__(self, communication_network: CommunicationNetwork, bidding_timeout: int = 3):
        """
        Initialize CNP handler.
        
        Args:
            communication_network: Network for message passing
            bidding_timeout: Timesteps to wait for bids
        """
        self.network = communication_network
        self.bidding_timeout = bidding_timeout
        self.active_cfps: Dict[Tuple[int, int], int] = {}  # task_id -> announcement_time
        self.awarded_tasks: Dict[Tuple[int, int], int] = {}  # task_id -> agent_id
        
    def announce_task(self, manager_id: int, task_id: Tuple[int, int], 
                     task_details: Dict[str, Any], agent_positions: Dict[int, Tuple[int, int]]):
        """
        Announce a task for bidding (Call for Proposals).
        
        Args:
            manager_id: ID of agent/system managing task
            task_id: Unique task identifier (survivor position)
            task_details: Task information (type, priority, etc.)
            agent_positions: Current agent positions
        """
        message = Message(
            msg_type=MessageType.TASK_REQUEST,
            sender_id=manager_id,
            receiver_id=None,  # Broadcast
            content={
                'task_id': task_id,
                'details': task_details,
                'deadline': self.network.current_timestep + self.bidding_timeout
            },
            priority=task_details.get('priority', 0.5)
        )
        
        self.network.send_message(message, agent_positions)
        self.active_cfps[task_id] = self.network.current_timestep
    
    def submit_bid(self, bid: TaskBid, agent_positions: Dict[int, Tuple[int, int]]):
        """
        Submit a bid for a task.
        
        Args:
            bid: TaskBid object with agent's proposal
            agent_positions: Current agent positions
        """
        message = Message(
            msg_type=MessageType.TASK_BID,
            sender_id=bid.agent_id,
            receiver_id=0,  # Send to manager (ID 0 = simulator/central)
            content={
                'task_id': bid.task_id,
                'bid': bid
            },
            priority=1.0 / (bid.score() + 0.01)  # Better bids = higher priority
        )
        
        self.network.send_message(message, agent_positions)
    
    def evaluate_bids(self, task_id: Tuple[int, int], bids: List[TaskBid]) -> Optional[int]:
        """
        Evaluate bids and select winner.
        
        Args:
            task_id: Task being evaluated
            bids: List of received bids
            
        Returns:
            Winning agent ID, or None if no valid bids
        """
        if not bids:
            return None
        
        # Sort bids by score (lower is better)
        bids_sorted = sorted(bids, key=lambda b: b.score())
        winner = bids_sorted[0]
        
        # Record task award
        self.awarded_tasks[task_id] = winner.agent_id
        
        return winner.agent_id
    
    def award_task(self, task_id: Tuple[int, int], winner_id: int, 
                   agent_positions: Dict[int, Tuple[int, int]]):
        """
        Award task to winning bidder.
        
        Args:
            task_id: Task being awarded
            winner_id: Winning agent ID
            agent_positions: Current agent positions
        """
        # Send award to winner
        award_message = Message(
            msg_type=MessageType.TASK_AWARD,
            sender_id=0,  # Manager
            receiver_id=winner_id,
            content={
                'task_id': task_id,
                'awarded': True
            },
            priority=1.0
        )
        
        self.network.send_message(award_message, agent_positions)
        
        # Remove from active CFPs
        if task_id in self.active_cfps:
            del self.active_cfps[task_id]
    
    def is_task_awarded(self, task_id: Tuple[int, int]) -> bool:
        """Check if a task has been awarded."""
        return task_id in self.awarded_tasks
    
    def get_task_agent(self, task_id: Tuple[int, int]) -> Optional[int]:
        """Get the agent assigned to a task."""
        return self.awarded_tasks.get(task_id)
    
    def complete_task(self, task_id: Tuple[int, int], agent_id: int, 
                     agent_positions: Dict[int, Tuple[int, int]]):
        """
        Mark task as completed and notify network.
        
        Args:
            task_id: Completed task
            agent_id: Agent who completed it
            agent_positions: Current agent positions
        """
        message = Message(
            msg_type=MessageType.TASK_COMPLETE,
            sender_id=agent_id,
            receiver_id=None,  # Broadcast
            content={
                'task_id': task_id,
                'completion_time': self.network.current_timestep
            }
        )
        
        self.network.send_message(message, agent_positions)
        
        # Remove from awarded tasks
        if task_id in self.awarded_tasks:
            del self.awarded_tasks[task_id]
