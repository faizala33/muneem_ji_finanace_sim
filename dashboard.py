import streamlit as st
import json
import pandas as pd
import plotly.express as px
import requests
import time
from streamlit_option_menu import option_menu

# --- PAGE CONFIG ---
st.set_page_config(page_title="MuneemAI", page_icon="💎", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp {background-color: #0f172a;}
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .pending-box {
        background-color: #451a03;
        color: #fbbf24;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #d97706;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
    }
    input {background-color: #334155 !important; color: white !important;}
    </style>
""", unsafe_allow_html=True)

def load_data():
    try:
        with open('user_data.json', 'r') as f: return json.load(f)
    except: return None

def save_data(data):
    with open('user_data.json', 'w') as f: json.dump(data, f, indent=2)

data = load_data()

# ==========================================
# 🛑 STATE 1: FULL KYC ONBOARDING
# ==========================================
if not data or not data.get("profile_complete", False):
    st.title("🚀 Initialize MuneemAI")
    st.markdown("### complete your KYC to activate Financial Autopilot.")
    
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Personal Info")
            name = st.text_input("Full Name", placeholder="Rahul Verma")
            mobile = st.text_input("Mobile Number", placeholder="9876543210")
            job = st.text_input("Occupation", placeholder="Zomato Rider")
            pan = st.text_input("PAN Card", placeholder="ABCDE1234F")

        with col2:
            st.markdown("#### 🏦 Bank Details")
            bank = st.text_input("Bank Name", placeholder="HDFC Bank")
            acc = st.text_input("Account Number")
            ifsc = st.text_input("IFSC Code")
        
        st.markdown("---")
        c3, c4 = st.columns(2)
        with c3:
            goal = st.text_area("Financial Goals", placeholder="Buy a bike, Save for wedding")
        with c4:
            debt = st.text_area("Current Debt/EMI", placeholder="Laptop EMI ₹2000")

        # Hidden defaults for logic
        if st.form_submit_button("✅ Create Account"):
            data.update({
                "profile_complete": True,
                "full_name": name,
                "mobile": mobile,
                "job": job,
                "pan_card": pan,
                "bank_name": bank,
                "account_number": acc,
                "ifsc_code": ifsc,
                "financial_goals": goal,
                "current_debt": debt,
                "balance_liquid": 1000, # Starting bonus
                "balance_gold": 0,
                "balance_mutual_funds": 0,
                "alerts": ["🎉 Account Created Successfully"],
                "pending_transaction": None
            })
            save_data(data)
          # 2. 🚀 TRIGGER WELCOME MESSAGE (The New Magic)
            try:
                # Send request to FastAPI (running on localhost)
                requests.post("http://127.0.0.1:8000/trigger-welcome", 
                              json={"mobile": mobile, "name": name})
                st.toast("📲 Welcome Message Sent to WhatsApp!")
            except Exception as e:
                st.error(f"Could not send WhatsApp: {e}")

            st.success("KYC Verified! Redirecting...")
            time.sleep(2)
            st.rerun()

# ==========================================
# 🟢 STATE 2: THE MAIN DASHBOARD
# ==========================================
else:
    with st.sidebar:
        # Profile Card
        st.write(f"### 👤 {data['full_name']}")
        st.caption(f"{data['job']} | {data['bank_name']}")
        st.caption(f"Acct: **{data['account_number'][-4:]}**")
        
        st.markdown("---")
        
        selected = option_menu("Menu", ["Overview", "Wallet", "Settings"], 
            icons=['speedometer', 'wallet', 'gear'], menu_icon="cast", default_index=0,
            styles={"nav-link-selected": {"background-color": "#3b82f6"}})
        
        st.markdown("---")
        st.markdown("### 🔔 Notifications")
        if data.get('alerts'):
            for alert in data['alerts'][:5]:
                st.info(alert)
            
        if st.button("🔴 Factory Reset"):
            save_data({"profile_complete": False})
            st.rerun()

    # --- PENDING APPROVAL ALERT ---
    if data.get('pending_transaction'):
        pt = data['pending_transaction']
        st.markdown(f"""
        <div class="pending-box">
            ⚠️ ACTION REQUIRED: Approve Investment of ₹{pt['amount']} in {pt['asset'].upper()}?<br>
            Reply 'YES' on WhatsApp to confirm.
        </div>
        """, unsafe_allow_html=True)

    # --- VIEW: OVERVIEW ---
    if selected == "Overview":
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Liquid Cash", f"₹{data['balance_liquid']}")
        k2.metric("Gold", f"₹{data['balance_gold']}")
        k3.metric("Mutual Funds", f"₹{data['balance_mutual_funds']}")
        k4.metric("Net Worth", f"₹{data['balance_liquid'] + data['balance_gold'] + data['balance_mutual_funds']}")

        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Income Trend")
            if data.get('income_history'):
                df = pd.DataFrame(data['income_history'])
                fig = px.area(df, x=df.index, y="amount", color_discrete_sequence=['#3b82f6'])
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig, use_container_width=True, key="income_chart")
            else:
                st.info("No income data yet.")

        with c2:
            st.subheader("Allocation")
            df_pie = pd.DataFrame({
                "Asset": ["Cash", "Gold", "Funds"],
                "Amount": [data['balance_liquid'], data['balance_gold'], data['balance_mutual_funds']]
            })
            fig2 = px.pie(df_pie, values='Amount', names='Asset', hole=0.7, 
                         color_discrete_sequence=['#3b82f6', '#f59e0b', '#8b5cf6'])
            fig2.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True, key="pie_chart")

    # --- VIEW: SETTINGS ---
    elif selected == "Settings":
        st.header("Profile Settings")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Full Name", value=data['full_name'], disabled=True)
            st.text_input("Mobile", value=data['mobile'], disabled=True)
            st.text_input("PAN Card", value=data['pan_card'], disabled=True)
        with c2:
            st.text_input("Bank", value=data['bank_name'], disabled=True)
            st.text_input("IFSC", value=data['ifsc_code'], disabled=True)
            st.text_input("Goal", value=data['financial_goals'], disabled=True)

    time.sleep(2)
    st.rerun()