"""
Implement simple MAS using observer pattern
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import date

class EventType(Enum):
    CAPACITY_CHECK = "capacity_check"
    ALLOCATE = "allocate"
    URGENT_ORDER = "urgent_order"

class Status(Enum):
    AVAILABLE = "available"
    BUSY = "busy"

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

# Observer interface: Base Agent class 
@dataclass
class ObserverAgent(ABC):
    def subscribe(self, subject: "SubjectAgent"):
        subject.register_agent(self)
        
    @abstractmethod
    def receive_message(self): raise NotImplementedError

@dataclass(kw_only=True)
class SubjectAgent(ABC):
    agents: list[ObserverAgent] = field(default_factory=list)

    def register_agent(self, agent: ObserverAgent):
        self.agents.append(agent)

    @abstractmethod
    def broadcast_event(self): raise NotImplementedError
    
# Observer class: Resource Agent
@dataclass
class ResourceAgent(ObserverAgent):
    name: str
    is_busy: bool = False

    def receive_message(self, **kwargs):
        sender: str = kwargs.get("sender")
        message_type: EventType = kwargs.get("message_type")

        if message_type == EventType.CAPACITY_CHECK:
            status = Status.BUSY if self.is_busy else Status.AVAILABLE
            print(f"🤖 [{self.name}] 收到來自 {sender} 的查詢。目前狀態: {status.value}")
            return status
        elif message_type == EventType.ALLOCATE:
            self.is_busy = True
            print(f"✅ [{self.name}] 已成功鎖定資源，準備執行任務。")

# Observer class: Scheduler Agent
@dataclass
class SchedulerAgent(ObserverAgent):
    pending_jobs: list = field(default_factory=list)

    def receive_message(self, **kwargs):
        message_type: EventType = kwargs.get("message_type")
        data: dict = kwargs.get("data")

        if message_type == EventType.URGENT_ORDER:
            print(f"🧠 [Scheduler] 偵測到急單 {data['order_id']}！開始重新計算權重...")
            self.reoptimize(data)
    
    def reoptimize(self, order_data):
        """Implement the scheduling algorithm (EDD, SPT, ...)"""
        print(f"⚖️ [Scheduler] 已將任務 {order_data['order_id']} 插入高優先級佇列。")

@dataclass(kw_only=True)
class OrderAgent(SubjectAgent):

    def update_order(self, order_data: dict, priority: Priority):
        self.broadcast_event(order_data, priority)

    def broadcast_event(self, data: dict, event_type: EventType):
        """broadcasting to all the subscriber agents"""
        print(f"\n📢 [Order {data['order_id']}] 發布事件: {event_type}")
        event: dict = {
            "sender": f"Order-{data['order_id']}",
            "message_type": event_type,
            "data": data
        }
        for agent in self.agents:
            agent.receive_message(**event)

# simulation
def main():
    # intialise MAS
    scheduler = SchedulerAgent()
    cnc_machine_1 = ResourceAgent("Machine-CNC-1")

    # create a production task
    order_agent = OrderAgent()

    # subscription
    scheduler.subscribe(order_agent)
    cnc_machine_1.subscribe(order_agent)

    # simulation: 
    # trigger reoptimisation of scheduler and capacity checking of resource 
    # by changing order status
    event_data: dict = {
        "order_id": "PO2026001",
        "deadline": date(2026, 2, 15),
        "requirement": "CNC_MILLING"
    }

    order_agent.broadcast_event(event_data, EventType.URGENT_ORDER)
    order_agent.broadcast_event(event_data, EventType.CAPACITY_CHECK)


if __name__ == "__main__":
    main()
