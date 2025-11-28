import streamlit as st
import json
import pandas as pd
import plotly.express as px
import time

# --- CONFIG ---
st.set_page_config(page_title="MuneemAI | Onboarding", page_icon="🤖", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp {background-color: #0e1117;}
    div.stMetric {background-color: #1f2937; padding: 10px; border-radius: 5px; border: 1px solid #374151;}
    input {background-color: #1f2937; color: white;}
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADER ---
def load_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except:
        return None

def save_data(data):
    with open('user_data.json', 'w') as f:
        json.dump(data, f, indent=2)

data = load_data()

# ==========================================
# 🛑 STATE 1: USER ONBOARDING (THE FORM)
# ==========================================
if not data or not data.get("profile_complete", False):
    st.title("🚀 Welcome to MuneemAI")
    st.markdown("### Let's set up your Financial Autopilot.")
    st.info("Please fill in your details to activate the AI Agent.")

    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Personal Details")
            full_name = st.text_input("Full Name", placeholder="e.g. Rahul Verma")
            mobile = st.text_input("Mobile Number", placeholder="+91 9876543210")
            job = st.text_input("Occupation/Gig", placeholder="e.g. Zomato Rider, Freelancer")
            pan = st.text_input("PAN Card Number")

        with col2:
            st.markdown("#### 🏦 Banking Details")
            bank_name = st.text_input("Bank Name", placeholder="e.g. HDFC Bank")
            ac_no = st.text_input("Account Number")
            ifsc = st.text_input("IFSC Code")
            
        st.markdown("---")
        st.markdown("#### 🎯 Financial Snapshot")
        c3, c4 = st.columns(2)
        with c3:
            goals = st.text_area("What are your Financial Goals?", placeholder="e.g. Buy a Bike in 6 months, Save for sister's wedding")
        with c4:
            debt = st.text_area("Current Debts / EMIs?", placeholder="e.g. ₹5000 friend loan, ₹2000 Phone EMI")
            
        # Initial Balance Injection
        initial_cash = st.number_input("Current Cash in Hand (₹)", min_value=0, value=1000)

        submitted = st.form_submit_button("🚀 Activate My Agent")
        
        if submitted:
            if full_name and mobile:
                # Update Data Object
                data["profile_complete"] = True
                data["full_name"] = full_name
                data["mobile"] = mobile
                data["job"] = job
                data["pan_card"] = pan
                data["bank_name"] = bank_name
                data["account_number"] = ac_no
                data["ifsc_code"] = ifsc
                data["financial_goals"] = goals
                data["current_debt"] = debt
                data["balance_liquid"] = initial_cash
                
                save_data(data)
                st.success("Profile Created! Redirecting...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Please fill in at least Name and Mobile.")

# ==========================================
# 🟢 STATE 2: THE MAIN DASHBOARD
# ==========================================
else:
    # Sidebar for Profile View
    with st.sidebar:
        st.header(f"👤 {data['full_name']}")
        st.caption(f"{data['job']} | {data['bank_name']}")
        st.markdown("---")
        st.write(f"**📱 Mobile:** {data['mobile']}")
        st.write(f"**🎯 Goals:** {data['financial_goals']}")
        st.write(f"**💸 Debt:** {data['current_debt']}")
        st.markdown("---")
        
        if st.button("🔴 Reset / Edit Profile"):
            # Wipe data to trigger form again
            empty_data = {"profile_complete": False, "balance_liquid": 0, "balance_gold": 0, "balance_mutual_funds": 0}
            save_data(empty_data)
            st.rerun()

    # Main Area
    st.title(f"🤖 MuneemAI Monitor")

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💸 Cash", f"₹{data['balance_liquid']}")
    k2.metric("🥇 Gold", f"₹{data['balance_gold']}")
    k3.metric("📈 Mutual Funds", f"₹{data['balance_mutual_funds']}")
    
    net_worth = data['balance_liquid'] + data['balance_gold'] + data['balance_mutual_funds']
    k4.metric("💰 Net Worth", f"₹{net_worth}")

    # Charts
    c1, c2 = st.columns([2,1])
    with c1:
        st.subheader("Asset Allocation")
        df = pd.DataFrame({
            "Asset": ["Cash", "Gold", "Mutual Funds"],
            "Amount": [data['balance_liquid'], data['balance_gold'], data['balance_mutual_funds']]
        })
        fig = px.pie(df, values='Amount', names='Asset', hole=0.5, 
                     color_discrete_sequence=['#3b82f6', '#f59e0b', '#8b5cf6'], template="plotly_dark")
        st.plotly_chart(fig, key="pie_chart", use_container_width=True)

    with c2:
        st.subheader("Financial Health")
        if data['current_debt']:
            st.warning(f"⚠️ Active Debt: {data['current_debt']}")
        else:
            st.success("✅ Debt Free")
            
        st.info(f"🎯 Goal: {data['financial_goals']}")

    # Auto Refresh
    time.sleep(2)
    st.rerun()