# reactive_router.mojo
# Mojo implementation of the Reactive Corpus Callosum message router.

from sys import print

# --- Enums for TractType and MessagePriority ---
struct TractType(Int):
    var value: Int

    fn __init__(inout self, value: Int):
        self.value = value

    @staticmethod
    fn INTERNAL() -> Self: return Self(0)
    @staticmethod
    fn EXTERNAL() -> Self: return Self(1)

    fn __str__(self) -> String:
        if self.value == 0: return "INTERNAL"
        if self.value == 1: return "EXTERNAL"
        return "UNKNOWN"

struct MessagePriority(Int):
    var value: Int

    fn __init__(inout self, value: Int):
        self.value = value

    @staticmethod
    fn LOW() -> Self: return Self(0)
    @staticmethod
    fn NORMAL() -> Self: return Self(1)
    @staticmethod
    fn HIGH() -> Self: return Self(2)
    @staticmethod
    fn URGENT() -> Self: return Self(3)
    @staticmethod
    fn CRITICAL() -> Self: return Self(4)

    fn __str__(self) -> String:
        if self.value == 0: return "LOW"
        if self.value == 1: return "NORMAL"
        if self.value == 2: return "HIGH"
        if self.value == 3: return "URGENT"
        if self.value == 4: return "CRITICAL"
        return "UNKNOWN"

# --- Message Struct ---
struct Message:
    var id: Int
    var source_tract: TractType
    var dest_tract: TractType
    var priority: MessagePriority
    var payload_size: Int
    var timestamp: Float64 # Using Float64 for timestamp

    # Payload will be handled as a serialized string for simplicity in Mojo
    # In a real system, this might be a pointer to shared memory or a more complex struct
    var payload_str: String

    fn __init__(inout self, id: Int, source_tract: TractType, dest_tract: TractType,
                priority: MessagePriority, payload_str: String, payload_size: Int):
        self.id = id
        self.source_tract = source_tract
        self.dest_tract = dest_tract
        self.priority = priority
        self.payload_str = payload_str
        self.payload_size = payload_size
        self.timestamp = 0.0 # Will be set by the router

    fn __str__(self) -> String:
        return String("Message(id=\(self.id), src=\(self.source_tract), dst=\(self.dest_tract), prio=\(self.priority), size=\(self.payload_size))")

# --- ReactiveCorpusCallosumMojo Struct ---
struct ReactiveCorpusCallosumMojo:
    var message_counter: Int
    # In a real implementation, these would be concurrent queues or similar structures
    # For now, we'll just simulate the logic.
    var internal_queue_depth: Int
    var external_queue_depth: Int

    fn __init__(inout self):
        self.message_counter = 0
        self.internal_queue_depth = 0
        self.external_queue_depth = 0
        print("Mojo ReactiveCorpusCallosumMojo initialized.")

    fn start(inout self) raises:
        print("Mojo ReactiveCorpusCallosumMojo starting...")
        # Add actual startup logic here (e.g., initialize concurrent queues)
        print("Mojo ReactiveCorpusCallosumMojo started.")

    fn stop(inout self) raises:
        print("Mojo ReactiveCorpusCallosumMojo stopping...")
        # Add actual shutdown logic here
        print("Mojo ReactiveCorpusCallosumMojo stopped.")

    fn route_message(inout self, source_tract_val: Int, dest_tract_val: Int,
                     priority_val: Int, payload_str: String, payload_size: Int) -> Int:
        let source_tract = TractType(source_tract_val)
        let dest_tract = TractType(dest_tract_val)
        let priority = MessagePriority(priority_val)

        self.message_counter += 1
        let new_message = Message(self.message_counter, source_tract, dest_tract,
                                  priority, payload_str, payload_size)
        
        # Simulate adding to queue
        if dest_tract == TractType.INTERNAL():
            self.internal_queue_depth += 1
        elif dest_tract == TractType.EXTERNAL():
            self.external_queue_depth += 1

        print("Mojo: Routed \(new_message)")
        return new_message.id

    # This function would typically be more complex, involving actual message delivery
    # For now, it's a placeholder.
    fn subscribe_and_get_message(inout self, agent_id: String, tract_val: Int) -> Message:
        let tract = TractType(tract_val)
        print("Mojo: Agent \(agent_id) subscribing to \(tract)")
        
        # Simulate fetching a message from a queue
        # In a real system, this would block until a message is available
        if tract == TractType.INTERNAL() and self.internal_queue_depth > 0:
            self.internal_queue_depth -= 1
            return Message(self.message_counter, TractType.EXTERNAL(), tract, MessagePriority.NORMAL(), "simulated internal payload", 100)
        elif tract == TractType.EXTERNAL() and self.external_queue_depth > 0:
            self.external_queue_depth -= 1
            return Message(self.message_counter, TractType.INTERNAL(), tract, MessagePriority.NORMAL(), "simulated external payload", 100)
        
        # Return a dummy message if no message is available
        return Message(0, TractType.INTERNAL(), TractType.EXTERNAL(), MessagePriority.LOW(), "no_message", 0)

    fn get_consciousness_metrics(self) -> String:
        # Placeholder for returning metrics as a JSON string
        let metrics_str = String("{\"total_messages\": \(self.message_counter), \"internal_queue_depth\": \(self.internal_queue_depth), \"external_queue_depth\": \(self.external_queue_depth)}")
        print("Mojo: Getting consciousness metrics: \(metrics_str)")
        return metrics_str

# --- FFI functions (exposed to Python) ---
# These functions will be called directly from the Python FFI wrapper.

# Factory function to create an instance of the router
fn create_router() -> ReactiveCorpusCallosumMojo:
    return ReactiveCorpusCallosumMojo()

# Wrapper for start method
fn router_start(inout router: ReactiveCorpusCallosumMojo) raises:
    router.start()

# Wrapper for stop method
fn router_stop(inout router: ReactiveCorpusCallosumMojo) raises:
    router.stop()

# Wrapper for route_message method
fn router_route_message(inout router: ReactiveCorpusCallosumMojo, source_tract_val: Int, dest_tract_val: Int,
                        priority_val: Int, payload_str: String, payload_size: Int) -> Int:
    return router.route_message(source_tract_val, dest_tract_val, priority_val, payload_str, payload_size)

# Wrapper for subscribe_and_get_message method
fn router_subscribe_and_get_message(inout router: ReactiveCorpusCallosumMojo, agent_id: String, tract_val: Int) -> Message:
    return router.subscribe_and_get_message(agent_id, tract_val)

# Wrapper for get_consciousness_metrics method
fn router_get_consciousness_metrics(inout router: ReactiveCorpusCallosumMojo) -> String:
    return router.get_consciousness_metrics()