import streamlit as st
import requests
import streamlit.components.v1 as components


# =========================================================
# إعداد التطبيق
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

html, body, [class*="css"] {
    direction: rtl;
}

.main {
    direction: rtl;
    text-align: right;
}

h1 {
    text-align: center;
}

.description {
    text-align: center;
    font-size: 18px;
    color: #777;
    margin-bottom: 25px;
}

.voice-button {
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# العنوان
# =========================================================

st.title("🤖 المساعد التنفيذي الذكي")

st.markdown(
    '<div class="description">'
    'احچي وياي، وأنا أساعدك بالتخطيط والقرارات وتنظيم شغلك.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# قراءة مفتاح Groq
# =========================================================

try:

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

except Exception:

    st.error("❌ مفتاح Groq غير موجود.")

    st.info(
        'روح إلى Secrets وأضف:\n\n'
        'GROQ_API_KEY = "ضع مفتاحك الجديد هنا"'
    )

    st.stop()


# =========================================================
# اختيار نوع الرد
# =========================================================

st.markdown("### 🎧 اختار طريقة الرد")

response_mode = st.radio(
    "طريقة إجابة المساعد:",
    [
        "📝 جواب كتابي",
        "🔊 جواب صوتي + كتابي"
    ],
    horizontal=True
)


# =========================================================
# إدخال صوتي
# =========================================================

st.markdown("### 🎙️ احچي ويا المساعد")


components.html(
    """
    <div style="
        direction:rtl;
        text-align:center;
        padding:15px;
    ">

        <button
            onclick="startListening()"
            style="
                background:#111;
                color:white;
                border:none;
                border-radius:15px;
                padding:18px 35px;
                font-size:20px;
                font-weight:bold;
                cursor:pointer;
            "
        >
            🎙️ اضغط هنا واحچي
        </button>

        <p id="status" style="
            font-size:16px;
            margin-top:15px;
        ">
            جاهز أسمعك
        </p>

        <textarea
            id="voice_text"
            placeholder="بعد ما تحچي، النص يظهر هنا..."
            style="
                width:100%;
                height:100px;
                padding:12px;
                border-radius:12px;
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
                    "❌ المتصفح لا يدعم المايكروفون. استخدم Google Chrome.";

                return;
            }

            const recognition =
                new SpeechRecognition();

            recognition.lang = "ar-IQ";

            recognition.continuous = false;

            recognition.interimResults = false;


            document.getElementById("status").innerText =
                "🔴 أسمعك الآن... احچي";


            recognition.start();


            recognition.onresult =
                function(event) {

                    const text =
                        event.results[0][0].transcript;

                    document.getElementById("voice_text").value =
                        text;

                    document.getElementById("status").innerText =
                        "✅ تم سماع كلامك";

                };


            recognition.onerror =
                function(event) {

                    document.getElementById("status").innerText =
                        "❌ حدثت مشكلة: " +
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
# إدخال السؤال
# =========================================================

user_input = st.text_area(
    "🗣️ الكلام الذي تم التقاطه:",
    key="voice_question",
    placeholder="اضغط على المايكروفون واحچي..."
)


# =========================================================
# إرسال السؤال
# =========================================================

if st.button("🚀 اسأل المساعد"):

    if not user_input.strip():

        st.warning(
            "⚠️ أولاً اضغط على المايكروفون واحچي."
        )

    else:

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }


        payload = {

            # =================================================
            # الموديل الجديد
            # =================================================

            "model": "openai/gpt-oss-120b",

            "messages": [

                {
                    "role": "system",

                    "content": """
أنت مساعد تنفيذي ذكي ومحترف.

المستخدم عراقي.

افهم اللهجة العراقية والكلمات العراقية
والأسلوب العراقي في الكلام.

إذا كان المستخدم يحچي باللهجة العراقية،
جاوبه باللهجة العراقية بشكل طبيعي.

كن واضحاً ومباشراً وعملياً.

ساعد المستخدم في:

- إدارة الأعمال
- التخطيط
- ترتيب الأولويات
- تنظيم المهام
- اتخاذ القرارات
- إدارة الوقت
- كتابة الرسائل
- حل المشاكل
- تطوير المشاريع
- التفكير الاستراتيجي

إذا طلب المستخدم خطة،
اعطه خطة واضحة.

إذا طلب رأيك،
أعطه رأياً واضحاً مع السبب.

لا تستخدم كلاماً روبوتياً.

لا تطيل بدون داعٍ.
"""
                },

                {
                    "role": "user",
                    "content": user_input
                }

            ],

            "temperature": 0.7,

            "max_tokens": 2000
        }


        # =================================================
        # الاتصال بـ Groq
        # =================================================

        with st.spinner("🤖 دا أفكر..."):

            try:

                response = requests.post(

                    "https://api.groq.com/openai/v1/chat/completions",

                    headers=headers,

                    json=payload,

                    timeout=60
                )


                # =================================================
                # فحص الاستجابة
                # =================================================

                if response.status_code != 200:

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

                    st.stop()


                data = response.json()


                # =================================================
                # استخراج الجواب
                # =================================================

                if "choices" not in data:

                    st.error(
                        "❌ لم يصل جواب من الذكاء الاصطناعي."
                    )

                    st.json(data)

                    st.stop()


                answer = (
                    data["choices"][0]
                    ["message"]
                    ["content"]
                )


                # =================================================
                # عرض الجواب
                # =================================================

                st.markdown("### 🤖 جواب المساعد")

                st.success(answer)


                # =================================================
                # إذا اختار المستخدم الصوت
                # =================================================

                if response_mode == "🔊 جواب صوتي + كتابي":

                    # حماية النص من مشاكل JavaScript
                    safe_answer = (
                        answer
                        .replace("\\", "\\\\")
                        .replace("`", "\\`")
                        .replace("${", "\\${")
                    )


                    components.html(

                        f"""
                        <script>

                        const text = `{safe_answer}`;

                        const speech =
                            new SpeechSynthesisUtterance(text);

                        speech.lang = "ar-IQ";

                        speech.rate = 0.9;

                        speech.pitch = 1.0;

                        window.speechSynthesis.cancel();

                        window.speechSynthesis.speak(speech);

                        </script>
                        """,

                        height=1
                    )


                    st.info(
                        "🔊 جاري قراءة الجواب بصوت..."
                    )


                else:

                    st.info(
                        "📝 تم اختيار الرد الكتابي."
                    )


            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ الاتصال أخذ وقت طويل. حاول مرة ثانية."
                )


            except requests.exceptions.RequestException as e:

                st.error(
                    f"❌ مشكلة بالاتصال: {str(e)}"
                )


            except Exception as e:

                st.error(
                    f"❌ حدث خطأ: {str(e)}"
                )


# =========================================================
# معلومات
# =========================================================

st.divider()

st.caption(
    "🤖 المساعد التنفيذي الذكي — صوت وكتابة"
        )
