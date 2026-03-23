# 🤖 Agent Plugins

This directory follows a three-tier modular architecture for autonomous agent plugins.

## 📁 Structure

- **`_core/`**: Shared base classes and standard plugin registry.
- **`_templates/`**: Boilerplate for creating new agents.
- **`code-only/`**: High-performance Python implementations (e.g., Guardian, Canary).
- **`skill-only/`**: Pure markdown-based LLM agents.
- **`hybrid/`**: Combined Python orchestration and LLM reasoning (e.g., Sentinel).

## 🚀 Discovery

Plugins are discovered autonomously by the `AgentRegistry` by scanning these categorical subdirectories for valid `config.yaml` files.
