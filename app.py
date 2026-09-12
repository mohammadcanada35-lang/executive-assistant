import asyncio
import queue
import threading

import av
import numpy as np
import streamlit as st
from scipy.signal import resample_poly
from streamlit_webrtc import AudioProcessorBase, WebRtcMode, webrtc_streamer
from google import genai
from google.genai import types


# =========================================================
# إعداد الصفحة
# =========================================================

st.set_page_config(
    page_title="المساعد التنفيذي",
    page_icon="📞",
    layout="centered",
)

st.title("📞 المساعد التنفيذي")
st.caption("مكالمة صوتية مباشرة مع Gemini")


# =========================================================
# System Prompt
# =========================================================

try:
    with open("system_prompt.md", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = """
أنت مساعد تنفيذي شخصي محترف.

تحدث مع المستخدم باللغة العربية.
استخدم اللهجة العراقية بشكل طبيعي وواضح عندما تتحدث معه.
لا تتكلم بالفصحى الرسمية إلا إذا طلب المستخدم ذلك.

تكلم بطريقة طبيعية كأنها مكالمة هاتفية.
لا تطيل في الردود.
لا تكرر كلام المستخدم.
استمع جيداً قبل الرد.

لا تنفذ أي إجراء حساس أو مهم بدون موافقة المستخدم.
"""


# =========================================================
# Gemini API
# =========================================================

if "GEMINI_API_KEY" not in st.secrets:
    st.error("GEMINI_API_KEY غير موجود في Streamlit Secrets.")
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

MODEL = "gemini-3.1-flash-live-preview"


# =========================================================
# طوابير الصوت
# =========================================================

MIC_QUEUE = queue.Queue(maxsize=200)
SPEAKER_QUEUE = queue.Queue(maxsize=500)


# =========================================================
# حالة الاتصال
# =========================================================

if "gemini_started" not in st.session_state:
    st.session_state.gemini_started = False

if "gemini_error" not in st.session_state:
    st.session_state.gemini_error = None


# =========================================================
# تحويل صوت المايك إلى PCM 16kHz
# =========================================================

def microphone_to_pcm(frame):

    audio = frame.to_ndarray()

    # تحويل Stereo إلى Mono
    if audio.ndim > 1:
        audio = np.mean(audio, axis=0)

    audio = audio.astype(np.float32)

    # الحصول على sample rate
    sample_rate = frame.sample_rate

    # Gemini Live يحتاج 16kHz
    if sample_rate != 16000:
        audio = resample_poly(
            audio,
            16000,
            sample_rate
        )

    # تحويل إلى PCM 16-bit
    audio = np.clip(audio, -32768, 32767)

    return audio.astype(np.int16).tobytes()


# =========================================================
# Audio Processor
# =========================================================

class GeminiAudioProcessor(AudioProcessorBase):

    def recv(self, frame):

        try:

            # -----------------------------
            # إرسال صوت المستخدم إلى Gemini
            # -----------------------------

            pcm = microphone_to_pcm(frame)

            if not MIC_QUEUE.full():
                MIC_QUEUE.put_nowait(pcm)

        except Exception:
            pass


        # =================================================
        # تشغيل صوت Gemini في السماعة
        # =================================================

        try:

            if not SPEAKER_QUEUE.empty():

                data = SPEAKER_QUEUE.get_nowait()

                samples = np.frombuffer(
                    data,
                    dtype=np.int16
                )

                # Gemini يخرج 24kHz
                samples = samples.astype(np.int16)

                # AudioFrame يحتاج shape = channels x samples
                samples = samples.reshape(1, -1)

                output_frame = av.AudioFrame.from_ndarray(
                    samples,
                    format="s16",
                    layout="mono"
                )

                output_frame.sample_rate = 24000

                return output_frame

        except Exception:
            pass


        # =================================================
        # إذا ماكو رد من Gemini
        # نرجع صمت حتى تستمر المكالمة
        # =================================================

        try:

            sample_count = int(
                24000 * 0.02
            )

            silence = np.zeros(
                (1, sample_count),
                dtype=np.int16
            )

            output_frame = av.AudioFrame.from_ndarray(
                silence,
                format="s16",
                layout="mono"
            )

            output_frame.sample_rate = 24000

            return output_frame

        except Exception:
            return frame


# =========================================================
# Gemini Live Worker
# =========================================================

def start_gemini():

    async def send_audio(session):

        while True:

            try:

                audio_data = await asyncio.to_thread(
                    MIC_QUEUE.get
                )

                await session.send_realtime_input(
                    audio=types.Blob(
                        data=audio_data,
                        mime_type="audio/pcm;rate=16000"
                    )
                )

            except Exception:
                break


    async def receive_audio(session):

        try:

            async for response in session.receive():

                if not response.server_content:
                    continue

                if not response.server_content.model_turn:
                    continue

                for part in response.server_content.model_turn.parts:

                    if not part.inline_data:
                        continue

                    audio_data = part.inline_data.data

                    if not audio_data:
                        continue

                    try:

                        SPEAKER_QUEUE.put_nowait(
                            audio_data
                        )

                    except queue.Full:
                        pass

        except Exception as e:

            st.session_state.gemini_error = str(e)


    async def run():

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],

            system_instruction=types.Content(
                parts=[
                    types.Part(
                        text=SYSTEM_PROMPT
                    )
                ]
            ),

            input_audio_transcription={},

            output_audio_transcription={},

            speech_config={
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": "Kore"
                    }
                }
            },
        )

        try:

            async with client.aio.live.connect(
                model=MODEL,
                config=config
            ) as session:

                st.session_state.gemini_started = True

                sender = asyncio.create_task(
                    send_audio(session)
                )

                receiver = asyncio.create_task(
                    receive_audio(session)
                )

                await asyncio.gather(
                    sender,
                    receiver
                )

        except Exception as e:

            st.session_state.gemini_error = str(e)


    asyncio.run(run())


# =========================================================
# تشغيل Gemini مرة واحدة
# =========================================================

if not st.session_state.gemini_started:

    thread = threading.Thread(
        target=start_gemini,
        daemon=True
    )

    thread.start()


# =========================================================
# واجهة المكالمة
# =========================================================

ctx = webrtc_streamer(
    key="gemini-live-call",

    mode=WebRtcMode.SENDRECV,

    audio_processor_factory=GeminiAudioProcessor,

    media_stream_constraints={
        "audio": True,
        "video": False,
    },

    async_processing=True,
)


# =========================================================
# الحالة
# =========================================================

if ctx.state.playing:

    st.success(
        "🟢 المكالمة شغالة — احچي ويا المساعد"
    )

else:

    st.info(
        "اضغط Start واسمح للمتصفح باستخدام المايك."
    )


# =========================================================
# عرض الأخطاء
# =========================================================

if st.session_state.gemini_error:

    st.error(
        "حدث خطأ في اتصال Gemini:"
    )

    st.code(
        st.session_state.gemini_error
    )
