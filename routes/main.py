from flask import render_template, request, jsonify, session
from . import main_bp
from config import Config
import requests

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        data = response.json()
        return data['ip']
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None

@main_bp.route('/authenticate', methods=['POST'])
def authenticate():
    user_ip = request.json.get('ip')
    print(f"Visitor: {user_ip}")
    
    if not Config.AUTHENTICATION:
        session['authorized'] = True
        return jsonify({"authorized": True})
    
    allowed_ip = get_public_ip()
    if user_ip == allowed_ip:
        session['authorized'] = True
        return jsonify({"authorized": True})
    else:
        return jsonify({"authorized": False})

def get_balance(api_key, organization_id):
    url = 'https://api.openai.com/v1/dashboard/billing/credit_grants'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Openai-Organization': f'{organization_id}'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        balance = data.get('total_available', 0)
        return balance
    except requests.RequestException as e:
        print(f"Request to OpenAI API failed: {e}")
        return None

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    balance = get_balance(Config.OPENAI_SESSION_KEY, Config.OPENAI_ORGANIZATION)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"balance": balance})

    return render_template('index.html', balance=balance)