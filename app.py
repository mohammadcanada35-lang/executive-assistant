import streamlit as st
import requests

# ==================================================
# إعداد الصفحة
# ==================================================

st.set_page_config(
    page_title="AI Executive Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 المساعد التنفيذي الذكي")
st.caption("خطط بذكاء • رتّب أولوياتك • أنجز أكثر")

# ==================================================
# قراءة مفتاح Groq من Secrets
# ==================================================

if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ لم يتم العثور على GROQ_API_KEY.")
    st.info("أضف مفتاح Groq في Secrets باسم GROQ_API_KEY.")
    st.stop()

groq_api_key = st.secrets["GROQ_API_KEY"]

# ==================================================
# تعليمات المساعد
# ==================================================

SYSTEM_PROMPT = """
أنت مساعد تنفيذي ذكي ومحترف.

تحدث باللغة العربية بشكل طبيعي وواضح.
يمكنك استخدام اللهجة العراقية عندما يكون ذلك مناسباً.

مهامك الأساسية:

- مساعدة المستخدم في التخطيط.
- ترتيب الأولويات.
- تنظيم المهام.
- اتخاذ القرارات.
- إدارة الوقت.
- كتابة الرسائل والإيميلات باحتراف.
- تلخيص المعلومات.
- اقتراح حلول عملية.
- تحويل الأفكار إلى خطوات قابلة للتنفيذ.
- مساعدة المستخدم في العمل والمشاريع والتواصل.

أسلوبك:

- واضح ومباشر.
- عملي وذكي.
- لا تكرر الكلام.
- لا تطيل بدون حاجة.
- استخدم النقاط والترقيم عندما يكون ذلك مفيداً.
- إذا كان هناك أكثر من خيار، قارن بينها.
- إذا طلب المستخدم كتابة رسالة، أعطه رسالة جاهزة للنسخ والإرسال.
- إذا كان المستخدم يريد قراراً، وضح أفضل خيار والسبب.
- تعامل مع المستخدم كمساعد تنفيذي شخصي وليس مجرد روبوت أسئلة وأجوبة.

اللغة الأساسية: العربية.
"""

# ==================================================
# إنشاء ذاكرة المحادثة
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

# ==================================================
# عرض المحادثة السابقة
# ==================================================

for message in st.session_state.messages:

    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==================================================
# إدخال المستخدم
# ==================================================

user_input = st.chat_input(
    "اكتب طلبك هنا..."
)

# ==================================================
# إرسال الرسالة إلى Groq
# ==================================================

if user_input:

    # إضافة رسالة المستخدم
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # عرض رسالة المستخدم
    with st.chat_message("user"):
        st.markdown(user_input)

    # إنشاء رد المساعد
    with st.chat_message("assistant"):

        with st.spinner("جاري التفكير..."):

            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": st.session_state.messages,
                "temperature": 0.7,
                "max_tokens": 4000
            }

            try:

                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                # ==========================================
                # التحقق من الاستجابة
                # ==========================================

                if response.status_code != 200:

                    try:
                        error_data = response.json()

                        error_message = (
                            error_data
                            .get("error", {})
                            .get("message", response.text)
                        )

                    except Exception:
                        error_message = response.text

                    st.error(
                        f"❌ خطأ من Groq "
                        f"({response.status_code}): "
                        f"{error_message}"
                    )

                else:

                    data = response.json()

                    # استخراج الرد
                    reply = (
                        data["choices"][0]
                        ["message"]["content"]
                    )

                    # عرض الرد
                    st.markdown(reply)

                    # حفظ الرد في الذاكرة
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": reply
                        }
                    )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ انتهت مهلة الاتصال بـ Groq. "
                    "حاول مرة أخرى."
                )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"🌐 حدث خطأ في الاتصال:\n\n{str(e)}"
                )

            except KeyError:

                st.error(
                    "⚠️ Groq أرسل استجابة غير متوقعة."
                )

            except Exception as e:

                st.error(
                    f"⚠️ حدث خطأ غير متوقع:\n\n{str(e)}"
                )

# ==================================================
# الشريط السفلي
# ==================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.caption("🧠 يعمل بواسطة Groq")

with col2:
    if st.button("🗑️ مسح المحادثة", use_container_width=True):

        st.session_state.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        st.rerun()
