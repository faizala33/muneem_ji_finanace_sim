from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Important for security

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # --- 1. Get form data ---
        # Using request.form for standard text fields
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile')
        job = request.form.get('job')
        pan_card = request.form.get('pan_card')
        bank_name = request.form.get('bank_name')
        account_number = request.form.get('account_number')
        ifsc_code = request.form.get('ifsc_code')
        financial_goals = request.form.get('financial_goals')
        current_debt = request.form.get('current_debt')
        
        # Using request.form for numerical fields and converting them to the correct type
        try:
            balance_liquid = int(request.form.get('balance_liquid', 0))
            balance_gold = int(request.form.get('balance_gold', 0))
            balance_mutual_funds = int(request.form.get('balance_mutual_funds', 0))
        except ValueError:
            # Handle non-integer input gracefully
            balance_liquid, balance_gold, balance_mutual_funds = 0, 0, 0


        # --- 2. Construct the desired JSON payload ---
        json_data = {
            "profile_complete": True,
            "full_name": full_name,
            "mobile": mobile,
            "job": job,
            "pan_card": pan_card,
            "bank_name": bank_name,
            "account_number": account_number,
            "ifsc_code": ifsc_code,
            "financial_goals": financial_goals,
            "current_debt": current_debt,
            "balance_liquid": balance_liquid,
            "balance_gold": balance_gold,
            "balance_mutual_funds": balance_mutual_funds,
            "income_history": []
        }
        
        # --- 3. Return the JSON payload ---
        # This will send the data back as JSON to the client
        return jsonify(json_data)
        
    return render_template('form.html')

if __name__ == '__main__':
    # You'll need to install Flask first: pip install Flask
    app.run(debug=True)