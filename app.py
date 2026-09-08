import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# مفتاح Groq المجاني (راح نخليه بمتغير بيئي أو تخلينه هنا مؤقتاً للتجربة)
GROQ_API_KEY = "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"


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>AI Executive Assistant</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #f4f7f6; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .chat-container { width: 100%; max-width: 600px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #333; }
        .chat-box { height: 350px; border: 1px solid #ddd; border-radius: 8px; padding: 10px; overflow-y: scroll; margin-bottom: 15px; background: #fafafa; }
        .message { margin-bottom: 10px; padding: 8px 12px; border-radius: 6px; line-height: 1.5; }
        .user { background: #dcf8c6; text-align: right; }
        .assistant { background: #e2e2e2; text-align: right; }
        .input-group { display: flex; gap: 10px; }
        input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="chat-container">
        <h2>مساعدك التنفيذي الذكي (Groq)</h2>
        <div class="chat-box" id="chatBox">
            <div class="message assistant">أهلاً بك! أنا جاهز لمساعدتك في التخطيط، الأولويات، وصياغة الرسائل. كيف أساعدك اليوم؟</div>
        </div>
        <div class="input-group">
            <input type="text" id="userInput" placeholder="اكتب رسالتك هنا..." onkeypress="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">إرسال</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const text = input.value.trim();
            if (!text) return;

            chatBox.innerHTML += `<div class="message user"><b>أنت:</b> ${text}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                chatBox.innerHTML += `<div class="message assistant"><b>المساعد:</b> ${data.reply}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (err) {
                chatBox.innerHTML += `<div class="message assistant" style="color:red;">حدث خطأ في الاتصال.</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "أنت مساعد تنفيذي ذكي ومحترف تساعد المستخدم في تنظيم مهامه باللغة العربية."},
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(GROQ_URL, json=payload, headers=headers)
        res_data = response.json()
        reply = res_data["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"عذراً، حدث خطأ في معالجة الطلب: {str(e)}"
        
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

