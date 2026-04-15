"""
OpenAI Agent SDK Example
The Minimalist - Low latency, GPT-native, minimal dependencies
"""

import json
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI, AssistantEventHandler

# Load environment variables from .env file
load_dotenv()


# Define tool schemas
class TaxCalculation(BaseModel):
    """Tax calculation result"""
    user_id: str = Field(description="User ID")
    amount: float = Field(description="Original amount")
    state: str = Field(description="State code")
    tax_rate: float = Field(description="Tax rate applied")
    tax_amount: float = Field(description="Calculated tax")
    total: float = Field(description="Total with tax")


# Define mock database
class MockDatabase:
    """Simple mock database"""
    
    BALANCES = {
        "U123": 1500.0,
        "U456": 2500.0,
        "U789": 5000.0,
    }
    
    TAX_RATES = {
        "NY": 0.08,
        "CA": 0.09,
        "TX": 0.0625,
        "WA": 0.065,
    }
    
    @staticmethod
    def get_balance(user_id: str) -> float:
        return MockDatabase.BALANCES.get(user_id, 0.0)
    
    @staticmethod
    def get_tax_rate(state: str) -> float:
        return MockDatabase.TAX_RATES.get(state, 0.05)
    
    @staticmethod
    def get_supported_states() -> list[str]:
        return list(MockDatabase.TAX_RATES.keys())


# Tool definitions for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_balance",
            "description": "Get the current balance for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID (e.g., U123)"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_tax",
            "description": "Calculate sales tax for a given amount in a specific state",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The dollar amount to calculate tax on"
                    },
                    "state": {
                        "type": "string",
                        "description": "Two-letter state code (NY, CA, TX, WA)"
                    }
                },
                "required": ["amount", "state"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_supported_states",
            "description": "Get list of supported states for tax calculation",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process tool calls and return results"""
    
    if tool_name == "get_user_balance":
        balance = MockDatabase.get_balance(tool_input["user_id"])
        return f"User {tool_input['user_id']} balance: ${balance:.2f}"
    
    elif tool_name == "calculate_tax":
        amount = tool_input["amount"]
        state = tool_input["state"]
        tax_rate = MockDatabase.get_tax_rate(state)
        tax_amount = amount * tax_rate
        total = amount + tax_amount
        
        result = TaxCalculation(
            user_id="",
            amount=amount,
            state=state,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total=total
        )
        return result.model_dump_json()
    
    elif tool_name == "get_supported_states":
        states = MockDatabase.get_supported_states()
        return f"Supported states: {', '.join(states)}"
    
    else:
        return f"Unknown tool: {tool_name}"


def run_agent_sync(query: str) -> str:
    """
    Run OpenAI agent in synchronous mode
    This is the most straightforward approach
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    client = OpenAI(api_key=api_key)
    
    print(f"\n{'='*70}")
    print(f"💬 Query: {query}")
    print(f"{'='*70}\n")
    
    messages = [
        {
            "role": "user",
            "content": query
        }
    ]
    
    # Initial request to OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    
    print(f"🤖 Initial Response:")
    print(f"  Stop Reason: {response.stop_reason}")
    
    # Handle tool calls in a loop
    max_iterations = 10
    iteration = 0
    
    while response.stop_reason == "tool_calls" and iteration < max_iterations:
        iteration += 1
        
        # Extract tool calls from response
        tool_calls = [
            choice.message.tool_calls
            for choice in response.choices
            if choice.message.tool_calls
        ]
        
        if not tool_calls:
            break
        
        # Flatten the list
        tool_calls = [call for sublist in tool_calls for call in sublist]
        
        # Process each tool call
        tool_results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)
            
            print(f"\n🔧 Tool Call #{iteration}:")
            print(f"  Function: {tool_name}")
            print(f"  Input: {tool_input}")
            
            # Execute tool
            tool_result = process_tool_call(tool_name, tool_input)
            
            print(f"  Result: {tool_result[:100]}...")
            
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": tool_result
            })
        
        # Add assistant response and tool results to messages
        messages.append(response.choices[0].message)
        messages.extend(tool_results)
        
        # Next request with tool results
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        
        print(f"\n  New Stop Reason: {response.stop_reason}")
    
    # Extract final response
    final_response = response.choices[0].message.content
    
    print(f"\n{'='*70}")
    print(f"✅ Final Answer:")
    print(f"{final_response}")
    print(f"{'='*70}\n")
    
    return final_response


def main():
    """Main entry point"""
    
    print("🚀 OpenAI Agent SDK - Multi-Tool Financial Assistant")
    print("="*70)
    
    query = "What is the tax on user U123's balance in NY?"
    
    try:
        run_agent_sync(query)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Installed dependencies with: uv sync")


if __name__ == "__main__":
    main()
