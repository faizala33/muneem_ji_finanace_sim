import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage # <--- NEW IMPORTS

load_dotenv() 

def load_db():
    try:
        with open('user_data.json', 'r') as f: return json.load(f)
    except FileNotFoundError: return {}

# --- 🛠️ TOOLS (Same as before) ---
@tool
def check_balance():
    """Returns wallet status."""
    data = load_db()
    total = data['balance_liquid'] + data['balance_gold'] + data['balance_mutual_funds']
    return f"Liquid Cash: ₹{data['balance_liquid']}, Gold: ₹{data['balance_gold']}, MF: ₹{data['balance_mutual_funds']}. Total: ₹{total}"

@tool
def deposit_income(amount: int, source: str = "Gig Work"):
    """Use when user EARNS money."""
    data = load_db()
    data['balance_liquid'] += amount
    if 'income_history' not in data: data['income_history'] = []
    data['income_history'].append({"amount": amount, "source": source, "date": "Today"})
    with open('user_data.json', 'w') as f: json.dump(data, f, indent=2)
    return f"SUCCESS: Added ₹{amount}. New Cash: ₹{data['balance_liquid']}"

@tool
def record_expense(amount: int, description: str):
    """Use when user SPENDS money or PAYS BILLS."""
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

@tool
def transfer_asset(amount: int, from_asset: str, to_asset: str):
    """
    Moves money between assets.
    Usage: "Move 5000 from Gold to Mutual Funds" or "Sell Gold".
    Valid assets: 'cash', 'gold', 'mutual_funds'.
    """
    data = load_db()
    
    # normalize inputs
    from_key = f"balance_{from_asset.lower().replace(' ', '_')}"
    to_key = f"balance_{to_asset.lower().replace(' ', '_')}"
    
    # Handle mappings (e.g. 'funds' -> 'mutual_funds')
    if 'gold' in from_asset.lower(): from_key = 'balance_gold'
    elif 'mutual' in from_asset.lower(): from_key = 'balance_mutual_funds'
    elif 'cash' in from_asset.lower(): from_key = 'balance_liquid'
    
    if 'gold' in to_asset.lower(): to_key = 'balance_gold'
    elif 'mutual' in to_asset.lower(): to_key = 'balance_mutual_funds'
    elif 'cash' in to_asset.lower(): to_key = 'balance_liquid'

    # Validation
    if data.get(from_key, 0) < amount:
        return f"ERROR: Insufficient {from_asset}. You only have ₹{data.get(from_key, 0)}."
    
    # Execute
    data[from_key] -= amount
    data[to_key] += amount
    
    with open('user_data.json', 'w') as f: json.dump(data, f, indent=2)
    return f"SUCCESS: Moved ₹{amount} from {from_asset} to {to_asset}."

# --- 🧠 BRAIN SETUP ---
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)
tools = [check_balance, deposit_income, record_expense, get_market_sentiment, invest_money, transfer_asset]

def get_system_prompt():
    data = load_db()
    user_name = data.get("full_name", "User")
    user_debt = data.get("current_debt", "None")
    
    return f"""
    You are 'MuneemAI', an Autonomous Wealth Manager for {user_name}.
    USER PROFILE: Debt: {user_debt}
    
    RULES:
    1. **Memory:** Use 'chat_history' to understand "Yes/No" answers.
       - If you asked "Should we pay EMI?" and user says "Yes", call 'record_expense'.
    2. **Tools:**
       - Income -> 'deposit_income'.
       - Spending -> 'record_expense'.
       - Investing -> 'invest_money'.
    3. **Strategy:** If user has Debt, advise paying it off.
    4. **MAX LENGTH:** Keep replies under 25 words.
    """

def process_user_message(user_input, chat_history):
    try:
        current_prompt = get_system_prompt()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", current_prompt),
            MessagesPlaceholder(variable_name="chat_history"), # <--- MEMORY SLOT
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Pass history to the agent
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        return response["output"]
    except Exception as e:
        return f"Agent Error: {str(e)}"