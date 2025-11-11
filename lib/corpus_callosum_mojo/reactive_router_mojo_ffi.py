# reactive_router_mojo_ffi.py
# Python FFI wrapper for the Mojo Reactive Corpus Callosum message router.

import asyncio
import logging
import json
from enum import Enum
from typing import Any, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
from pathlib import Path

# Attempt to import Mojo's FFI capabilities
try:
    from mojo import load
    MOJO_AVAILABLE = True
except ImportError:
    logging.warning("Mojo Python API not found. Mojo-backed router will not be available.")
    MOJO_AVAILABLE = False

logger = logging.getLogger(__name__)

# --- Enums and Message class, mirroring Mojo definitions ---
class TractType(Enum):
    INTERNAL = 0
    EXTERNAL = 1

    def __int__(self):
        return self.value

class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3
    CRITICAL = 4

    def __int__(self):
        return self.value

@dataclass
class Message:
    id: int
    source_tract: TractType
    dest_tract: TractType
    priority: MessagePriority
    payload: Dict[str, Any]
    payload_size: int
    timestamp: float = 0.0

    @staticmethod
    def from_mojo_message(mojo_msg: Any) -> 'Message':
        """Converts a Mojo Message object to a Python Message dataclass."""
        # Assuming mojo_msg has attributes like id, source_tract_val, dest_tract_val, etc.
        # and payload_str which needs to be deserialized.
        payload_dict = json.loads(mojo_msg.payload_str)
        return Message(
            id=mojo_msg.id,
            source_tract=TractType(mojo_msg.source_tract.value),
            dest_tract=TractType(mojo_msg.dest_tract.value),
            priority=MessagePriority(mojo_msg.priority.value),
            payload=payload_dict,
            payload_size=mojo_msg.payload_size,
            timestamp=mojo_msg.timestamp
        )

class ReactiveCorpusCallosumMojoFFI:
    """
    Python FFI wrapper for the Mojo Reactive Corpus Callosum.
    This class will interact with the compiled Mojo module.
    """
    def __init__(self):
        logger.info("Initializing ReactiveCorpusCallosumMojoFFI (Mojo-backed)")
        self._mojo_router = None
        self._mojo_module = None
        self._is_running = False

        if MOJO_AVAILABLE:
            try:
                # Load the compiled Mojo module
                mojo_path = Path(__file__).parent / "reactive_router.mojo"
                self._mojo_module = load(str(mojo_path))
                self._mojo_router = self._mojo_module.create_router()
                logger.info(f"Mojo module loaded from {mojo_path}")
            except Exception as e:
                logger.error(f"Failed to load Mojo module or create router: {e}")
                self._mojo_module = None
                self._mojo_router = None
        else:
            logger.warning("Mojo is not available, ReactiveCorpusCallosumMojoFFI will not function.")

    async def start(self):
        """Starts the Mojo-backed reactive router."""
        if not self._mojo_router:
            logger.error("Mojo router not initialized, cannot start.")
            return
        if self._is_running:
            logger.warning("Mojo Reactive Corpus Callosum already running.")
            return

        logger.info("Mojo Reactive Corpus Callosum starting...")
        try:
            self._mojo_module.router_start(self._mojo_router)
            self._is_running = True
            logger.info("Mojo Reactive Corpus Callosum started.")
        except Exception as e:
            logger.error(f"Failed to start Mojo router: {e}")

    async def stop(self):
        """Stops the Mojo-backed reactive router."""
        if not self._mojo_router or not self._is_running:
            logger.warning("Mojo Reactive Corpus Callosum not running, cannot stop.")
            return

        logger.info("Mojo Reactive Corpus Callosum stopping...")
        try:
            self._mojo_module.router_stop(self._mojo_router)
            self._is_running = False
            logger.info("Mojo Reactive Corpus Callosum stopped.")
        except Exception as e:
            logger.error(f"Failed to stop Mojo router: {e}")

    async def route_message(
        self,
        source_tract: TractType,
        dest_tract: TractType,
        priority: Any, # This will be MessagePriority enum
        payload: Dict[str, Any],
        payload_size: int
    ) -> int:
        """
        Routes a message through the Mojo-backed Corpus Callosum.
        """
        if not self._mojo_router or not self._is_running:
            logger.error("Mojo router not running, cannot route message.")
            return -1

        logger.debug(f"Mojo FFI: Routing message from {source_tract.name} to {dest_tract.name}")
        try:
            # Serialize payload to JSON string for Mojo
            payload_str = json.dumps(payload)
            message_id = self._mojo_module.router_route_message(
                self._mojo_router,
                int(source_tract),
                int(dest_tract),
                int(priority),
                payload_str,
                payload_size
            )
            return message_id
        except Exception as e:
            logger.error(f"Failed to route message via Mojo: {e}")
            return -1

    async def subscribe(self, agent_id: str, tract: TractType) -> AsyncGenerator[Message, None]:
        """
        Subscribes an agent to receive messages from a specific tract.
        """
        if not self._mojo_router or not self._is_running:
            logger.error("Mojo router not running, cannot subscribe.")
            return

        logger.debug(f"Mojo FFI: Agent {agent_id} subscribing to {tract.name} tract")
        while self._is_running:
            try:
                # Call Mojo function to get a message
                mojo_msg = self._mojo_module.router_subscribe_and_get_message(
                    self._mojo_router,
                    agent_id,
                    int(tract)
                )
                
                # Check if it's a dummy "no_message" from Mojo
                if mojo_msg.id == 0 and mojo_msg.payload_str == "no_message":
                    await asyncio.sleep(0.01) # Wait a bit before polling again
                    continue

                # Convert Mojo Message to Python Message dataclass
                py_msg = Message.from_mojo_message(mojo_msg)
                yield py_msg
            except Exception as e:
                logger.error(f"Error during Mojo subscription for agent {agent_id}: {e}")
                await asyncio.sleep(0.1) # Wait before retrying
                if not self._is_running:
                    break # Exit if router was stopped

    async def get_consciousness_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves consciousness emergence metrics from the Mojo router.
        """
        if not self._mojo_router:
            logger.error("Mojo router not initialized, cannot get metrics.")
            return None

        logger.debug("Mojo FFI: Getting consciousness metrics")
        try:
            metrics_json_str = self._mojo_module.router_get_consciousness_metrics(self._mojo_router)
            metrics_dict = json.loads(metrics_json_str)
            return metrics_dict
        except Exception as e:
            logger.error(f"Failed to get consciousness metrics from Mojo: {e}")
            return None

# Singleton instance for the FFI wrapper
_mojo_ffi_instance: Optional[ReactiveCorpusCallosumMojoFFI] = None

def get_reactive_corpus_callosum_mojo_ffi() -> ReactiveCorpusCallosumMojoFFI:
    global _mojo_ffi_instance
    if _mojo_ffi_instance is None:
        _mojo_ffi_instance = ReactiveCorpusCallosumMojoFFI()
    return _mojo_ffi_instance
