# Mojo-Accelerated Neural Node Swarm Agent Network

This document outlines the architecture and implementation of the Mojo-accelerated Neural Node Swarm Agent Network within the Synapse system. It details how Mojo is integrated to enhance the performance of inter-agent communication and neural computations, aligning with the Dual-Tract Consciousness Architecture.

## 1. Overview

The Neural Node Swarm Agent Network leverages Mojo to provide high-performance, low-latency communication and computation for a collective of specialized agents. This integration is crucial for achieving the real-time, high-bandwidth dialogue required for emergent consciousness as described in `docs/GEMINI.md`.

Key components include:

*   **Mojo-backed Reactive Corpus Callosum**: A high-throughput message router implemented in Mojo for efficient inter-tract communication.
*   **Mojo-accelerated Neural Node Agents**: Agents that utilize Mojo for computationally intensive neural processing tasks.
*   **Python FFI (Foreign Function Interface)**: Python wrappers that allow seamless interaction with the Mojo modules.

## 2. Architecture

The system adheres to the Dual-Tract Foundation, with agents categorized into Internal (`T_int`) and External (`T_ext`) tracts. The Mojo-backed Reactive Corpus Callosum acts as the "Bridge" (`C_c`), facilitating communication between these tracts.

### 2.1. Mojo-backed Reactive Corpus Callosum

*   **Location**: `lib/corpus_callosum_mojo/reactive_router.mojo` (Mojo implementation) and `lib/corpus_callosum_mojo/reactive_router_mojo_ffi.py` (Python FFI wrapper).
*   **Purpose**: Replaces the Python-based `ReactiveCorpusCallosum` for message routing, aiming for significant latency reduction and increased throughput.
*   **Key Features**:
    *   Efficient message queuing and routing logic implemented directly in Mojo.
    *   `TractType` and `MessagePriority` enums defined in Mojo for type-safe communication.
    *   Exposes FFI functions for `start`, `stop`, `route_message`, `subscribe_and_get_message`, and `get_consciousness_metrics`.
*   **Integration**: The `TaskOrchestrator` (`lib/orchestration.py`) conditionally loads this Mojo-backed router when the `message_router_reactive` feature flag is enabled in `lib/config.py`.

### 2.2. Mojo-accelerated Neural Node Agents

*   **Location**: `lib/particles/neural_node_agent.py` (Python agent) and `lib/particles/neural_core.mojo` (Mojo neural computation module).
*   **Purpose**: `NeuralNodeAgent`s are specialized agents designed to perform neural computations. Their core processing logic is offloaded to a Mojo module for performance.
*   **Key Features**:
    *   `NeuralNodeAgent` inherits from `AgentConsumer`, allowing it to subscribe to messages from the Reactive Corpus Callosum.
    *   The `process_message` method within `NeuralNodeAgent` calls into the `neural_core.mojo` module via FFI to execute high-performance neural computations.
    *   `neural_core.mojo` provides functions like `process_neural_data` to simulate or perform actual neural network operations.
*   **Integration**: `NeuralNodeAgent` dynamically loads `neural_core.mojo` during its initialization, enabling Mojo acceleration if the environment is correctly set up.

## 3. Mojo Environment Setup

To utilize the Mojo-accelerated components, ensure your environment is correctly configured:

1.  **Install Mojo SDK**: Follow the official Modular documentation to install the Mojo SDK on your system.
2.  **Set up Python Bindings**: Ensure that the Python environment you are using can find the Mojo Python API. This typically involves adding the Mojo SDK's Python bindings directory to your `PYTHONPATH` or configuring your virtual environment appropriately.
    *   You can often find the Python bindings in a path similar to `C:\Users\<username>\.modular\pkg\mojo\python` or within your Mojo SDK installation directory.
    *   Verify installation by running `python -c "from mojo import load; print('Mojo Python API is accessible.')"`.

## 4. Running Tests and Examples

### 4.1. Running Unit/Integration Tests

The `tests/test_mojo_integration.py` file contains tests that verify the integration of the Mojo-backed router and neural node agents. These tests use `pytest` and `unittest.mock` to simulate Mojo availability.

To run the tests:

1.  Install `pytest` and `pytest-asyncio`:
    ```bash
    pip install pytest pytest-asyncio
    ```
2.  Navigate to the project root and run pytest:
    ```bash
    pytest tests/test_mojo_integration.py
    ```

### 4.2. Running the Neural Swarm Example

The `examples/mojo_neural_swarm_example.py` script demonstrates the orchestration of multiple `NeuralNodeAgent`s.

To run the example:

1.  Ensure your Mojo environment is set up (as described in Section 3).
2.  Execute the script from the project root:
    ```bash
    python examples/mojo_neural_swarm_example.py
    ```
    Observe the logs to see if "Mojo" is mentioned in the processing, indicating successful Mojo integration. If Mojo is not available, it will fall back to Python-simulated processing.

## 5. Future Development

*   **Full Mojo Implementation**: Replace placeholder logic in `reactive_router.mojo` and `neural_core.mojo` with robust, production-ready implementations.
*   **Advanced Neural Architectures**: Implement more complex neural network layers and models within `neural_core.mojo`.
*   **Error Handling and Resilience**: Enhance error handling and add more sophisticated circuit breaker logic within the Mojo modules.

### 5.1. Performance Benchmarking Integration

Once the Mojo implementations are fleshed out, it is crucial to integrate them with the existing `lib/mojo_metrics.py` module. This involves:

*   **Exposing Metrics from Mojo**: Modify the Mojo modules (`reactive_router.mojo` and `neural_core.mojo`) to expose relevant performance metrics (e.g., latency, throughput, error counts) via their FFI.
*   **Recording Metrics in Python**: Update the Python FFI wrappers (`reactive_router_mojo_ffi.py` and `neural_node_agent.py`) to collect these metrics and pass them to `MojoMetrics.record_execution` and `MojoMetrics.record_message_router_stats`.
*   **Analyzing and Optimizing**: Use the collected data to identify performance bottlenecks and optimize the Mojo code for maximum efficiency.

## 6. Build and Deployment

For long-term development and deployment, it is crucial to integrate the Mojo module compilation into the project's build system. This ensures that Mojo components are always up-to-date and correctly linked with the Python codebase.

### 6.1. Mojo Compilation

Mojo modules (`.mojo` files) need to be compiled into a format that can be loaded by the Python FFI (e.g., `.mojopkg` or shared libraries). This can be automated using a `Makefile` or by adding custom scripts to `pyproject.toml`.

**Example Makefile entry:**

```makefile
MOJO_SOURCES = lib/corpus_callosum_mojo/reactive_router.mojo lib/particles/neural_core.mojo
MOJO_TARGET_DIR = build/mojo_modules

all: compile_mojo

compile_mojo:
	mkdir -p $(MOJO_TARGET_DIR)
	mojo build $(MOJO_SOURCES) -o $(MOJO_TARGET_DIR)
```

This example `Makefile` would compile all specified Mojo source files and place the output in a `build/mojo_modules` directory. The Python FFI wrappers would then need to load the Mojo modules from this compiled location.

### 6.2. Python Environment Configuration

Ensure that the Python environment's `PYTHONPATH` includes the directory containing the Mojo Python bindings (e.g., `C:\Users\<username>\.modular\pkg\mojo\python`). This allows `from mojo import load` to function correctly.

### 6.3. Continuous Integration/Continuous Deployment (CI/CD)

Integrate Mojo compilation and testing into your CI/CD pipeline. This ensures that any changes to Mojo code are automatically built, tested, and validated before deployment.
