import streamlit as st
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(
    page_title="المساعد التنفيذي",
    page_icon="📧"
)

# قراءة تعليمات المساعد من ملف system_prompt.md
with open("system_prompt.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# إعداد Gemini API
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# إنشاء النموذج
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=system_prompt
)

# عنوان التطبيق
st.title("المساعد التنفيذي")

# إنشاء المحادثة
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# حفظ الرسائل
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# مربع إدخال المستخدم
user_input = st.chat_input("اكتب رسالتك هنا...")

if user_input:
    # إضافة رسالة المستخدم
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # عرض رسالة المستخدم
    with st.chat_message("user"):
        st.write(user_input)

    # إرسال الرسالة إلى Gemini
    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير..."):
            try:
                response = st.session_state.chat.send_message(user_input)
                assistant_reply = response.text

                # عرض رد المساعد
                st.write(assistant_reply)

                # حفظ رد المساعد
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_reply
                })

            except Exception as e:
                st.error(f"حدث خطأ: {e}")
