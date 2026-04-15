"""
Google GenAI Agent Example (Vertex AI / Gemini)
The Managed RAG Choice - Integrated vector DB, lowest setup overhead
"""

import json
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel, Field
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()


# Define structured output models
class TaxCalculation(BaseModel):
    """Tax calculation result"""
    user_id: str = Field(description="User ID")
    balance: float = Field(description="User balance")
    state: str = Field(description="State code")
    tax_rate: float = Field(description="Tax rate")
    tax_amount: float = Field(description="Calculated tax")
    total: float = Field(description="Total with tax")


class FinancialSummary(BaseModel):
    """Final financial summary"""
    analysis: str = Field(description="Analysis of financial data")
    tax_calculation: TaxCalculation = Field(description="Tax details")
    recommendation: str = Field(description="Financial recommendation")


# Mock database
class MockDatabase:
    """Simple mock database for Gemini"""
    
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
    
    POLICIES = {
        "default": "Standard financial policy applies. All transactions above $5000 require approval.",
        "premium": "Premium account holders get reduced tax rates and extended support.",
    }
    
    @staticmethod
    def get_balance(user_id: str) -> float:
        return MockDatabase.BALANCES.get(user_id, 0.0)
    
    @staticmethod
    def get_tax_rate(state: str) -> float:
        return MockDatabase.TAX_RATES.get(state, 0.05)
    
    @staticmethod
    def get_policy(policy_type: str) -> str:
        return MockDatabase.POLICIES.get(policy_type, "No policy found")


# Tool definitions for Gemini
tools = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="get_user_balance",
                description="Get the current balance for a user",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "user_id": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="User ID like U123"
                        )
                    },
                    required=["user_id"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="calculate_tax",
                description="Calculate sales tax for a given amount in a specific state",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "amount": genai.protos.Schema(
                            type=genai.protos.Type.NUMBER,
                            description="Amount to calculate tax on"
                        ),
                        "state": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Two-letter state code"
                        )
                    },
                    required=["amount", "state"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="get_policy",
                description="Get financial policy information",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "policy_type": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Policy type: default or premium"
                        )
                    },
                    required=["policy_type"]
                )
            ),
        ]
    )
]


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process Gemini tool calls"""
    
    if tool_name == "get_user_balance":
        user_id = tool_input.get("user_id", "")
        balance = MockDatabase.get_balance(user_id)
        return f"User {user_id} has balance: ${balance:.2f}"
    
    elif tool_name == "calculate_tax":
        amount = tool_input.get("amount", 0)
        state = tool_input.get("state", "NY")
        tax_rate = MockDatabase.get_tax_rate(state)
        tax_amount = amount * tax_rate
        total = amount + tax_amount
        
        result = TaxCalculation(
            user_id="",
            balance=0,
            state=state,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total=total
        )
        return result.model_dump_json()
    
    elif tool_name == "get_policy":
        policy_type = tool_input.get("policy_type", "default")
        policy = MockDatabase.get_policy(policy_type)
        return policy
    
    else:
        return f"Unknown tool: {tool_name}"


def run_gemini_agent_sync(query: str):
    """Run Gemini agent with function calling"""
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Create model with tools
    model = genai.GenerativeModel(
        model_name="gemini-pro",  # Using basic gemini-pro model
        tools=tools,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024
        )
    )
    
    print(f"\n{'='*70}")
    print(f"💬 Query: {query}")
    print(f"{'='*70}\n")
    
    messages = [
        query  # Start with just the query string
    ]
    
    # Initial response
    response = model.generate_content(
        contents=messages,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024
        )
    )
    
    print(f"🤖 Gemini Initial Response:")
    
    # Process function calls
    max_iterations = 10
    iteration = 0
    
    while (hasattr(response, 'candidates') and response.candidates and
           hasattr(response.candidates[0], 'content') and
           any(part.function_call for part in response.candidates[0].content.parts 
               if hasattr(part, 'function_call'))):
        
        iteration += 1
        if iteration > max_iterations:
            break
        
        # Extract function calls
        function_calls = []
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call'):
                function_calls.append(part.function_call)
        
        if not function_calls:
            break
        
        # Build conversation history for next call
        conversation_parts = [query]  # Start with original query
        
        # Add the model's response
        conversation_parts.append(response.candidates[0].content)
        
        # Process each function call
        for func_call in function_calls:
            func_name = func_call.name
            func_args = {k: v for k, v in func_call.args.items()}
            
            print(f"\n🔧 Tool Call #{iteration}:")
            print(f"  Function: {func_name}")
            print(f"  Arguments: {func_args}")
            
            # Execute tool
            result = process_tool_call(func_name, func_args)
            
            print(f"  Result: {result[:100]}...")
            
            # Add function result to conversation
            conversation_parts.append(genai.protos.Part(
                function_response=genai.protos.FunctionResponse(
                    name=func_name,
                    response=result
                )
            ))
        
        # Get next response with updated conversation
        response = model.generate_content(
            contents=conversation_parts,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024
            )
        )
        
        print(f"\n  New Response Generated")
    
    # Extract final response
    final_response = response.text if hasattr(response, 'text') else "No response generated"
    
    print(f"\n{'='*70}")
    print(f"✅ Final Answer:")
    print(f"{final_response}")
    print(f"{'='*70}\n")
    
    return final_response


async def run_gemini_with_streaming(query: str):
    """Alternative: Streaming response from Gemini"""
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(
        model_name="gemini-pro",  # Using basic gemini-pro model
        tools=tools,
        system_instruction="You are a helpful financial advisor with access to tools."
    )
    
    print(f"\n🎬 Streaming Response:\n")
    
    # Stream the response
    response = model.generate_content(
        contents=query,
        stream=True,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024
        )
    )
    
    for chunk in response:
        if chunk.text:
            print(chunk.text, end="", flush=True)
    
    print("\n")


def main():
    """Main entry point"""
    
    print("✨ Google Gemini Agent - Financial Advisor")
    print("="*70)
    
    query = "What is the tax on user U123's balance in NY? Also check the default policy."
    
    try:
        run_gemini_agent_sync(query)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set GOOGLE_API_KEY environment variable")
        print("2. Installed dependencies with: uv sync")
        print("3. Enabled Generative AI API in Google Cloud Console")


if __name__ == "__main__":
    main()
