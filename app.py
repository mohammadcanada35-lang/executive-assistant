import streamlit as st
import requests

st.set_page_config(page_title="المساعد التنفيذي الذكي", page_icon="🤖", layout="centered")

st.title("🤖 المساعد التنفيذي الذكي")
st.write("مرحباً بك! أنا مساعدك الذكي للتخطيط وتنظيم المهام.")

groq_api_key = "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"

user_input = st.text_input("اكتب سؤالك هنا:")

if st.button("إرسال") and user_input:
    with st.spinner("جاري التفكير..."):
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "أنت مساعد تنفيذي ذكي ومحترف."},
                {"role": "user", "content": user_input}
            ]
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        reply = response.json()["choices"][0]["message"]["content"]
        
        st.success(reply)
        
        # نطق الجواب صوتياً بشكل تلقائي
        st.markdown(f"""
            <script>
                var utterance = new SpeechSynthesisUtterance("{reply}");
                utterance.lang = 'ar-SA';
                window.speechSynthesis.speak(utterance);
            </script>
        """, unsafe_allow_html=True)

