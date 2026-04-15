"""
PydanticAI Agent Example
The "Standard Agent Core" - Type-safe, production-grade agentic framework
"""

from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import os

# Load environment variables from .env file
load_dotenv()


# Define Pydantic models for type-safe agents
class UserBalance(BaseModel):
    """User account information"""
    user_id: str = Field(description="Unique user identifier")
    balance: float = Field(description="Current account balance")


class TaxCalculation(BaseModel):
    """Tax calculation result"""
    amount: float = Field(description="Original amount")
    state: str = Field(description="State for tax calculation")
    tax_amount: float = Field(description="Calculated tax")
    tax_rate: float = Field(description="Tax rate applied")
    total: float = Field(description="Amount + tax")


class FinancialReport(BaseModel):
    """Final financial report - structured output"""
    user_id: str = Field(description="The user ID")
    balance: UserBalance = Field(description="User balance info")
    tax_info: TaxCalculation = Field(description="Tax calculation")
    recommendation: str = Field(description="Financial recommendation")


# Define dependency context
class DatabaseContext:
    """Mock database for demonstration"""
    
    @staticmethod
    def get_balance(user_id: str) -> float:
        balances = {
            "U123": 1500.0,
            "U456": 2500.0,
            "U789": 5000.0,
        }
        return balances.get(user_id, 0.0)
    
    @staticmethod
    def get_tax_rate(state: str) -> float:
        rates = {
            "NY": 0.08,
            "CA": 0.09,
            "TX": 0.0625,
            "WA": 0.065,
        }
        return rates.get(state, 0.05)


# Initialize the agent with type-safe dependencies
db = DatabaseContext()
agent = Agent(
    model='openai:gpt-4o',
    deps_type=DatabaseContext,
    system_prompt="""You are a financial advisor assistant.
You have tools to check account balances and calculate taxes.
Always provide clear, actionable financial advice.
Return structured data when requested.""",
)


# Define tools using decorators
@agent.tool
def get_user_balance(ctx: RunContext[DatabaseContext], user_id: str) -> str:
    """Get the current balance for a user.
    
    Args:
        user_id: The unique user identifier (e.g., U123)
    
    Returns:
        A formatted string with balance information
    """
    balance = ctx.deps.get_balance(user_id)
    return f"User {user_id} has a balance of ${balance:.2f}"


@agent.tool
def calculate_tax(ctx: RunContext[DatabaseContext], amount: float, state: str) -> str:
    """Calculate sales tax for a given amount in a specific state.
    
    Args:
        amount: The dollar amount to calculate tax on
        state: Two-letter state code (NY, CA, TX, WA)
    
    Returns:
        A formatted string with tax calculation
    """
    tax_rate = ctx.deps.get_tax_rate(state)
    tax_amount = amount * tax_rate
    total = amount + tax_amount
    
    return f"Tax on ${amount:.2f} in {state}: ${tax_amount:.2f} (rate: {tax_rate*100}%) | Total: ${total:.2f}"


@agent.tool
def get_supported_states(ctx: RunContext[DatabaseContext]) -> str:
    """Get list of supported states for tax calculation."""
    states = ["NY", "CA", "TX", "WA"]
    return f"Supported states: {', '.join(states)}"


async def run_financial_advisor():
    """Run the financial advisor agent"""
    
    print("\n" + "="*70)
    print("💰 PydanticAI Financial Advisor - Type-Safe Agent")
    print("="*70 + "\n")
    
    # Example query
    query = "What is the tax on user U123's balance in NY? Give me a financial report."
    
    print(f"📝 Query: {query}\n")
    
    try:
        # Run the agent - it returns type-validated response
        result = await agent.run(query, deps=db)
        
        print(f"\n✅ Agent Response:")
        print(f"{result.data}\n")
        
        # Show all tool calls made
        if result.all_messages():
            print(f"📊 Tool Calls Summary:")
            for msg in result.all_messages():
                print(f"  - {msg}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


async def run_structured_output_example():
    """Demonstrate structured output using Pydantic models"""
    
    print("\n" + "="*70)
    print("🏗️  Structured Output Example")
    print("="*70 + "\n")
    
    # Create a specialized agent for structured financial reports
    report_agent = Agent(
        model='openai:gpt-4o',
        deps_type=DatabaseContext,
        result_type=FinancialReport,  # ← This enforces the output type!
        system_prompt="""You must analyze the financial data and return a structured report.
Always fill all fields. Be professional and data-driven.""",
    )
    
    # Add the same tools
    @report_agent.tool
    def get_balance(ctx: RunContext[DatabaseContext], user_id: str) -> str:
        balance = ctx.deps.get_balance(user_id)
        return f"User {user_id} has ${balance:.2f}"
    
    @report_agent.tool
    def calculate_tax_report(ctx: RunContext[DatabaseContext], amount: float, state: str) -> str:
        tax_rate = ctx.deps.get_tax_rate(state)
        tax_amount = amount * tax_rate
        total = amount + tax_amount
        return f"Tax: ${tax_amount:.2f} at {tax_rate*100}% rate"
    
    query = "Generate a financial report for user U456 in CA state"
    
    print(f"📝 Query: {query}\n")
    
    try:
        result = await report_agent.run(query, deps=db)
        
        # result.data is a FinancialReport object - fully typed!
        print(f"✅ Structured Report Generated:")
        print(f"\nUser ID: {result.data.user_id}")
        print(f"Balance: ${result.data.balance.balance:.2f}")
        print(f"Tax Amount: ${result.data.tax_info.tax_amount:.2f}")
        print(f"Recommendation: {result.data.recommendation}\n")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def main():
    """Main entry point"""
    import asyncio
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        return
    
    # Run examples
    asyncio.run(run_financial_advisor())
    asyncio.run(run_structured_output_example())


if __name__ == "__main__":
    main()
