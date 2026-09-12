import asyncio
import queue
import threading
import time

import av
import numpy as np
import streamlit as st
from scipy.signal import resample_poly
from streamlit_webrtc import AudioProcessorBase, WebRtcMode, webrtc_streamer
from google import genai
from google.genai import types


# =========================
# إعداد الصفحة
# =========================

st.set_page_config(
    page_title="المساعد التنفيذي",
    page_icon="📞",
    layout="centered",
)

st.title("📞 المساعد التنفيذي")
st.caption("مكالمة صوتية مباشرة مع Gemini")


# =========================
# قراءة التعليمات
# =========================

try:
    with open("system_prompt.md", "r", encoding="utf-8") as f:
        system_prompt = f.read()
except FileNotFoundError:
    system_prompt = """
أنت مساعد تنفيذي شخصي محترف.
تحدث باللغة العربية.
استخدم اللهجة العراقية بشكل طبيعي عندما تتحدث مع المستخدم.
كن واضحاً ومختصراً وودوداً.
لا تنفذ أي إجراء حساس أو مهم بدون موافقة المستخدم.
"""


# =========================
# مفتاح Gemini
# =========================

if "GEMINI_API_KEY" not in st.secrets:
    st.error("لم يتم العثور على GEMINI_API_KEY في Streamlit Secrets.")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]


# =========================
# إعداد Gemini Live
# =========================

MODEL = "gemini-3.1-flash-live-preview"


# =========================
# طوابير الصوت
# =========================

audio_to_gemini = queue.Queue(maxsize=100)
audio_from_gemini = queue.Queue(maxsize=200)

stop_event = threading.Event()


# =========================
# تحويل الصوت إلى 16kHz
# =========================

def convert_to_16khz(frame):
    """
    يحول صوت المتصفح إلى PCM 16-bit / 16kHz.
    """

    audio = frame.to_ndarray()

    # إذا كان الصوت متعدد القنوات
    if audio.ndim > 1:
        audio = np.mean(audio, axis=0)

    audio = audio.astype(np.float32)

    input_rate = frame.sample_rate

    if input_rate != 16000:
        audio = resample_poly(
            audio,
            16000,
            input_rate
        )

    audio = np.clip(audio, -32768, 32767)

    return audio.astype(np.int16).tobytes()


# =========================
# معالج المايك
# =========================

class AudioProcessor(AudioProcessorBase):

    def recv(self, frame):

        try:
            pcm_data = convert_to_16khz(frame)

            if not audio_to_gemini.full():
                audio_to_gemini.put_nowait(pcm_data)

        except Exception:
            pass

        # لا نرجع صوت المايك للسماعة
        return frame


# =========================
# تشغيل Gemini Live
# =========================

def gemini_worker():

    async def run():

        client = genai.Client(
            api_key=API_KEY
        )

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=types.Content(
                parts=[
                    types.Part(
                        text=system_prompt
                    )
                ]
            ),
            input_audio_transcription={},
            output_audio_transcription={},
        )

        try:

            async with client.aio.live.connect(
                model=MODEL,
                config=config
            ) as session:

                while not stop_event.is_set():

                    try:
                        pcm_data = audio_to_gemini.get(
                            timeout=0.05
                        )
                    except queue.Empty:
                        await asyncio.sleep(0.01)
                        continue

                    await session.send_realtime_input(
                        audio=types.Blob(
                            data=pcm_data,
                            mime_type="audio/pcm;rate=16000"
                        )
                    )

                    # استقبال الرد الصوتي
                    try:

                        while True:

                            response = await asyncio.wait_for(
                                session.receive().__anext__(),
                                timeout=0.01
                            )

                            if (
                                response.server_content
                                and response.server_content.model_turn
                            ):

                                for part in response.server_content.model_turn.parts:

                                    if part.inline_data:

                                        audio_data = (
                                            part.inline_data.data
                                        )

                                        if audio_data:
                                            try:
                                                audio_from_gemini.put_nowait(
                                                    audio_data
                                                )
                                            except queue.Full:
                                                pass

                    except asyncio.TimeoutError:
                        pass

        except Exception as e:

            st.session_state["gemini_error"] = str(e)

    asyncio.run(run())


# =========================
# تشغيل الاتصال
# =========================

if "worker_started" not in st.session_state:

    st.session_state.worker_started = False


if not st.session_state.worker_started:

    st.info(
        "اضغط Start ثم اسمح للمتصفح باستخدام المايك."
    )

    st.session_state.worker_started = True

    worker = threading.Thread(
        target=gemini_worker,
        daemon=True
    )

    worker.start()


# =========================
# واجهة المكالمة
# =========================

ctx = webrtc_streamer(
    key="gemini-live-call",

    mode=WebRtcMode.SENDRECV,

    audio_processor_factory=AudioProcessor,

    media_stream_constraints={
        "audio": True,
        "video": False,
    },

    async_processing=True,
)


# =========================
# حالة المكالمة
# =========================

if ctx.state.playing:
    st.success("🟢 المكالمة متصلة — احچي وياي")

else:
    st.warning("🔴 اضغط Start لبدء المكالمة")


# =========================
# عرض حالة الخطأ
# =========================

if "gemini_error" in st.session_state:

    st.error(
        "حدث خطأ في اتصال Gemini:"
    )

    st.code(
        st.session_state["gemini_error"]
                    )
