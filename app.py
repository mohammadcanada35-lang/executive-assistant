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
    border-radius: 12px;
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
# مفتاح Groq
# =========================================================

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]

except Exception:

    st.error(
        "❌ مفتاح Groq غير موجود.\n\n"
        "اذهب إلى Secrets وأضف:\n\n"
        "GROQ_API_KEY = \"مفتاحك هنا\""
    )

    st.stop()


# =========================================================
# ذاكرة المحادثة
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# عرض المحادثة
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.write(message["content"])

    elif message["role"] == "assistant":

        with st.chat_message("assistant"):
            st.write(message["content"])


# =========================================================
# المايكروفون
# =========================================================

st.markdown("### 🎙️ تحدث مع المساعد")

components.html(
    """
    <div style="
        direction:rtl;
        text-align:center;
        padding:10px;
    ">

        <button
            onclick="startListening()"
            style="
                background:#111;
                color:white;
                border:none;
                border-radius:12px;
                padding:15px 30px;
                font-size:18px;
                cursor:pointer;
            "
        >
            🎙️ اضغط وتكلم
        </button>

        <p id="status">
            اضغط على الزر وتكلم
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
                font-size:17px;
                direction:rtl;
                box-sizing:border-box;
            "
        ></textarea>

        <script>

        function startListening() {

            const SpeechRecognition =
                window.SpeechRecognition ||
                window.webkitSpeechRecognition;

            if (!SpeechRecognition) {

                document.getElementById("status").innerText =
                    "❌ المتصفح لا يدعم التعرف على الصوت. استخدم Google Chrome.";

                return;
            }

            const recognition =
                new SpeechRecognition();

            recognition.lang = "ar-IQ";

            recognition.continuous = false;

            recognition.interimResults = false;

            document.getElementById("status").innerText =
                "🎙️ أسمعك الآن... احچي";

            recognition.start();


            recognition.onresult =
                function(event) {

                    const transcript =
                        event.results[0][0].transcript;

                    document.getElementById("result").value =
                        transcript;

                    document.getElementById("status").innerText =
                        "✅ تم تحويل صوتك إلى نص";

                };


            recognition.onerror =
                function(event) {

                    document.getElementById("status").innerText =
                        "❌ مشكلة بالمايكروفون: " +
                        event.error;

                };


            recognition.onend =
                function() {

                    if (
                        document
                        .getElementById("status")
                        .innerText
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
    "✍️ اكتب سؤالك:",
    placeholder="مثلاً: رتب لي مهامي اليوم حسب الأولوية...",
    height=120
)


# =========================================================
# إرسال
# =========================================================

if st.button("🚀 إرسال"):

    if not user_input.strip():

        st.warning(
            "⚠️ اكتب سؤالًا أو تحدث باستخدام المايكروفون أولاً."
        )

    else:

        # إضافة سؤال المستخدم
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )


        # =====================================================
        # Groq
        # =====================================================

        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }


        payload = {

            # الموديل الجديد
            "model": "openai/gpt-oss-120b",

            "messages": [

                {
                    "role": "system",
                    "content": """
أنت المساعد التنفيذي الذكي.

أنت مساعد محترف وعملي يساعد المستخدم في:

- إدارة الأعمال
- التخطيط
- ترتيب الأولويات
- تنظيم المهام
- اتخاذ القرارات
- إدارة الوقت
- كتابة الرسائل
- تحليل المشاكل
- تطوير المشاريع
- التفكير الاستراتيجي

تحدث باللغة العربية.

إذا تحدث المستخدم باللهجة العراقية،
افهم اللهجة العراقية ورد عليه بأسلوب عراقي
طبيعي ومفهوم.

لا تتكلم بطريقة روبوتية.

كن واضحاً ومباشراً.

إذا كان السؤال يحتاج خطوات،
استخدم قائمة مرقمة.

إذا كان المستخدم يريد قراراً،
اعرض له الخيارات ثم أعطه توصية واضحة.

لا تطيل الإجابة بدون سبب.
"""
                }

            ]

            + st.session_state.messages,

            "temperature": 0.7,

            "max_tokens": 2000
        }


        # =====================================================
        # إرسال الطلب
        # =====================================================

        with st.spinner("🤖 المساعد يفكر..."):

            try:

                response = requests.post(

                    "https://api.groq.com/openai/v1/chat/completions",

                    json=payload,

                    headers=headers,

                    timeout=60
                )


                response.raise_for_status()

                res_data = response.json()


                # =================================================
                # الرد
                # =================================================

                if "choices" in res_data:

                    reply = (
                        res_data["choices"][0]
                        ["message"]
                        ["content"]
                    )


                    # حفظ الرد
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": reply
                        }
                    )


                    # عرض الرد
                    with st.chat_message("assistant"):

                        st.write(reply)


                    # =================================================
                    # تحويل الرد إلى صوت
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
                        "❌ لم يصل رد صحيح من Groq."
                    )

                    st.json(res_data)


            # =====================================================
            # أخطاء API
            # =====================================================

            except requests.exceptions.HTTPError:

                st.error(
                    "❌ Groq رفض الطلب."
                )

                try:

                    st.json(
                        response.json()
                    )

                except Exception:

                    st.write(
                        response.text
                    )


            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ انتهى وقت الاتصال بـ Groq. "
                    "حاول مرة ثانية."
                )


            except Exception as e:

                st.error(
                    f"❌ حدث خطأ: {str(e)}"
                )


# =========================================================
# مسح المحادثة
# =========================================================

st.divider()

if st.button("🗑️ مسح المحادثة"):

    st.session_state.messages = []

    st.rerun()
