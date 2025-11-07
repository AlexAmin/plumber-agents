# Gemini Agent Rules

This document outlines the core rules and conventions for developing and interacting with Gemini agents in this project.

## General Principles

*   **Adherence to Project Conventions:** Always follow existing project conventions for code style, structure, and libraries.
*   **Tool Usage:** Verify library/framework availability and established usage before employing them.
*   **Idiomatic Changes:** Ensure changes integrate naturally and idiomatically with the surrounding code.
*   **Comments:** Add comments sparingly, focusing on *why* something is done, not *what*.
*   **Proactiveness:** Fulfill requests thoroughly, including adding tests where appropriate.
*   **Confirmation:** Do not take significant actions beyond the clear scope of a request without user confirmation.
*   **Path Construction:** Always use full absolute paths for file system operations.
*   **No Reverts:** Do not revert changes unless explicitly asked by the user or due to an error.

## Project Structure and Conventions

*   **Relative Paths for Prompts:** When the current working directory (PWD) is the project root, paths to prompt files should be relative to the PWD (e.g., `prompts/system_prompt.txt`).
*   **Modular Tools:** Each tool function should reside in its own Python file within the `tools` directory (e.g., `tools/my_tool.py` for `my_tool` function).

## Model Series

*   **Gemini 2.5 Series:** We must always use models from the Gemini 2.5 series (e.g., `gemini-1.5-flash`, `gemini-1.5-pro`) for all agent interactions and development.
