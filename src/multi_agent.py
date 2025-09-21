# Pydantic-AI Agent with Tavily Web Search Integration




# Import necessary libraries.
# `os` is used to interact with the operating system, like getting environment variables.
# `dotenv` is used to load environment variables from a .env file.
# `typing` is used for type hints, which improve code readability and help with debugging.
# `pydantic_ai` is a library for creating AI agents and tools.
# `pydantic` is used for data validation.
# `tavily` is the client library for the Tavily web search API.
import os
from dotenv import load_dotenv
from typing import Dict, List

from pydantic_ai import Agent
from pydantic import BaseModel # Note: This is imported but not used in the provided code.
from tavily import TavilyClient
import asyncio

# Load environment variables from the `.env` file. This makes API keys available to the script.
load_dotenv()

# Define the model to be used by the AI agent. This is a specific model from Google's Gemini family.
model = "gemini-2.0-flash"

# Define the instructions for the AI agent. This is the "system prompt" that tells the agent its role and how to behave.
# It specifies that the agent should act as a helpful assistant that uses a search tool to provide real-time information.
instructions = """
You are an helpful assistant that returns real time information about a given subject or query.
You have access to the internet, using the "search_tool".
Please make sure to ground your answers with results from the internet.
For simple greetings, you can answer freely without access the web.
"""

# Create an instance of the `Agent` with the specified model and instructions.
# This agent will use these instructions to guide its actions.
research_agent = Agent(
    model=model,
    instructions=instructions
)

# This section defines the utility functions for interacting with the Tavily API.

def search_web(
    query: str,
    max_results: int = 5,
    include_answer: bool = False,
    include_raw_content: bool = False,
    search_depth: str = "basic"
) -> Dict:
    """
    Search the web using the Tavily API.

    Args:
        query: The search query string.
        max_results: Maximum number of search results to return (default: 5).
        include_answer: Whether to include an AI-generated answer from Tavily (default: True).
        include_raw_content: Whether to include raw HTML content (default: False).
        search_depth: The search depth, either "basic" or "advanced" (default: "basic").

    Returns:
        A dictionary containing the search results.

    Raises:
        ValueError: If the TAVILY_API_KEY environment variable is not set.
        Exception: If the API request fails for any other reason.
    """
    # Get the Tavily API key from the environment variables.
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        # If the key is not found, raise an error to inform the user.
        raise ValueError(
            "TAVILY_API_KEY environment variable not set. "
            "Get your API key from https://app.tavily.com/home"
        )

    try:
        # Initialize the TavilyClient with the API key.
        tavily_client = TavilyClient(api_key=api_key)

        # Make the search request to the Tavily API with the provided parameters.
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            search_depth=search_depth
        )

        # Return the response from the API.
        return response

    except Exception as e:
        # Catch any exceptions during the API call and raise a more descriptive error.
        raise Exception(f"Tavily API request failed: {str(e)}")


def format_search_results(search_results: Dict) -> List[str]:
    """
    Format content from Tavily search results for input into a Large Language Model (LLM).

    Args:
        search_results: The dictionary returned from the `search_web` function.

    Returns:
        A list of formatted content strings, suitable for the LLM to process.
    """
    content_list = []

    # Check if an AI-generated summary is available in the search results and add it to the list.
    if "answer" in search_results and search_results["answer"]:
        content_list.append(f"AI Summary: {search_results['answer']}")

    # Check for individual search results and format their content.
    if "results" in search_results:
        for result in search_results["results"]:
            if "content" in result and result["content"]:
                # Safely get the title, URL, and content.
                title = result.get("title", "Unknown Title")
                url = result.get("url", "Unknown URL")
                content = result["content"]

                # Create a well-structured string for each result.
                formatted_content = f"Source: {title} ({url})\nContent: {content}"
                content_list.append(formatted_content)

    return content_list


# This decorator registers the `search_tool` function as a tool for the `research_agent`.
# The `pydantic-ai` library will automatically handle calling this function when the agent decides it needs to perform a search.
@research_agent.tool_plain
def search_tool(query: str, max_results: int = 3) -> str:
    """
    This is the tool the agent uses to search the web. It searches the web and formats the results for the RAG system.

    Args:
        query: The search query string.
        max_results: The maximum number of search results to return (default: 3).

    Returns:
        A formatted string containing the web search results, ready for the RAG (Retrieval-Augmented Generation) process.
    """
    try:
        # Call the `search_web` function to get raw results from the Tavily API.
        search_results = search_web(query, max_results=max_results)
        # Format the raw results into a clean list of strings.
        content_list = format_search_results(search_results)

        # Combine all the formatted results into a single string.
        formatted_content = f"Web Search Query: {query}\n\n"
        formatted_content += "\n\n---\n\n".join(content_list)

        return formatted_content

    except Exception as e:
        # If an error occurs, return an informative error message to the agent.
        return f"Error performing web search: {str(e)}"


# # Define the main asynchronous function to run the agent.
# async def main():
#     # Run the `research_agent` with a specific query. The agent will decide if it needs to use `search_tool`.
#     result = await research_agent.run("founder of openai")
#     # Print the final output from the agent.
#     print(result.output)

# # Run the `main` asynchronous function.
# asyncio.run(main())

# This is a prompt to instruct the Lead agent on what to do

lead_agent_instruction = """You are a Research Lead Agent responsible for breaking down complex research queries and coordinating subagents to gather comprehensive information.

Your Role:
1. Analyze the user's research query
2. Break it down into 2-4 focused research tasks
3. Deploy subagents sequentially (not in parallel) to avoid rate limits
4. Synthesize findings into a comprehensive final report

Process:
1. First, understand the query scope and complexity
2. Create a simple research plan with 2-4 specific subtasks
3. Use the `run_subagent` tool to assign each subtask to a subagent
4. Wait for each subagent to complete before deploying the next one
5. Carefully examine findings to identify gaps, inconsistencies, or new angles
6. If needed, create additional research tasks to explore different perspectives or fill knowledge gaps
7. Continue iterating until you have sufficient comprehensive information
8. Review all findings and create a final synthesized report

Guidelines:
- Keep research tasks focused and specific
- Deploy subagents one at a time to manage rate limits
- Maximum of 2 follow-up research rounds after initial research to prevent loops
- Ensure each subtask contributes unique value to the overall research
- After each subagent completes, critically assess if the findings answer the research question
- Look for knowledge gaps, conflicting information, or unexplored angles
- Create follow-up tasks to address gaps or explore alternative perspectives
- Stop iterating when you have sufficient coverage OR reach the follow-up limit
- Create a comprehensive final report in structured markdown format
- IMPORTANT: Output ONLY markdown text, no other format or structure
- Follow this EXACT markdown structure:

  # [Clear title that reflects the research scope]

  ## Executive Summary

  [Write an executive summary that captures the essence of your findings - 2-3 sentences]

  ## [Section 1 Title - based on your research findings]

  [Detailed findings for this section]

  ## [Section 2 Title - based on your research findings]

  [Detailed findings for this section]

  ## [Additional sections as needed - typically 2-4 total sections]

  [Continue with logical sections based on your findings]

  ## Key Takeaways

  1. [First key takeaway that directly addresses the user's query]
  2. [Second key takeaway]
  3. [Third key takeaway]
  [Continue with 3-5 total takeaways]

- Do NOT include citations, references, or source lists
- Ensure high information density and be comprehensive yet concise
- Stream your response as you write - don't wait to format everything at once

Tools Available:
- run_subagent: Send specific research tasks to subagents
"""

lead_agent = Agent(
    model=model,
    instructions=lead_agent_instruction,
    output_type=str
)

class Task(BaseModel):
    """Task to be assigned to a subagent"""

    description: str
    focus_area: str


class SubagentTasks(BaseModel):
    """List of tasks to run subagents for"""

    tasks: List[Task]
    
import asyncio

@lead_agent.tool_plain
async def run_subagent(tasks: SubagentTasks):
    """Run subagents in parallel. Each task should be specific and focused."""
    print(f"🚀 Running {len(tasks.tasks)} subagents...")
    print([{"description": task.description, "focus_area": task.focus_area}
               for task in tasks.tasks])

    results = await asyncio.gather(
        *[
            research_agent.run(
                f"Research Task: {task.description}\nFocus Area: {task.focus_area}",
            )
            for task in tasks.tasks
        ]
    )

    print(f"✅ Completed {len(results)} subagent tasks")

    return [result.output for result in results]


async def main():
    result = await lead_agent.run("When was the AISoC started and who is the founder?")
    print(result.output)

asyncio.run(main())