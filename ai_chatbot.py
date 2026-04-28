"""
🤖 AI Employee Chatbot — "AI Agent as a Service"
Powered by Claude AI | Speaks Arabic, French & English
================================================
Install: pip install anthropic flask flask-cors
Run:     python ai_chatbot.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import json
import os

app = Flask(__name__)
CORS(app)

# ============================================================
# ⚙️ CONFIGURATION — Edit this per client!
# ============================================================

BUSINESS_PROFILES = {
    "demo": {
        "name": "Demo Business",
        "type": "general",
        "language": "auto",  # auto-detects Arabic/French/English
        "personality": "friendly and professional",
        "info": """
        - We are open 9am to 9pm every day
        - We offer free consultation
        - Contact: +212 600 000 000
        - Location: Tétouan, Morocco
        - We accept cash and bank transfer
        """,
        "services": ["Service 1", "Service 2", "Service 3"],
        "faq": {
            "price": "Our prices start from 100 DH. Contact us for a custom quote.",
            "delivery": "We deliver within 24-48 hours.",
            "contact": "Call us at +212 600 000 000 or WhatsApp us!"
        }
    },
    
    # Template for restaurant client
    "restaurant": {
        "name": "Restaurant Al Baraka",
        "type": "restaurant",
        "language": "auto",
        "personality": "warm, welcoming, and helpful",
        "info": """
        - Open daily 12pm to 11pm
        - Speciality: Moroccan & Mediterranean cuisine
        - Reservations: +212 650 000 000
        - Location: Avenue Mohammed V, Tétouan
        - Free delivery for orders over 150 DH
        - We cater for events and weddings
        """,
        "services": ["Dine-in", "Takeaway", "Delivery", "Event catering"],
        "faq": {
            "menu": "We serve tagine, couscous, grills, pasta and fresh salads.",
            "reservation": "Call or WhatsApp +212 650 000 000 to reserve your table.",
            "delivery": "Free delivery within 5km for orders above 150 DH."
        }
    },

    # Template for real estate client
    "realestate": {
        "name": "Immo Express",
        "type": "real estate",
        "language": "auto",
        "personality": "professional, trustworthy, and informative",
        "info": """
        - Available 7 days a week, 8am to 10pm
        - We handle buying, selling, and renting
        - Free property valuation
        - Office: Martil, Tétouan
        - WhatsApp: +212 660 000 000
        - We speak Arabic, French, and Spanish
        """,
        "services": ["Buy property", "Sell property", "Rent", "Investment advice"],
        "faq": {
            "price": "Prices vary by location. Contact us for current listings.",
            "process": "We handle all paperwork and legal procedures for you.",
            "languages": "We speak Arabic, French, Spanish and English."
        }
    }
}

# ============================================================
# 🤖 AI CHATBOT ENGINE
# ============================================================

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here"))

def get_system_prompt(business_id="demo"):
    """Generate system prompt for a specific business"""
    profile = BUSINESS_PROFILES.get(business_id, BUSINESS_PROFILES["demo"])
    
    return f"""You are an AI assistant for {profile['name']}, a {profile['type']} business.

Your personality: {profile['personality']}

Business Information:
{profile['info']}

Services offered: {', '.join(profile['services'])}

FAQ:
{json.dumps(profile['faq'], indent=2)}

IMPORTANT RULES:
1. ALWAYS detect the language the customer writes in (Arabic, French, or English) and reply in the SAME language
2. If they write in Arabic (including Darija), reply in Arabic
3. If they write in French, reply in French  
4. If they write in English, reply in English
5. Be helpful, friendly and concise (max 3-4 sentences per reply)
6. Always try to move toward a sale or booking
7. If you don't know something, say "Let me connect you with our team" and give the contact number
8. Never make up prices or information not given to you
9. End responses with a helpful follow-up question when appropriate

You are their 24/7 AI employee. Make every customer feel welcome and help them take action."""

def chat_with_ai(message, business_id="demo", conversation_history=None):
    """Send message to AI and get response"""
    if conversation_history is None:
        conversation_history = []
    
    # Add new message to history
    conversation_history.append({
        "role": "user",
        "content": message
    })
    
    try:
        response = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=500,
            system=get_system_prompt(business_id),
            messages=conversation_history
        )
        
        ai_reply = response.content[0].text
        
        # Add AI reply to history
        conversation_history.append({
            "role": "assistant", 
            "content": ai_reply
        })
        
        return ai_reply, conversation_history
        
    except Exception as e:
        return f"Sorry, I'm having a technical issue. Please call us directly! Error: {str(e)}", conversation_history

# ============================================================
# 🌐 API ENDPOINTS
# ============================================================

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    message = data.get('message', '')
    business_id = data.get('business_id', 'demo')
    history = data.get('history', [])
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    reply, updated_history = chat_with_ai(message, business_id, history)
    
    return jsonify({
        "reply": reply,
        "history": updated_history,
        "business_id": business_id
    })

@app.route('/businesses', methods=['GET'])
def get_businesses():
    """List all available business profiles"""
    return jsonify({
        "businesses": [
            {"id": k, "name": v["name"], "type": v["type"]}
            for k, v in BUSINESS_PROFILES.items()
        ]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "message": "AI Employee Bot is alive! 🤖"})

# ============================================================
# 🚀 RUN
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 AI EMPLOYEE CHATBOT SERVER")
    print("=" * 50)
    print("Server running at: http://localhost:5000")
    print("Chat endpoint: POST http://localhost:5000/chat")
    print("\nSet your API key:")
    print("  export ANTHROPIC_API_KEY=your-key-here")
    print("=" * 50)
    app.run(debug=True, port=5000)
