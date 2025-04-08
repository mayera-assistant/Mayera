import os
import openai
import requests
from flask import Flask, request

app = Flask(__name__)

# Load from environment variables
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY


@app.route('/')
def home():
    return "Mayera Assistant is running!"


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return challenge
        return "Invalid verification token", 403

    if request.method == 'POST':
        data = request.get_json()
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            user_msg = message['text']['body']
            phone_number = message['from']

            ai_response = get_ai_response(user_msg)

            send_whatsapp_message(phone_number, ai_response)

        except Exception as e:
            print("Error:", e)
        return "OK", 200


def get_ai_response(user_message):
    try:
        prompt = f"""You are Mayera, a friendly Indian multilingual AI assistant. 
You can understand and reply in Hindi, Bengali, and English fluently. 
Respond like a human with emojis and warmth. Here's the user message:
{user_message}"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful multilingual assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        reply = response['choices'][0]['message']['content']
        return reply.strip()

    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, Mayera thoda busy hai abhi. Thodi der baad try karein!"


def send_whatsapp_message(recipient_id, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("WhatsApp response:", response.status_code, response.text)


if __name__ == "__main__":
    app.run(debug=True)
