# Pydantic-AI Agent with Tavily Web Search Integration

## Overview

This repository contains a versatile AI agent framework that combines type-safe data structures using `pydantic` with a powerful web search tool powered by the `Tavily Search API`. The agent is designed to act as a helpful assistant that can retrieve real-time, accurate information from the internet to answer user queries.

The core of this project is a multi-agent system where a `lead_agent` orchestrates research tasks by delegating them to one or more `research_agent` subagents. This architecture enables parallel processing of multiple, focused research tasks to deliver a comprehensive and concise response.

## ✨ Features

- **Structured AI Interactions:** Utilizes `Pydantic` for robust data validation and clear input/output structures.
- **Real-time Web Search:** Integrates with the `Tavily Search API` to access up-to-date information from the web.
- **Efficient Multi-Agent Architecture:** Employs a multi-agent system for parallel execution of research tasks, ensuring fast and comprehensive results.
- **Modular Python Codebase:** The code is well-structured and easy to extend.
- **Asynchronous Operations:** Leverages `asyncio` for efficient handling of concurrent operations, such as running subagents in parallel.

## 🛠️ Technology Stack

- **Python:** The core programming language.
- **Pydantic-AI:** A framework for building and orchestrating AI agents.
- **Pydantic:** Used for data validation and settings management.
- **Tavily API:** The web search API for search augmentation.
- **Asyncio:** For asynchronous and concurrent programming.
- **python-dotenv:** To manage environment variables securely.

## Prerequisites

- Python 3.8+
- A Tavily API key.
- A supported LLM model API key (e.g., from Gemini, OpenAI, or Groq).

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/BLVCK-MAMBA-6/Pydantic-AI-Agent-with-Tavily-Web-Search-Integration
    cd Pydantic-AI-Agent-with-Tavily-Web-Search-Integration
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```
    
4.  **Set up your environment variables:**
    * Create a `.env` file in the root directory of your project.
    * Add your API keys to this file. You will need a key for your chosen LLM and a Tavily API key.

    ```bash
    # For Gemini
    GOOGLE_API_KEY="your_gemini_api_key"

    # For Tavily
    TAVILY_API_KEY="your_tavily_api_key"
    ```
    *You can get a Tavily API key by signing up on their website.*

## Usage

This project demonstrates a multi-agent system. To run the `multi_agent.py` script, you would execute it from the command line.

**Example:**

```bash
python multi_agent.py
