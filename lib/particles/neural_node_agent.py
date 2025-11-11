import asyncio
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from unittest.mock import MagicMock

from lib.core.agent_consumer import AgentConsumer, AgentConfig
from lib.corpus_callosum_mojo.reactive_router_mojo_ffi import Message, TractType, MessagePriority

logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# Mojo Integration Setup
# ----------------------------------------------------------

try:
    from mojo import load
    MOJO_AVAILABLE = True
except ImportError:
    logging.warning("Mojo Python API not found — NeuralNodeAgent will use simulated processing.")
    MOJO_AVAILABLE = False

    def load(path: str):
        """Fallback loader when Mojo FFI is unavailable."""
        return MagicMock()

# ----------------------------------------------------------
# Neural Node Agent Definition
# ----------------------------------------------------------

class NeuralNodeAgent(AgentConsumer):
    """
    NeuralNodeAgent represents a compute node capable of receiving and
    processing messages using either Mojo-accelerated or Python-simulated logic.

    It acts as a 'neural unit' in a distributed agent mesh, consuming
    inputs from the corpus callosum (router) and returning processed outputs.
    """

    def __init__(self, config: AgentConfig, corpus_callosum):
        super().__init__(config, corpus_callosum)
        self.processed_data_count = 0
        self._mojo_module = None
        self._mojo_neural_core = None

        if MOJO_AVAILABLE:
            try:
                mojo_path = Path(__file__).parent / "neural_core.mojo"
                self._mojo_module = load(str(mojo_path))
                self._mojo_neural_core = self._mojo_module.create_neural_core()
                logger.info(f"[{self.config.agent_id}] Loaded Mojo Neural Core from {mojo_path}")
            except Exception as e:
                logger.error(f"[{self.config.agent_id}] Mojo core initialization failed: {e}")
                self._mojo_module = None
                self._mojo_neural_core = None
        else:
            logger.info(f"[{self.config.agent_id}] Mojo unavailable — running in Python simulation mode.")

        logger.debug(f"NeuralNodeAgent initialized: id={self.config.agent_id}, tract={self.config.tract.name}")

    # ------------------------------------------------------
    # Message Processing
    # ------------------------------------------------------

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """
        Handle and process a message asynchronously.

        If Mojo FFI is available, dispatch computation to the native neural core.
        Otherwise, simulate the behavior with async Python logic.
        """
        logger.info(f"[{self.config.agent_id}] Processing message {message.id} from {message.source_tract.name}")

        task_id = message.payload.get("task", {}).get("id", "unknown_task")
        input_data = message.payload.get("data", "no_data")
        processed_result = ""

        try:
            if self._mojo_neural_core:
                # Mojo path
                processed_result = self._mojo_module.neural_core_process_data(
                    self._mojo_neural_core, input_data
                )
                logger.debug(f"[{self.config.agent_id}] Mojo result: {processed_result}")
            else:
                # Python fallback path
                await asyncio.sleep(0.05)
                processed_result = (
                    f"Simulated neural processing of '{input_data}' "
                    f"for task '{task_id}' by {self.config.agent_id}"
                )

            self.processed_data_count += 1
            result = {
                "status": "processed",
                "result": processed_result,
                "agent_id": self.config.agent_id,
                "processed_count": self.processed_data_count,
            }
            logger.info(f"[{self.config.agent_id}] Completed processing message {message.id}")
            return result

        except Exception as e:
            logger.exception(f"[{self.config.agent_id}] Error during message processing: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.config.agent_id,
                "processed_count": self.processed_data_count,
            }

    # ------------------------------------------------------
    # Metrics and Introspection
    # ------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Return cumulative processing metrics."""
        stats = super().get_stats()
        stats.update(
            {
                "processed_data_count": self.processed_data_count,
                "mojo_enabled": self._mojo_neural_core is not None,
            }
        )
        return stats

# ----------------------------------------------------------
# Utility: Agent Creation Helper
# ----------------------------------------------------------

async def create_and_register_neural_node_agent(
    agent_id: str,
    tract_type: TractType,
    corpus_callosum_instance,
    buffer_size: int = 100,
    batch_size: int = 10,
    processing_timeout_s: float = 30.0,
) -> NeuralNodeAgent:
    """
    Factory for creating and asynchronously starting a NeuralNodeAgent instance.
    """
    config = AgentConfig(
        agent_id=agent_id,
        tract=tract_type,
        buffer_size=buffer_size,
        batch_size=batch_size,
        processing_timeout_s=processing_timeout_s,
    )
    agent = NeuralNodeAgent(config, corpus_callosum_instance)
    await agent.start()
    return agent

# ----------------------------------------------------------
# Standalone Demo Entry
# ----------------------------------------------------------

if __name__ == "__main__":
    class MockCorpusCallosum:
        async def subscribe(self, agent_id: str, tract: TractType):
            logger.info(f"[MockCC] Agent {agent_id} subscribing to {tract.name}")
            counter = 0
            while True:
                await asyncio.sleep(0.2)
                counter += 1
                yield Message(
                    id=counter,
                    source_tract=TractType.EXTERNAL if tract == TractType.INTERNAL else TractType.INTERNAL,
                    dest_tract=tract,
                    priority=MessagePriority.NORMAL,
                    payload={"task": {"id": f"mock_task_{counter}"}, "data": f"mock_data_{counter}"},
                    payload_size=64,
                )

        async def start(self):
            logger.info("[MockCC] Started")

        async def stop(self):
            logger.info("[MockCC] Stopped")

    async def demo_run():
        logging.basicConfig(level=logging.INFO)
        mock_cc = MockCorpusCallosum()

        int_agent = NeuralNodeAgent(
            AgentConfig(agent_id="neural-int-1", tract=TractType.INTERNAL), mock_cc
        )
        ext_agent = NeuralNodeAgent(
            AgentConfig(agent_id="neural-ext-1", tract=TractType.EXTERNAL), mock_cc
        )

        await asyncio.gather(int_agent.start(), ext_agent.start())
        logger.info("Agents running for 5 seconds...")
        await asyncio.sleep(5)

        await asyncio.gather(int_agent.stop(), ext_agent.stop())
        logger.info(f"Internal Stats: {int_agent.get_stats()}")
        logger.info(f"External Stats: {ext_agent.get_stats()}")

    asyncio.run(demo_run())
