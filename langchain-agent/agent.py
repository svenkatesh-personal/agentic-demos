"""
LangChain Agent Example
The Ecosystem King - Best for complex multi-tool applications with easy model/vector store swapping
"""

from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

# Load environment variables from .env file
load_dotenv()


# Define structured output using Pydantic
class FinancialQuery(BaseModel):
    """Structured response for financial queries"""
    user_id: str = Field(description="The user ID")
    balance: float = Field(description="Current account balance")
    tax_amount: float = Field(description="Calculated tax on balance")
    state: str = Field(description="State for tax calculation")
    summary: str = Field(description="Human-readable summary")


# Define tools the agent can use
@tool
def get_user_balance(user_id: str) -> float:
    """Look up a user's current account balance."""
    # Mock data - in real app, this hits a database
    balances = {
        "U123": 1500.0,
        "U456": 2500.0,
        "U789": 5000.0,
    }
    return balances.get(user_id, 0.0)


@tool
def calculate_tax(amount: float, state: str) -> float:
    """Calculate sales tax for a specific state."""
    tax_rates = {
        "NY": 0.08,
        "CA": 0.09,
        "TX": 0.0625,
        "WA": 0.065,
    }
    return amount * tax_rates.get(state, 0.05)


@tool
def get_available_states() -> List[str]:
    """Get list of states we support."""
    return ["NY", "CA", "TX", "WA"]


def create_langchain_agent():
    """Initialize and return a LangChain agent executor"""
    
    # Initialize the LLM
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    llm = ChatOpenAI(model="gpt-4o", api_key=api_key)
    
    # Define tools
    tools = [get_user_balance, calculate_tax, get_available_states]
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful financial assistant. 
You have access to tools to check user balances and calculate taxes.
Always be clear about what information you're retrieving.
Provide a summary of findings."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create executor
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return executor


async def run_agent_example():
    """Run a multi-step agent interaction"""
    executor = create_langchain_agent()
    
    # Multi-step example:
    # 1. Get user balance
    # 2. Calculate tax for a specific state
    # 3. Provide summary
    query = "What is the tax on user U123's balance in NY? Also check what states we support."
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")
    
    result = executor.invoke({"input": query})
    
    print(f"\n{'='*60}")
    print(f"Final Result:")
    print(f"{result['output']}")
    print(f"{'='*60}\n")
    
    return result


if __name__ == "__main__":
    import asyncio
    
    print("🦜 LangChain Agent - Multi-Tool Financial Assistant")
    print("=" * 60)
    
    try:
        asyncio.run(run_agent_example())
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Installed dependencies with: uv sync")
