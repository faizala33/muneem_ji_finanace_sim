import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

load_dotenv() 

def load_db():
    try:
        with open('user_data.json', 'r') as f: return json.load(f)
    except FileNotFoundError: return {}

# --- 🛠️ ALL TOOLS (Old + New) ---

@tool
def check_balance():
    """Returns current wallet status."""
    data = load_db()
    total = data['balance_liquid'] + data['balance_gold'] + data['balance_mutual_funds']
    return f"Liquid Cash: ₹{data['balance_liquid']}, Gold: ₹{data['balance_gold']}, MF: ₹{data['balance_mutual_funds']}. Total: ₹{total}"

@tool
def deposit_income(amount: int, source: str = "Gig Work"):
    """
    Call ONLY when user EARNS money.
    Example: "I made 500", "Got salary". 
    NOT for "I want to buy X".
    """
    data = load_db()
    data['balance_liquid'] += amount
    if 'income_history' not in data: data['income_history'] = []
    data['income_history'].append({"amount": amount, "source": source, "date": "Today"})
    with open('user_data.json', 'w') as f: json.dump(data, f, indent=2)
    return f"SUCCESS: Added ₹{amount}. New Cash: ₹{data['balance_liquid']}"

@tool
def record_expense(amount: int, description: str):
    """
    Call when user SPENDS money, pays BILLS, or pays EMI.
    Example: "I spent 500", "Pay my EMI", "Clear debt".
    """
    data = load_db()
    
    if data['balance_liquid'] < amount:
        return f"ERROR: Cannot pay ₹{amount}. Cash Balance is only ₹{data['balance_liquid']}."
    
    data['balance_liquid'] -= amount
    
    with open('user_data.json', 'w') as f: json.dump(data, f, indent=2)
    return f"SUCCESS: Paid ₹{amount} for {description}. Remaining Cash: ₹{data['balance_liquid']}"

@tool
def get_market_sentiment():
    """Returns market trends."""
    return "Market Status: Gold is Stable. Mutual Funds are Volatile but High Return."

@tool
def invest_money(amount: int, asset_class: str):
    """Moves money from Cash to Asset."""
    data = load_db()
    if data['balance_liquid'] < amount:
        return f"ERROR: Insufficient funds. Cash: ₹{data['balance_liquid']}."
    
    data['balance_liquid'] -= amount
    if "gold" in asset_class.lower(): data['balance_gold'] += amount
    elif "mutual" in asset_class.lower(): data['balance_mutual_funds'] += amount
    
    with open('user_data.json', 'w') as f: json.dump(data, f, indent=2)
    return f"SUCCESS: Invested ₹{amount} in {asset_class}."

# --- 🧠 THE BRAIN ---

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)

# Updated list with ALL 5 tools
tools = [check_balance, deposit_income, record_expense, get_market_sentiment, invest_money]

def get_system_prompt():
    data = load_db()
    # Profile Data
    user_name = data.get("full_name", "User")
    user_debt = data.get("current_debt", "None")
    user_goal = data.get("financial_goals", "Financial Stability")
    
    # Financial State (For AI Context)
    cash = data.get('balance_liquid', 0)
    gold = data.get('balance_gold', 0)
    
    return f"""
    You are 'MuneemAI', an Autonomous Wealth Manager for {user_name}.
    
    📊 CURRENT FINANCIAL STATE:
    - Cash in Hand: ₹{cash}
    - Debt/EMI: {user_debt}
    - Main Goal: {user_goal}
    
    🛑 CRITICAL RULES (MECHANICS):
    1. **Context Continuity:** - If user says a bare number (e.g., "50000"), assume it refers to the PREVIOUS topic (Gold, Income, or Debt payment).
       - If user says "Yes" to your suggestion, EXECUTE it immediately using the tool.
    2. **Tool Mapping:**
       - "I made/earned..." -> Call 'deposit_income'.
       - "I spent...", "Pay EMI" -> Call 'record_expense'.
       - "Invest..." -> Call 'invest_money'.
    
    🧠 COACHING STRATEGY (BEHAVIOR):
    1. **After Deposit (The Logic):** - If 'deposit_income' is successful, look at the new Cash Balance.
       - IF Cash > 5000 AND User has Debt ({user_debt}): Suggest paying off the debt immediately.
       - IF Cash > 5000 AND Debt is Low: Suggest investing in Gold/Funds for their goal ({user_goal}).
       - IF Cash < 2000: Advise caution and saving.
    
    2. **After Expense:**
       - Confirm the remaining balance. If low (<1000), warn the user.

    3. **Tone:**
       - Be proactive. Don't just say "Done." Say "Done. Now, given you have extra cash, should we pay your EMI?"
    """

def process_user_message(user_input):
    try:
        current_prompt = get_system_prompt()
        prompt = ChatPromptTemplate.from_messages([
            ("system", current_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        response = agent_executor.invoke({"input": user_input})
        return response["output"]
    except Exception as e:
        return f"Agent Error: {str(e)}"