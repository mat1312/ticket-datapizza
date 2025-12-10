
import os
from pydantic import BaseModel, Field
from datapizza.agents import Agent
from datapizza.tools import tool
from datapizza.clients.openai import OpenAIClient
from dotenv import load_dotenv

load_dotenv()

# Mock models
class SubTask(BaseModel):
    name: str
    status: str

class Plan(BaseModel):
    tasks: list[SubTask]
    summary: str

# Test Tool with Pydantic Argument
@tool
def submit_plan(plan: Plan) -> str:
    """Submit the final plan."""
    print(f"✅ RECEIVED PLAN: {plan}")
    return "Plan submitted successfully"

def test_agent_structured_tool():
    client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
    
    agent = Agent(
        name="planner",
        client=client,
        tools=[submit_plan],
        system_prompt="Create a simple plan with 1 task and submit it using the tool."
    )
    
    print("Testing Agent with Pydantic Tool...")
    try:
        res = agent.run("Make a plan to clean the house")
        print("Result:", res.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_agent_structured_tool()
