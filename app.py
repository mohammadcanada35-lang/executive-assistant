import streamlit as st
import requests
import base64


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

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #777;
    margin-bottom: 30px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# العنوان
# =========================================================

st.title("🤖 المساعد التنفيذي الذكي")

st.markdown(
    '<div class="subtitle">'
    'احچي وياي، وأنا أفهمك وأجاوبك كتابة أو صوت.'
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

    st.code(
        'GROQ_API_KEY = "ضع_المفتاح_الجديد_هنا"',
        language="toml"
    )

    st.stop()


# =========================================================
# إعدادات
# =========================================================

CHAT_MODEL = "openai/gpt-oss-120b"

STT_MODEL = "whisper-large-v3-turbo"

TTS_MODEL = "canopylabs/orpheus-arabic-saudi"

TTS_VOICE = "farah"


# =========================================================
# اختيار طريقة الرد
# =========================================================

st.markdown("### 🎧 طريقة رد المساعد")

response_mode = st.radio(
    "اختار:",
    [
        "📝 كتابة فقط",
        "🔊 صوت + كتابة"
    ],
    horizontal=True
)


# =========================================================
# تسجيل الصوت
# =========================================================

st.markdown("### 🎙️ احچي ويا المساعد")

audio_file = st.audio_input(
    "اضغط هنا وسجّل كلامك"
)


# =========================================================
# إرسال السؤال
# =========================================================

if audio_file is not None:

    st.audio(
        audio_file,
        format="audio/wav"
    )

    if st.button(
        "🚀 أرسل الكلام للمساعد",
        use_container_width=True
    ):

        with st.spinner("🎙️ دا أفهم كلامك..."):

            try:

                # =================================================
                # تحويل الصوت إلى نص باستخدام Whisper
                # =================================================

                audio_bytes = audio_file.getvalue()

                files = {
                    "file": (
                        "recording.wav",
                        audio_bytes,
                        "audio/wav"
                    )
                }

                stt_data = {
                    "model": STT_MODEL,
                    "language": "ar",
                    "response_format": "json",
                    "temperature": 0
                }

                stt_headers = {
                    "Authorization":
                        f"Bearer {GROQ_API_KEY}"
                }

                transcription_response = requests.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers=stt_headers,
                    files=files,
                    data=stt_data,
                    timeout=60
                )

                transcription_response.raise_for_status()

                transcription = transcription_response.json()

                user_text = transcription.get(
                    "text",
                    ""
                ).strip()


                # =================================================
                # التأكد من وجود كلام
                # =================================================

                if not user_text:

                    st.error(
                        "❌ ما قدرت أتعرف على كلامك. "
                        "حاول تحچي مرة ثانية."
                    )

                    st.stop()


                # =================================================
                # عرض ما فهمه المساعد
                # =================================================

                st.markdown("### 🗣️ كلامك")

                st.info(user_text)


                # =================================================
                # إرسال الكلام إلى النموذج
                # =================================================

                with st.spinner(
                    "🤖 دا أفكر بالجواب..."
                ):

                    chat_headers = {
                        "Authorization":
                            f"Bearer {GROQ_API_KEY}",

                        "Content-Type":
                            "application/json"
                    }


                    chat_payload = {

                        "model": CHAT_MODEL,

                        "messages": [

                            {
                                "role": "system",

                                "content": """
أنت مساعد تنفيذي ذكي ومحترف.

المستخدم عراقي ويتحدث باللهجة العراقية.

افهم اللهجة العراقية والكلمات العراقية
والتعبيرات العراقية.

أجب المستخدم باللغة العربية.

إذا كان مناسباً للسياق،
استخدم اللهجة العراقية بشكل طبيعي.

كن عملياً ومباشراً.

ساعد المستخدم في:

- الأعمال
- التخطيط
- إدارة الوقت
- ترتيب الأولويات
- تنظيم المهام
- اتخاذ القرارات
- كتابة الرسائل
- حل المشاكل
- تطوير المشاريع
- التفكير الاستراتيجي

إذا طلب خطة، قدم خطوات واضحة.

إذا طلب رأياً، أعطه رأياً واضحاً
مع السبب.

لا تستخدم أسلوباً روبوتياً.

لا تطيل بدون داعٍ.
"""
                            },

                            {
                                "role": "user",
                                "content": user_text
                            }

                        ],

                        "temperature": 0.7,

                        "max_tokens": 1500
                    }


                    chat_response = requests.post(

                        "https://api.groq.com/openai/v1/chat/completions",

                        headers=chat_headers,

                        json=chat_payload,

                        timeout=60
                    )


                    chat_response.raise_for_status()

                    chat_result = chat_response.json()


                    # =================================================
                    # استخراج الجواب
                    # =================================================

                    if "choices" not in chat_result:

                        st.error(
                            "❌ ما وصل جواب من المساعد."
                        )

                        st.json(chat_result)

                        st.stop()


                    answer = (
                        chat_result["choices"][0]
                        ["message"]
                        ["content"]
                    )


                # =================================================
                # عرض الجواب كتابة
                # =================================================

                st.markdown("### 🤖 جواب المساعد")

                st.success(answer)


                # =================================================
                # إذا اختار المستخدم الرد الصوتي
                # =================================================

                if response_mode == "🔊 صوت + كتابة":

                    with st.spinner(
                        "🔊 دا أحول الجواب إلى صوت..."
                    ):

                        tts_headers = {
                            "Authorization":
                                f"Bearer {GROQ_API_KEY}",

                            "Content-Type":
                                "application/json"
                        }


                        # موديل Orpheus العربي
                        tts_payload = {

                            "model": TTS_MODEL,

                            "voice": TTS_VOICE,

                            # الموديل العربي له حد إدخال 200 حرف
                            "input": answer[:200],

                            "response_format": "wav",

                            "speed": 1.0
                        }


                        tts_response = requests.post(

                            "https://api.groq.com/openai/v1/audio/speech",

                            headers=tts_headers,

                            json=tts_payload,

                            timeout=60
                        )


                        if tts_response.status_code != 200:

                            st.error(
                                "❌ فشل إنشاء الصوت."
                            )

                            try:
                                st.json(
                                    tts_response.json()
                                )

                            except Exception:
                                st.write(
                                    tts_response.text
                                )

                            st.stop()


                        # =================================================
                        # تشغيل الصوت
                        # =================================================

                        audio_bytes = (
                            tts_response.content
                        )


                        st.markdown(
                            "### 🔊 جواب المساعد الصوتي"
                        )

                        st.audio(
                            audio_bytes,
                            format="audio/wav",
                            autoplay=True
                        )


            # =========================================================
            # الأخطاء
            # =========================================================

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ الاتصال أخذ وقت طويل. "
                    "حاول مرة ثانية."
                )

            except requests.exceptions.HTTPError as e:

                st.error(
                    "❌ Groq رفض أحد الطلبات."
                )

                st.write(str(e))

            except Exception as e:

                st.error(
                    f"❌ حدث خطأ: {str(e)}"
                )


# =========================================================
# معلومات
# =========================================================

st.divider()

st.caption(
    "🤖 Executive Assistant • Voice + Text"
)
