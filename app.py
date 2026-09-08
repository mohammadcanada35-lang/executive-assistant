import streamlit as st
import requests
import html
import base64


# =========================================================
# إعداد التطبيق
# =========================================================

st.set_page_config(
    page_title="المساعد التنفيذي الذكي",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 المساعد التنفيذي الذكي")
st.caption("🎤 احچي وياي • 🧠 أفهمك • 👩 أجاوبك بصوت عراقي")


# =========================================================
# قراءة Secrets
# =========================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    AZURE_SPEECH_KEY = st.secrets["AZURE_SPEECH_KEY"]
    AZURE_SPEECH_REGION = st.secrets["AZURE_SPEECH_REGION"]
except Exception:
    st.error("❌ مفاتيح التطبيق غير مكتملة.")
    st.info(
        "روح إلى Streamlit → Settings → Secrets "
        "وتأكد من وجود المفاتيح الثلاثة."
    )
    st.code(
        'GROQ_API_KEY = "ضع_مفتاح_Groq_هنا"\n'
        'AZURE_SPEECH_KEY = "ضع_مفتاح_Azure_هنا"\n'
        'AZURE_SPEECH_REGION = "ضع_منطقة_Azure_هنا"'
    )
    st.stop()


# =========================================================
# إعداد المساعد
# =========================================================

SYSTEM_PROMPT = """
أنت مساعد تنفيذي ذكي ومحترف.

تحدث مع المستخدم باللغة العربية.

إذا كان المستخدم يتحدث باللهجة العراقية:
- جاوبه باللهجة العراقية.
- استخدم لغة طبيعية ومفهومة.
- لا تستخدم لهجة مصطنعة أو مبالغاً فيها.

أسلوبك:
- واضح.
- مباشر.
- عملي.
- ذكي.
- محترم.
- لا تطيل بدون داعٍ.

إذا طلب المستخدم خطوات، أعطه خطوات مرتبة.
إذا طلب رأياً، أعطه رأياً واضحاً مع السبب.
إذا لم تعرف شيئاً، قل إنك لا تعرف ولا تخترع المعلومات.
لا تدّعي أنك نفذت شيئاً لم تنفذه.

أنت مساعد شخصي تنفيذي يساعد المستخدم في:
العمل، المشاريع، العقارات، التسويق، الكتابة،
التخطيط، اتخاذ القرارات، البرمجة والتنظيم.
"""


# =========================================================
# ذاكرة المحادثة
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None


# =========================================================
# Groq Speech-to-Text
# =========================================================

def transcribe_audio(audio_file):

    url = "https://api.groq.com/openai/v1/audio/transcriptions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    files = {
        "file": (
            "recording.wav",
            audio_file.getvalue(),
            "audio/wav"
        )
    }

    data = {
        "model": "whisper-large-v3",
        "language": "ar",
        "response_format": "json",
        "temperature": "0"
    }

    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=data,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(
            f"Groq Speech Error {response.status_code}: "
            f"{response.text}"
        )

    result = response.json()

    text = result.get("text", "").strip()

    if not text:
        raise Exception("ما قدرت أسمع كلام واضح بالتسجيل.")

    return text


# =========================================================
# Groq AI
# =========================================================

def ask_groq():

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # نرسل آخر 30 رسالة حتى لا تكبر المحادثة بلا حدود
    messages = st.session_state.messages[-31:]

    # نضمن بقاء تعليمات النظام
    if messages[0]["role"] != "system":
        messages.insert(
            0,
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        )

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 3000
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(
            f"Groq AI Error {response.status_code}: "
            f"{response.text}"
        )

    result = response.json()

    try:
        answer = result["choices"][0]["message"]["content"]
    except Exception:
        raise Exception(
            "Groq رجع استجابة غير مفهومة."
        )

    return answer.strip()


# =========================================================
# Azure Text-to-Speech
# بدون مكتبة Azure
# =========================================================

def text_to_iraqi_voice(text):

    # نحذف HTML البسيط إذا وجد
    clean_text = html.unescape(text)

    # Azure Speech REST endpoint
    url = (
        f"https://{AZURE_SPEECH_REGION}.tts.speech.microsoft.com/"
        "cognitiveservices/v1"
    )

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3"
    }

    # نستخدم صوت بنت عراقي
    ssml = f"""
<speak version="1.0"
       xmlns="http://www.w3.org/2001/10/synthesis"
       xml:lang="ar-IQ">

    <voice name="ar-IQ-RanaNeural">
        <prosody rate="0%" pitch="0%">
            {html.escape(clean_text)}
        </prosody>
    </voice>

</speak>
"""

    response = requests.post(
        url,
        headers=headers,
        data=ssml.encode("utf-8"),
        timeout=120
    )

    if response.status_code != 200:

        raise Exception(
            f"Azure Speech Error {response.status_code}: "
            f"{response.text}"
        )

    return response.content


# =========================================================
# تشغيل الصوت داخل الصفحة
# =========================================================

def play_audio(audio_bytes):

    encoded = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
    <audio controls autoplay style="width:100%;">
        <source src="data:audio/mp3;base64,{encoded}" type="audio/mpeg">
    </audio>
    """

    st.markdown(
        audio_html,
        unsafe_allow_html=True
    )


# =========================================================
# عرض المحادثة
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# 🎤 الصوت
# =========================================================

st.subheader("🎤 احچي وياي")

audio_value = st.audio_input(
    "اضغط وسجل كلامك",
    sample_rate=16000,
    key="voice_recorder"
)


if audio_value is not None:

    current_audio_id = hash(audio_value.getvalue())

    if st.session_state.last_audio_id != current_audio_id:

        st.session_state.last_audio_id = current_audio_id

        try:

            # ---------------------------------------------
            # تحويل الصوت إلى نص
            # ---------------------------------------------

            with st.spinner("🎧 دا أسمعك..."):

                user_text = transcribe_audio(audio_value)

            with st.chat_message("user"):
                st.markdown(user_text)

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_text
                }
            )

            # ---------------------------------------------
            # الذكاء الاصطناعي
            # ---------------------------------------------

            with st.chat_message("assistant"):

                with st.spinner("🧠 دا أفكر..."):

                    reply = ask_groq()

                st.markdown(reply)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )

                # -----------------------------------------
                # الصوت العراقي
                # -----------------------------------------

                with st.spinner("👩 دا أحول الجواب إلى صوت..."):

                    audio_bytes = text_to_iraqi_voice(reply)

                play_audio(audio_bytes)

        except Exception as error:

            st.error("❌ صار خطأ أثناء معالجة التسجيل.")
            st.code(str(error))


# =========================================================
# ⌨️ الكتابة
# =========================================================

st.divider()

st.subheader("⌨️ أو اكتب لي")

text_input = st.chat_input(
    "اكتب رسالتك هنا..."
)


if text_input:

    try:

        with st.chat_message("user"):
            st.markdown(text_input)

        st.session_state.messages.append(
            {
                "role": "user",
                "content": text_input
            }
        )

        with st.chat_message("assistant"):

            with st.spinner("🧠 دا أفكر..."):

                reply = ask_groq()

            st.markdown(reply)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )

            with st.spinner("👩 دا أحچي وياك..."):

                audio_bytes = text_to_iraqi_voice(reply)

            play_audio(audio_bytes)

    except Exception as error:

        st.error("❌ صار خطأ.")
        st.code(str(error))


# =========================================================
# 🗑️ مسح المحادثة
# =========================================================

st.divider()

if st.button(
    "🗑️ مسح المحادثة",
    use_container_width=True
):

    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    st.session_state.last_audio_id = None

    st.rerun()
