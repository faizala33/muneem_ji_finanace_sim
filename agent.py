import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv() 

def load_db():
    try:
        with open('user_data.json', 'r') as f: return json.load(f)
    except FileNotFoundError: return {}

# --- 🛠️ TOOLS ---

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
    
    # Alert
    if 'alerts' not in data: data['alerts'] = []
    data['alerts'].insert(0, f"💰 Credit: ₹{amount} from {source}")
    
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

# --- 🚨 SAFETY TOOLS ---

@tool
def propose_investment(amount: int, asset_class: str):
    """
    Call this when user wants to INVEST. 
    This does NOT move money. It creates a pending request.
    """
    data = load_db()
    if data['balance_liquid'] < amount:
        return f"ERROR: Insufficient funds. Cash: ₹{data['balance_liquid']}."
    
    # Create Pending Transaction
    data['pending_transaction'] = {"amount": amount, "asset": asset_class}
    
    with open('user_data.json', 'w') as f: json.dump(data, f, indent=2)
    return f"PENDING: Investment of ₹{amount} in {asset_class} requires approval. Ask user to confirm."

@tool
def confirm_transaction():
    """
    Call this ONLY if user says 'YES' or 'Confirm'.
    Executes the pending transaction.
    """
    data = load_db()
    pending = data.get('pending_transaction')
    
    if not pending:
        return "No pending transactions to confirm."
    
    amount = pending['amount']
    asset = pending['asset']
    
    data['balance_liquid'] -= amount
    if "gold" in asset.lower(): data['balance_gold'] += amount
    elif "mutual" in asset.lower(): data['balance_mutual_funds'] += amount
    
    # Clear Pending & Alert
    data['pending_transaction'] = None
    if 'alerts' not in data: data['alerts'] = []
    data['alerts'].insert(0, f"✅ Invested ₹{amount} in {asset}")
    
    with open('user_data.json', 'w') as f: json.dump(data, f, indent=2)
    return f"SUCCESS: Invested ₹{amount} in {asset}."

@tool
def transfer_asset(amount: int, from_asset: str, to_asset: str):
    """Moves money between assets."""
    data = load_db()
    return "Rebalancing requires manual approval for this demo."

# --- 🧠 BRAIN SETUP ---

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)

# UPDATED TOOL LIST
tools = [check_balance, deposit_income, record_expense, get_market_sentiment, propose_investment, confirm_transaction, transfer_asset]

def get_system_prompt():
    data = load_db()
    user_name = data.get("full_name", "User")
    user_debt = data.get("current_debt", "None")
    
    # --- THE FIX IS HERE ---
    # We construct a clean string without dictionary braces
    pending = data.get("pending_transaction")
    if pending:
        pending_msg = f"⚠️ PENDING APPROVAL: Invest {pending['amount']} in {pending['asset']}"
    else:
        pending_msg = "No pending actions."
    # -----------------------
    
    return f"""
    You are 'MuneemAI', an Autonomous Wealth Manager for {user_name}.
    USER PROFILE: Debt: {user_debt}
    CURRENT STATE: {pending_msg}
    
    RULES:
    1. **Context Continuity:** - If user says "Yes" / "Confirm", and there is a PENDING action, call 'confirm_transaction'.
       - If user says "No", say "Cancelled".
    
    2. **Handling Money:**
       - **INCOME:** "I made 500" -> Call 'deposit_income'.
       - **EXPENSE:** "I spent 500", "Pay EMI" -> Call 'record_expense'.
       - **INVESTING (CRITICAL):** "Invest 500" -> Call 'propose_investment'. DO NOT call any other tool for investing.
        - **Rebalancing:** "Move Gold to Funds" -> Call 'transfer_asset'.

    3. **Strategy:** If user has Debt, warn them. But if they insist on investing, call 'propose_investment'.
    
    4. **MAX LENGTH:** Keep replies under 25 words.
    """

def process_user_message(user_input, chat_history):
    try:
        current_prompt = get_system_prompt()
        prompt = ChatPromptTemplate.from_messages([
            ("system", current_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        return response["output"]
    except Exception as e:
        return f"Agent Error: {str(e)}"