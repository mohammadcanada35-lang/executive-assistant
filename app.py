import streamlit as st
import requests
import azure.cognitiveservices.speech as speechsdk


# =========================================================
# إعداد الصفحة
# =========================================================

st.set_page_config(
    page_title="المساعد التنفيذي الذكي",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 المساعد التنفيذي الذكي")
st.caption("🎤 احچي وياي • 🧠 أفهمك • 👩 أجاوبك بصوت عراقي")


# =========================================================
# قراءة المفاتيح من Streamlit Secrets
# =========================================================

required_secrets = [
    "GROQ_API_KEY",
    "AZURE_SPEECH_KEY",
    "AZURE_SPEECH_REGION",
]

missing_secrets = [
    secret for secret in required_secrets
    if secret not in st.secrets
]

if missing_secrets:
    st.error("❌ التطبيق يحتاج إعداد المفاتيح.")
    st.write("المفاتيح الناقصة:")

    for secret in missing_secrets:
        st.code(secret)

    st.info(
        "أضف هذه المفاتيح من Streamlit → Settings → Secrets."
    )

    st.stop()


GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
AZURE_SPEECH_KEY = st.secrets["AZURE_SPEECH_KEY"]
AZURE_SPEECH_REGION = st.secrets["AZURE_SPEECH_REGION"]


# =========================================================
# إعداد المساعد
# =========================================================

SYSTEM_PROMPT = """
أنت مساعد تنفيذي ذكي ومحترف.

أسلوبك:
- تحدث باللغة العربية بشكل طبيعي.
- إذا تحدث المستخدم باللهجة العراقية، جاوبه باللهجة العراقية.
- استخدم أسلوب عراقي طبيعي وغير متكلف.
- كن واضحاً ومباشراً.
- لا تطيل بدون سبب.
- إذا كان السؤال يحتاج خطوات، رتبها بشكل واضح.
- إذا كان المستخدم يريد قراراً أو نصيحة، ساعده على اتخاذ قرار عملي.
- لا تدّعي أنك نفذت شيئاً لم تنفذه فعلاً.
- إذا لم تعرف معلومة، قل ذلك بصراحة.
- تعامل مع المستخدم باحترام وهدوء.
- لا تكرر كلام المستخدم بدون فائدة.

أنت مساعد شخصي تنفيذي هدفك مساعدة المستخدم في:
التخطيط، العمل، الأفكار، الكتابة، التنظيم، اتخاذ القرارات،
التسويق، العقارات، المشاريع، البرمجة، والتواصل.
"""


# =========================================================
# إنشاء المحادثة
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]


# =========================================================
# Groq - تحويل الصوت إلى نص
# =========================================================

def transcribe_audio(audio_file):

    url = "https://api.groq.com/openai/v1/audio/transcriptions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    files = {
        "file": (
            audio_file.name,
            audio_file.getvalue(),
            audio_file.type or "audio/wav",
        )
    }

    data = {
        "model": "whisper-large-v3",
        "language": "ar",
        "response_format": "json",
        "temperature": "0",
    }

    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=data,
        timeout=120,
    )

    if response.status_code != 200:
        raise Exception(
            f"Groq Speech-to-Text Error: "
            f"{response.status_code} - {response.text}"
        )

    result = response.json()

    text = result.get("text", "").strip()

    if not text:
        raise Exception("ما قدرت أستخرج كلام واضح من التسجيل.")

    return text


# =========================================================
# Groq - المساعد الذكي
# =========================================================

def ask_groq():

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": st.session_state.messages,
        "temperature": 0.7,
        "max_tokens": 4000,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120,
    )

    if response.status_code != 200:
        raise Exception(
            f"Groq Chat Error: "
            f"{response.status_code} - {response.text}"
        )

    result = response.json()

    try:
        answer = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise Exception("Groq رجع استجابة غير متوقعة.")

    return answer.strip()


# =========================================================
# Azure - تحويل النص إلى صوت عراقي أنثوي
# =========================================================

def text_to_iraqi_voice(text):

    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION,
    )

    # صوت أنثوي عربي عراقي
    speech_config.speech_synthesis_voice_name = "ar-IQ-RanaNeural"

    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio24Khz160KBitRateMonoMp3
    )

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=None,
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:

        return result.audio_data

    elif result.reason == speechsdk.ResultReason.Canceled:

        cancellation = (
            speechsdk.SpeechSynthesisCancellationDetails
            .from_result(result)
        )

        details = cancellation.error_details or "سبب غير معروف"

        raise Exception(
            f"تعذر إنشاء الصوت العراقي: {details}"
        )

    else:

        raise Exception("تعذر إنشاء الرد الصوتي.")


# =========================================================
# عرض المحادثة السابقة
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# التسجيل الصوتي
# =========================================================

st.subheader("🎤 احچي وياي")

audio_value = st.audio_input(
    "اضغط هنا وسجل كلامك",
    sample_rate=16000,
)


if audio_value is not None:

    audio_id = hash(audio_value.getvalue())

    # منع معالجة نفس التسجيل أكثر من مرة
    if st.session_state.get("last_audio_id") != audio_id:

        st.session_state.last_audio_id = audio_id

        try:

            with st.spinner("🎧 دا أسمعك..."):

                user_text = transcribe_audio(audio_value)

            # عرض كلام المستخدم
            with st.chat_message("user"):
                st.markdown(user_text)

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_text,
                }
            )

            with st.spinner("🧠 دا أفكر..."):

                reply = ask_groq()

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": reply,
                }
            )

            with st.chat_message("assistant"):

                st.markdown(reply)

                with st.spinner("👩 دا أحچي وياك..."):

                    audio_bytes = text_to_iraqi_voice(reply)

                st.audio(
                    audio_bytes,
                    format="audio/mp3",
                    autoplay=True,
                )

        except Exception as error:

            st.error("❌ صار خطأ:")
            st.code(str(error))


# =========================================================
# الكتابة
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
                "content": text_input,
            }
        )

        with st.chat_message("assistant"):

            with st.spinner("🧠 دا أفكر..."):

                reply = ask_groq()

            st.markdown(reply)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": reply,
                }
            )

            with st.spinner("👩 دا أحچي وياك..."):

                audio_bytes = text_to_iraqi_voice(reply)

            st.audio(
                audio_bytes,
                format="audio/mp3",
                autoplay=True,
            )

    except Exception as error:

        st.error("❌ صار خطأ:")
        st.code(str(error))


# =========================================================
# مسح المحادثة
# =========================================================

st.divider()

if st.button(
    "🗑️ مسح المحادثة",
    use_container_width=True,
):

    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    st.session_state.last_audio_id = None

    st.rerun()
