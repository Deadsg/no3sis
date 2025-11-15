# Mojo Integration in Synapse

This document provides an overview of the Mojo integration within the Synapse project. Mojo is used to accelerate performance-critical components of the system.

## Overview

Mojo is integrated into the Synapse architecture to provide significant performance improvements for specific, computationally intensive tasks. The integration is focused on two key areas: pattern searching and message routing.

## Production Implementations

### 1. Pattern Search

-   **File:** `.synapse/neo4j/pattern_search_mojo.mojo`
-   **Purpose:** Accelerates vector similarity searches within the Neo4j graph database. This is a critical component of the pattern learner.
-   **Performance:** Achieved a **13.1x speedup** over the baseline Python implementation.
-   **Features:**
    -   SIMD (Single Instruction, Multiple Data) optimization for parallel data processing.
    -   FFI (Foreign Function Interface) for seamless integration with the existing Python codebase.
    -   Matrix caching to reduce redundant computations.

### 2. Corpus Callosum Message Router

-   **File:** `.synapse/corpus_callosum/message_router.mojo`
-   **Purpose:** Manages the routing of messages between the internal and external tracts of the Synapse architecture. This is a high-throughput component that benefits from Mojo's performance.
-   **Performance:** Targets a **100x+ speedup** over the `ThreadPoolExecutor` based Python implementation.
-   **Features:**
    -   Dual-tract routing logic.
    -   Priority queues for efficient message handling.
    -   SIMD-accelerated sorting of messages.

## Development and Compilation

-   **Compilation:** Each Mojo module has a `Makefile` in its directory for compilation. To compile a module, navigate to its directory and run `make build`.
-   **Prerequisites:**
    -   Mojo v25.6 or later installed via the Modular CLI.
    -   Existing Synapse environment running.

## Archived Experiments

The `.no3sis/mojo-pilot` directory contains the archived results of the initial Mojo integration experiments. This directory is for historical reference and is not required for the current production system to function.
