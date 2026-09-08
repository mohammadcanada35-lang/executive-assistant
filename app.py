import streamlit as st
import requests

# إعداد الصفحة
st.set_page_config(
    page_title="AI Executive Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 المساعد التنفيذي الذكي")
st.write("مرحباً بك! أنا جاهز لمساعدتك في التخطيط، تنظيم الأولويات، وصياغة الرسائل.")

# قراءة مفتاح Groq من Secrets
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("⚠️ لم يتم العثور على GROQ_API_KEY في إعدادات Secrets.")
    st.stop()

# إدخال المستخدم
user_input = st.text_area(
    "ما الذي تحتاج إلى مساعدة فيه؟",
    placeholder="اكتب سؤالك هنا...",
    height=120
)

# زر الإرسال
if st.button("🚀 إرسال", use_container_width=True) and user_input.strip():

    with st.spinner("جاري التفكير..."):

        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": """
أنت مساعد تنفيذي ذكي ومحترف.

مهمتك:
- مساعدة المستخدم في التخطيط واتخاذ القرار.
- ترتيب الأولويات.
- كتابة وصياغة الرسائل باحتراف.
- تقديم إجابات واضحة ومباشرة.
- التحدث باللغة العربية بشكل طبيعي واحترافي.
- إذا كان السؤال يحتاج إلى خطوات، قدمها بشكل مرتب.
- لا تطيل بدون حاجة.
"""
                },
                {
                    "role": "user",
                    "content": user_input.strip()
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )

            # التحقق من نجاح الطلب
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get(
                        "message",
                        response.text
                    )
                except Exception:
                    error_message = response.text

                st.error(
                    f"❌ خطأ من Groq ({response.status_code}): "
                    f"{error_message}"
                )
                st.stop()

            # قراءة الرد
            res_data = response.json()

            reply = res_data["choices"][0]["message"]["content"]

            st.markdown("### 🤖 المساعد:")
            st.write(reply)

        except requests.exceptions.Timeout:
            st.error("⏱️ انتهت مهلة الاتصال. حاول مرة أخرى.")

        except requests.exceptions.RequestException as e:
            st.error(f"🌐 حدث خطأ في الاتصال: {str(e)}")

        except Exception as e:
            st.error(f"⚠️ حدث خطأ غير متوقع: {str(e)}")
