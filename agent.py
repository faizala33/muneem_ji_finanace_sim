import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. Load Google API Key
load_dotenv() 

# 2. Database Loader (MUST BE DEFINED FIRST)
def load_db():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default structure matching the new onboarding flow
        return {
            "profile_complete": False,
            "full_name": "User",
            "balance_liquid": 0, 
            "balance_gold": 0, 
            "balance_mutual_funds": 0,
            "current_debt": "",
            "financial_goals": ""
        }

# --- 🛠️ THE TOOLS ---

@tool
def check_balance():
    """
    Returns the current wallet status.
    Use this when user asks: "How much do I have?", "Can I afford X?", "Balance?".
    """
    data = load_db()
    total = data['balance_liquid'] + data['balance_gold'] + data['balance_mutual_funds']
    return f"Liquid Cash: ₹{data['balance_liquid']}, Gold: ₹{data['balance_gold']}, Mutual Funds: ₹{data['balance_mutual_funds']}. Total Net Worth: ₹{total}"

@tool
def deposit_income(amount: int, source: str = "Gig Work"):
    """
    Call this ONLY when the user explicitly says they EARNED, MADE, or RECEIVED money.
    Examples: "I made 500", "Got salary", "Received payment".
    
    ⚠️ CRITICAL: DO NOT call this if the user is stating a PRICE, COST, or BUDGET.
    Example: "Bike is 2 lakh" -> DO NOT CALL THIS.
    """
    data = load_db()
    data['balance_liquid'] += amount
    
    # Log it
    if 'income_history' not in data: data['income_history'] = []
    data['income_history'].append({"amount": amount, "source": source, "date": "Today"})
    
    with open('user_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    return f"SUCCESS: Added ₹{amount} to wallet. Current Cash: ₹{data['balance_liquid']}"

@tool
def get_market_sentiment():
    """
    Returns current market trends. Use this to decide WHERE to invest.
    """
    return "Market Status: Gold is Stable (Safe Haven). Mutual Funds are Volatile but have High Return."

@tool
def invest_money(amount: int, asset_class: str):
    """
    Moves money from Liquid Cash to an Asset.
    asset_class must be either 'gold' or 'mutual_funds'.
    """
    data = load_db()
    
    if data['balance_liquid'] < amount:
        return f"ERROR: Insufficient funds. Wallet only has ₹{data['balance_liquid']}."
    
    data['balance_liquid'] -= amount
    
    if "gold" in asset_class.lower():
        data['balance_gold'] += amount
    elif "mutual" in asset_class.lower() or "fund" in asset_class.lower():
        data['balance_mutual_funds'] += amount
    
    with open('user_data.json', 'w') as f:
        json.dump(data, f, indent=2)
        
    return f"SUCCESS: Invested ₹{amount} in {asset_class}."

# --- 🧠 THE BRAIN & DYNAMIC PROMPT ---

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0.3
)

tools = [check_balance, deposit_income, get_market_sentiment, invest_money]

def get_system_prompt():
    """Generates a prompt based on the User's Profile in the DB"""
    data = load_db()
    
    # Read User Profile from JSON
    user_name = data.get("full_name", "User")
    user_job = data.get("job", "Gig Worker")
    user_goals = data.get("financial_goals", "Financial Stability")
    user_debt = data.get("current_debt", "None")
    
    prompt = f"""
    You are 'LiquidAI', an Autonomous Wealth Manager for {user_name}.
    
    USER PROFILE:
    - Job: {user_job}
    - Financial Goals: {user_goals}
    - Current Debt/EMI: {user_debt}
    
    YOUR RULES:
    1. **Context:** Always remember their job, debt, and goals when replying.
    2. **Income vs Cost:** - "I made 5000" -> Call 'deposit_income'.
       - "Bike costs 5000" -> Call 'check_balance' to see if they can afford it.
    3. **Investing:** - If they have Debt ({user_debt}), suggest paying that off first.
       - Otherwise, invest towards their Goal ({user_goals}).
    
    Tone: Professional but friendly financial advisor.
    """
    return prompt

def process_user_message(user_input):
    try:
        # 1. Build the Prompt with latest User Data
        current_system_prompt = get_system_prompt()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", current_system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # 2. Create Agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # 3. Run
        response = agent_executor.invoke({"input": user_input})
        return response["output"]
    except Exception as e:
        return f"Agent Error: {str(e)}"