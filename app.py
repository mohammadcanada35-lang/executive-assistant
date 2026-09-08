import streamlit as st
import requests
import streamlit.components.v1 as components


# =========================================================
# إعداد الصفحة
# =========================================================

st.set_page_config(
    page_title="المساعد التنفيذي الذكي",
    page_icon="🤖",
    layout="centered"
)


# =========================================================
# التصميم
# =========================================================

st.markdown("""
<style>

.main {
    direction: rtl;
    text-align: right;
}

h1 {
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #777;
    font-size: 18px;
    margin-bottom: 30px;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 48px;
    font-size: 17px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# العنوان
# =========================================================

st.title("🤖 المساعد التنفيذي الذكي")

st.markdown(
    '<div class="subtitle">'
    'خطط بذكاء، نظم أعمالك، واتخذ قراراتك بثقة.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# قراءة مفتاح Groq من Secrets
# =========================================================

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error(
        "❌ مفتاح Groq غير موجود.\n\n"
        "أضفه داخل Streamlit Secrets باسم GROQ_API_KEY"
    )
    st.stop()


# =========================================================
# ذاكرة المحادثة
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# عرض المحادثة السابقة
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])

    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(message["content"])


# =========================================================
# إدخال صوتي
# =========================================================

st.markdown("### 🎙️ التحدث مع المساعد")

components.html(
    """
    <div style="
        direction: rtl;
        text-align: center;
        padding: 10px;
    ">

        <button
            onclick="startListening()"
            style="
                background:#222;
                color:white;
                border:none;
                border-radius:12px;
                padding:14px 25px;
                font-size:18px;
                cursor:pointer;
            "
        >
            🎙️ اضغط وتكلم
        </button>

        <p id="status" style="margin-top:12px;">
            اضغط على الزر وتكلم باللهجة العراقية
        </p>

        <textarea
            id="result"
            placeholder="الكلام الذي تقوله سيظهر هنا..."
            style="
                width:100%;
                min-height:100px;
                padding:12px;
                border-radius:10px;
                border:1px solid #ccc;
                font-size:16px;
                direction:rtl;
            "
        ></textarea>

        <script>

        function startListening() {

            const SpeechRecognition =
                window.SpeechRecognition ||
                window.webkitSpeechRecognition;

            if (!SpeechRecognition) {

                document.getElementById("status").innerText =
                    "❌ المتصفح لا يدعم التعرف على الصوت. جرّب Google Chrome.";

                return;
            }

            const recognition = new SpeechRecognition();

            recognition.lang = "ar-IQ";

            recognition.continuous = false;

            recognition.interimResults = false;

            document.getElementById("status").innerText =
                "🎙️ أسمعك الآن... احچي براحتك";

            recognition.start();

            recognition.onresult = function(event) {

                const transcript =
                    event.results[0][0].transcript;

                document.getElementById("result").value =
                    transcript;

                document.getElementById("status").innerText =
                    "✅ تم التعرف على الكلام";

            };

            recognition.onerror = function(event) {

                document.getElementById("status").innerText =
                    "❌ حدث خطأ في المايكروفون: " +
                    event.error;

            };

            recognition.onend = function() {

                if (
                    document.getElementById("status").innerText
                    .includes("أسمعك")
                ) {
                    document.getElementById("status").innerText =
                        "انتهى التسجيل";
                }

            };

        }

        </script>

    </div>
    """,
    height=280
)


# =========================================================
# الإدخال الكتابي
# =========================================================

user_input = st.text_area(
    "✍️ أو اكتب سؤالك هنا:",
    placeholder="مثلاً: رتب لي مهامي اليوم حسب الأولوية...",
    height=120
)


# =========================================================
# زر الإرسال
# =========================================================

if st.button("🚀 إرسال إلى المساعد"):

    if not user_input.strip():

        st.warning("⚠️ اكتب سؤالًا أو استخدم المايكروفون أولاً.")

    else:

        # إضافة رسالة المستخدم
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # =================================================
        # الاتصال بـ Groq
        # =================================================

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

تحدث باللغة العربية.

عندما يتحدث المستخدم باللهجة العراقية،
افهم اللهجة العراقية جيداً ورد عليه بطريقة
طبيعية ومفهومة وقريبة من اللهجة العراقية.

كن عملياً ومختصراً وواضحاً.

ساعد المستخدم في:
- التخطيط
- تنظيم المهام
- إدارة الوقت
- اتخاذ القرارات
- كتابة الرسائل
- تحليل المشاكل
- ترتيب الأولويات
- تطوير الأعمال

لا تستخدم لغة معقدة بدون داعٍ.

إذا كان السؤال يحتاج خطوات،
اعرضها بشكل مرتب ومرقم.

إذا كان المستخدم عراقي ويتحدث باللهجة العراقية،
يمكنك الرد باللهجة العراقية بشكل طبيعي.
"""
                }

            ] + st.session_state.messages,

            "temperature": 0.7,

            "max_tokens": 2000
        }


        # =================================================
        # إرسال الطلب
        # =================================================

        with st.spinner("🤖 المساعد يفكر..."):

            try:

                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60
                )

                # التأكد من نجاح الطلب
                response.raise_for_status()

                res_data = response.json()

                # =================================================
                # استخراج الرد
                # =================================================

                if "choices" in res_data:

                    reply = (
                        res_data["choices"][0]
                        ["message"]
                        ["content"]
                    )

                    # حفظ الرد
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply
                    })

                    # عرض الرد
                    with st.chat_message("assistant"):

                        st.write(reply)

                    # =================================================
                    # قراءة الرد صوتياً
                    # =================================================

                    safe_reply = (
                        reply
                        .replace("\\", "\\\\")
                        .replace("`", "\\`")
                        .replace("${", "\\${")
                    )

                    components.html(
                        f"""
                        <script>

                        const text = `{safe_reply}`;

                        const utterance =
                            new SpeechSynthesisUtterance(text);

                        /*
                        العربية العراقية تعتمد على
                        الأصوات العربية المتوفرة بالجهاز.
                        */

                        utterance.lang = "ar-IQ";

                        utterance.rate = 0.9;

                        utterance.pitch = 1.0;

                        window.speechSynthesis.cancel();

                        window.speechSynthesis.speak(
                            utterance
                        );

                        </script>
                        """,
                        height=0
                    )

                else:

                    st.error(
                        "❌ لم يصل رد صحيح من Groq:"
                    )

                    st.json(res_data)

            except requests.exceptions.HTTPError:

                st.error(
                    "❌ Groq رفض الطلب."
                )

                try:
                    st.json(response.json())
                except Exception:
                    st.write(response.text)

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ انتهى وقت الاتصال بـ Groq. "
                    "حاول مرة ثانية."
                )

            except Exception as e:

                st.error(
                    f"❌ حدث خطأ غير متوقع: {str(e)}"
                )


# =========================================================
# مسح المحادثة
# =========================================================

st.divider()

if st.button("🗑️ مسح المحادثة"):

    st.session_state.messages = []

    st.rerun()
