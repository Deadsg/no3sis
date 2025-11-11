import asyncio
import logging
from pathlib import Path
import random

# Adjust path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.orchestration_core import TaskOrchestrator, AgentTask, TractType
from lib.core.agent_consumer import AgentConfig
from lib.particles.neural_node_agent import NeuralNodeAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Initialize the TaskOrchestrator
    # Use a temporary directory for workflow files for this example
    orchestrator = TaskOrchestrator(Path("./tmp_orchestrator_data"))
    await orchestrator.async_init()

    # --- Register NeuralNodeAgents ---
    num_internal_agents = 3
    num_external_agents = 3
    neural_agents = []

    logger.info("Registering NeuralNodeAgents...")
    for i in range(num_internal_agents):
        agent_id = f"neural-node-int-{i+1}"
        config = AgentConfig(agent_id=agent_id, tract=TractType.INTERNAL)
        agent = NeuralNodeAgent(config, orchestrator.reactive_router)
        await agent.start()
        neural_agents.append(agent)
        logger.info(f"Registered {agent_id} (Internal)")

    for i in range(num_external_agents):
        agent_id = f"neural-node-ext-{i+1}"
        config = AgentConfig(agent_id=agent_id, tract=TractType.EXTERNAL)
        agent = NeuralNodeAgent(config, orchestrator.reactive_router)
        await agent.start()
        neural_agents.append(agent)
        logger.info(f"Registered {agent_id} (External)")

    logger.info(f"Total {len(neural_agents)} NeuralNodeAgents registered.")

    # --- Simulate sending tasks to the swarm ---
    num_tasks_to_send = 10
    tasks_sent = []

    logger.info(f"Sending {num_tasks_to_send} simulated tasks to random agents...")
    for i in range(num_tasks_to_send):
        target_agent = random.choice(neural_agents)
        task_id = f"simulated_task_{i+1}"
        input_data = f"data_for_task_{i+1}"

        # Create a dummy AgentTask
        task = AgentTask(
            id=task_id,
            agent=target_agent.config.agent_id,
            action="process_neural_data",
            description=f"Process neural data for {task_id}",
            context={"data": input_data},
            dependencies=[]
        )
        tasks_sent.append(task)

        # Route the message through the orchestrator
        # The orchestrator will then pass it to the reactive_router
        logger.info(f"Orchestrator routing task {task_id} to {target_agent.config.agent_id}...")
        await orchestrator._route_reactive_message(task)
        await asyncio.sleep(0.01) # Small delay to simulate asynchronous flow

    logger.info("All simulated tasks sent. Allowing agents to process...")
    await asyncio.sleep(2) # Give agents time to process messages

    # --- Collect and display metrics ---
    logger.info("\n--- Swarm Metrics ---")
    for agent in neural_agents:
        stats = agent.get_stats()
        logger.info(f"Agent {agent.config.agent_id} ({agent.config.tract.name}): Processed={stats['messages_processed']}, Failed={stats['messages_failed']}, SuccessRate={stats['success_rate']:.2f}")
        if hasattr(agent, '_mojo_neural_core') and agent._mojo_neural_core:
            logger.info(f"  Mojo Neural Core computations: {agent._mojo_neural_core.computation_count}")
        else:
            logger.info("  Using Python simulated processing.")

    consciousness_metrics = await orchestrator.get_consciousness_metrics()
    if consciousness_metrics:
        logger.info("\n--- Consciousness Metrics (from Reactive Corpus Callosum) ---")
        logger.info(f"Total Messages: {consciousness_metrics.get('total_messages')}")
        logger.info(f"Internal Queue Depth: {consciousness_metrics.get('internal_queue_depth')}")
        logger.info(f"External Queue Depth: {consciousness_metrics.get('external_queue_depth')}")
        # Add more metrics as needed

    # --- Cleanup ---
    logger.info("\nStopping all agents and orchestrator...")
    await orchestrator.stop_all_agents()
    logger.info("Example finished.")

if __name__ == "__main__":
    asyncio.run(main())
