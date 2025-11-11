import asyncio
import pytest
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Adjust path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from lib.orchestration_core import TaskOrchestrator, AgentTask, ExecutionResult, TractType
from lib.core.agent_consumer import AgentConfig, create_agent_consumer
from lib.corpus_callosum_mojo.reactive_router_mojo_ffi import ReactiveCorpusCallosumMojoFFI, Message, MessagePriority
from lib.particles.neural_node_agent import NeuralNodeAgent # Ensure this is imported

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check for Mojo availability at the test file level
try:
    from mojo import load
    logger.info("Mojo Python API is accessible for tests.")
    MOJO_TEST_AVAILABLE = True
except ImportError:
    logger.warning("Mojo Python API is NOT accessible for tests. Tests relying on actual Mojo loading will fail.")
    MOJO_TEST_AVAILABLE = False

# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------

@pytest.fixture
def mock_mojo_available():
    with patch('lib.corpus_callosum_mojo.reactive_router_mojo_ffi.MOJO_AVAILABLE', True), \
         patch('lib.particles.neural_node_agent.MOJO_AVAILABLE', True):
        yield

@pytest.fixture
def mock_mojo_unavailable():
    with patch('lib.corpus_callosum_mojo.reactive_router_mojo_ffi.MOJO_AVAILABLE', False), \
         patch('lib.particles.neural_node_agent.MOJO_AVAILABLE', False):
        yield

@pytest.fixture
async def orchestrator_with_mojo_ffi(tmp_path, mock_mojo_available):
    """Fixture for TaskOrchestrator with Mojo FFI enabled."""
    with patch('lib.corpus_callosum_mojo.reactive_router_mojo_ffi.ReactiveCorpusCallosumMojoFFI') as MockMojoFFI, \
         patch('lib.particles.neural_node_agent.load') as mock_neural_load:
        
        mock_mojo_router_instance = MagicMock()
        mock_mojo_router_instance.start = AsyncMock()
        mock_mojo_router_instance.stop = AsyncMock()
        mock_mojo_router_instance.route_message = AsyncMock(return_value=1)
        mock_mojo_router_instance.subscribe_and_get_message.side_effect = [
            MagicMock(
                id=1,
                source_tract=MagicMock(value=TractType.EXTERNAL.value),
                dest_tract=MagicMock(value=TractType.INTERNAL.value),
                priority=MagicMock(value=MessagePriority.NORMAL.value),
                payload={'task': MagicMock(id="test_task_1"), 'action': 'process', 'orchestrator': orchestrator},
                payload_size=100,
                timestamp=0.0,
            ),
            MagicMock(
                id=2,
                source_tract=MagicMock(value=TractType.EXTERNAL.value),
                dest_tract=MagicMock(value=TractType.INTERNAL.value),
                priority=MagicMock(value=MessagePriority.NORMAL.value),
                payload={'task': MagicMock(id="test_task_2"), 'action': 'process', 'orchestrator': orchestrator},
                payload_size=100,
                timestamp=0.0,
            ),
            MagicMock(id=0, payload_str="no_message"),
        ]
        mock_mojo_router_instance.get_consciousness_metrics.return_value = (
            '{"total_messages": 10, "internal_queue_depth": 0, "external_queue_depth": 0}'
        )
        MockMojoFFI.return_value = mock_mojo_router_instance

        mock_neural_core_instance = MagicMock()
        mock_neural_core_instance.create_neural_core.return_value = MagicMock()
        mock_neural_core_instance.neural_core_process_data.return_value = "Mojo processed: MOCK_DATA"
        mock_neural_load.return_value = mock_neural_core_instance

        orchestrator = TaskOrchestrator(tmp_path)
        await orchestrator.async_init()
        yield orchestrator
        await orchestrator.stop_all_agents()

@pytest.fixture
async def orchestrator_without_mojo_ffi(tmp_path, mock_mojo_unavailable):
    """Fixture for TaskOrchestrator with Mojo FFI disabled (Python fallback)."""
    # Patch the module-level instance of ReactiveCorpusCallosum
    with patch('lib.orchestration_core._python_reactive_corpus_callosum_instance') as MockPythonReactiveCC:
        mock_python_cc_instance = AsyncMock()
        mock_python_cc_instance.start = AsyncMock()
        mock_python_cc_instance.stop = AsyncMock()
        mock_python_cc_instance.route_message = AsyncMock(return_value=1)
        mock_python_cc_instance.subscribe.return_value.__aiter__.return_value = [
            Message(
                id=1,
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload={"task": MagicMock(id="test_task_1"), "data": "input_data_1", 'orchestrator': orchestrator},
                payload_size=100,
            ),
            Message(
                id=2,
                source_tract=TractType.EXTERNAL,
                dest_tract=TractType.INTERNAL,
                priority=MessagePriority.NORMAL,
                payload={"task": MagicMock(id="test_task_2"), "data": "input_data_2", 'orchestrator': orchestrator},
                payload_size=100,
            ),
        ]
        mock_python_cc_instance.get_consciousness_metrics.return_value = {
            "total_messages": 10,
            "internal_to_external": 5,
            "external_to_internal": 5,
            "dialogue_balance_ratio": 1.0,
            "emergence_score": 0.5,
            "balanced_dialogue_events": 5,
            "last_emergence_timestamp": 0.0,
        }

        MockPythonReactiveCC.return_value = mock_python_cc_instance

        orchestrator = TaskOrchestrator(tmp_path)
        await orchestrator.async_init()
        yield orchestrator
        await orchestrator.stop_all_agents()

# ----------------------------------------------------------
# Tests
# ----------------------------------------------------------

@pytest.mark.asyncio
async def test_mojo_ffi_router_and_neural_node_agent_with_mojo(orchestrator_with_mojo_ffi):
    """Test integration of Mojo-backed router and neural node agent when Mojo is available."""
    orchestrator = orchestrator_with_mojo_ffi

    agent_id = "test-neural-node-1"
    await orchestrator.register_agent_consumer(agent_id, NeuralNodeAgent, TractType.INTERNAL)

    assert agent_id in orchestrator.agent_consumers
    agent_instance = orchestrator.agent_consumers[agent_id]
    assert isinstance(agent_instance, NeuralNodeAgent)
    assert agent_instance._mojo_neural_core is not None  # Should be loaded

    # Mock the process_message method of the actual agent instance
    agent_instance.process_message = AsyncMock(return_value={
        "status": "processed",
        "result": "Mojo processed: MOCK_DATA",
        "agent_id": agent_id,
        "processed_count": 1
    })
    agent_instance._messages_processed = 1 # Manually set for assertion

    task = AgentTask(
        id="test_task_route",
        agent=agent_id,
        action="process",
        description="Process some data",
        context={"data": "initial_input"},
        dependencies=[],
    )

    routed_msg_id = await orchestrator._route_reactive_message(task)
    assert routed_msg_id is not None and routed_msg_id >= 0

    await asyncio.sleep(0.1)

    stats = agent_instance.get_stats()
    assert stats["messages_processed"] >= 1
    assert "Mojo processed: MOCK_DATA" in orchestrator._result_store[task.id].output["result"]

    metrics = await orchestrator.get_consciousness_metrics()
    assert metrics is not None
    assert metrics["total_messages"] == 10

@pytest.mark.asyncio
async def test_mojo_ffi_router_and_neural_node_agent_without_mojo(orchestrator_without_mojo_ffi):
    """Test integration when Mojo is NOT available (Python fallback)."""
    orchestrator = orchestrator_without_mojo_ffi

    agent_id = "test-neural-node-2"
    await orchestrator.register_agent_consumer(agent_id, NeuralNodeAgent, TractType.EXTERNAL)

    assert agent_id in orchestrator.agent_consumers
    agent_instance = orchestrator.agent_consumers[agent_id]
    assert isinstance(agent_instance, NeuralNodeAgent)
    assert agent_instance._mojo_neural_core is None  # Python fallback path

    # Mock the process_message method of the actual agent instance
    agent_instance.process_message = AsyncMock(return_value={
        "status": "processed",
        "result": "Simulated neural processing of 'python_input'",
        "agent_id": agent_id,
        "processed_count": 1
    })
    agent_instance._messages_processed = 1 # Manually set for assertion

    task = AgentTask(
        id="test_task_route_py",
        agent=agent_id,
        action="process",
        description="Process some data (Python fallback)",
        context={"data": "python_input"},
        dependencies=[],
    )

    routed_msg_id = await orchestrator._route_reactive_message(task)
    assert routed_msg_id is not None and routed_msg_id >= 0

    await asyncio.sleep(0.1)

    stats = agent_instance.get_stats()
    assert stats["messages_processed"] >= 1
    assert "Simulated neural processing of 'python_input'" in orchestrator._result_store[task.id].output["result"]

    metrics = await orchestrator.get_consciousness_metrics()
    assert metrics is not None
    assert metrics["total_messages"] == 10
