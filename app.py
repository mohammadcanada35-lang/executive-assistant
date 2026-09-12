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
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ المساعد التنفيذي")
st.write("محادثة صوتية مباشرة مع Gemini Live")


# =========================================================
# مفتاح Gemini
# =========================================================

if "GEMINI_API_KEY" not in st.secrets:
    st.error("GEMINI_API_KEY غير موجود داخل Streamlit Secrets.")
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


# =========================================================
# نموذج Gemini Live الحالي
# =========================================================

MODEL = "models/gemini-2.5-flash-native-audio-latest"


# =========================================================
# تعليمات المساعد
# =========================================================

try:
    with open("system_prompt.md", "r", encoding="utf-8") as file:
        SYSTEM_PROMPT = file.read()

except FileNotFoundError:

    SYSTEM_PROMPT = """
أنت مساعد تنفيذي شخصي محترف.

تحدث مع المستخدم باللغة العربية.
استخدم اللهجة العراقية بشكل طبيعي عندما يكون ذلك مناسباً.

تحدث كأنك في مكالمة صوتية حقيقية.
اجعل ردودك طبيعية ومختصرة وواضحة.
لا تكرر كلام المستخدم بدون سبب.

ساعد المستخدم في:
- تنظيم يومه
- المواعيد
- المهام
- المتابعات
- الاجتماعات
- البريد الإلكتروني عند توفر التكامل
- التخطيط واتخاذ القرار
- تذكيره بالأمور المهمة

إذا كان الطلب يتعلق بإجراء حساس أو مهم، اطلب موافقة المستخدم قبل تنفيذه.

لا تدّعي أنك نفذت إجراءً خارج النظام إذا لم يتم تنفيذه فعلياً.

صوتك يجب أن يكون ودوداً وطبيعياً.
"""


# =========================================================
# طوابير الصوت
# =========================================================

audio_to_gemini = queue.Queue(maxsize=300)
audio_from_gemini = queue.Queue(maxsize=500)


# =========================================================
# تحويل صوت المايك إلى PCM 16kHz
# =========================================================

def convert_to_16khz(frame):

    audio = frame.to_ndarray()

    # تحويل Stereo إلى Mono
    if audio.ndim > 1:
        audio = np.mean(audio, axis=0)

    audio = audio.astype(np.float32)

    source_rate = frame.sample_rate

    # تحويل إلى 16kHz
    if source_rate != 16000:
        audio = resample_poly(
            audio,
            16000,
            source_rate,
        )

    # تحويل إلى int16
    audio = np.clip(
        audio,
        -32768,
        32767,
    )

    return audio.astype(np.int16).tobytes()


# =========================================================
# Audio Processor
# =========================================================

class GeminiAudioProcessor(AudioProcessorBase):

    def recv(self, frame):

        # -------------------------------------------------
        # 1. أخذ صوت المستخدم
        # -------------------------------------------------

        try:

            pcm_data = convert_to_16khz(frame)

            if not audio_to_gemini.full():

                audio_to_gemini.put_nowait(
                    pcm_data
                )

        except Exception:
            pass


        # -------------------------------------------------
        # 2. تشغيل صوت Gemini
        # -------------------------------------------------

        try:

            out_bytes = audio_from_gemini.get_nowait()

            out_array = np.frombuffer(
                out_bytes,
                dtype=np.int16,
            )

            if len(out_array) == 0:
                raise queue.Empty

            out_array = out_array.reshape(
                1,
                -1,
            )

            new_frame = av.AudioFrame.from_ndarray(
                out_array,
                format="s16",
                layout="mono",
            )

            new_frame.sample_rate = 24000

            return new_frame

        except queue.Empty:

            # لا يوجد رد من Gemini حالياً
            # نرسل صمت بدل إعادة صوت المستخدم

            sample_count = int(
                24000 * 0.02
            )

            silence = np.zeros(
                (1, sample_count),
                dtype=np.int16,
            )

            silent_frame = av.AudioFrame.from_ndarray(
                silence,
                format="s16",
                layout="mono",
            )

            silent_frame.sample_rate = 24000

            return silent_frame


# =========================================================
# متغيرات الحالة
# =========================================================

if "gemini_running" not in st.session_state:
    st.session_state.gemini_running = False

if "gemini_error" not in st.session_state:
    st.session_state.gemini_error = None


# =========================================================
# تشغيل Gemini Live
# =========================================================

def run_gemini_live():

    async def send_audio(session):

        while True:

            try:

                audio_data = await asyncio.to_thread(
                    audio_to_gemini.get
                )

                await session.send_realtime_input(
                    audio=types.Blob(
                        data=audio_data,
                        mime_type="audio/pcm;rate=16000",
                    )
                )

            except Exception:
                break


    async def receive_audio(session):

        try:

            async for response in session.receive():

                if not response.server_content:
                    continue

                model_turn = response.server_content.model_turn

                if not model_turn:
                    continue

                # Gemini 3.1 قد يرسل أكثر من part
                for part in model_turn.parts:

                    if not part.inline_data:
                        continue

                    audio_data = part.inline_data.data

                    if not audio_data:
                        continue

                    try:

                        if not audio_from_gemini.full():

                            audio_from_gemini.put_nowait(
                                audio_data
                            )

                    except queue.Full:
                        pass

        except Exception as error:

            st.session_state.gemini_error = str(
                error
            )


    async def main():

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        config = types.LiveConnectConfig(

            response_modalities=[
                "AUDIO"
            ],

            system_instruction=types.Content(
                parts=[
                    types.Part(
                        text=SYSTEM_PROMPT
                    )
                ]
            ),

            input_audio_transcription={},

            output_audio_transcription={},

            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"
                    )
                )
            ),

            thinking_config=types.ThinkingConfig(
                thinking_level="minimal"
            ),
        )


        try:

            async with client.aio.live.connect(
                model=MODEL,
                config=config,
            ) as session:

                st.session_state.gemini_running = True

                sender_task = asyncio.create_task(
                    send_audio(session)
                )

                receiver_task = asyncio.create_task(
                    receive_audio(session)
                )

                await asyncio.gather(
                    sender_task,
                    receiver_task,
                )

        except Exception as error:

            st.session_state.gemini_error = str(
                error
            )

            st.session_state.gemini_running = False


    asyncio.run(main())


# =========================================================
# بدء Gemini في Thread منفصل
# =========================================================

if not st.session_state.gemini_running:

    if "gemini_thread_started" not in st.session_state:

        st.session_state.gemini_thread_started = True

        thread = threading.Thread(
            target=run_gemini_live,
            daemon=True,
        )

        thread.start()


# =========================================================
# WebRTC
# =========================================================

ctx = webrtc_streamer(

    key="gemini-live",

    mode=WebRtcMode.SENDRECV,

    audio_processor_factory=GeminiAudioProcessor,

    media_stream_constraints={
        "audio": True,
        "video": False,
    },

    async_processing=True,
)


# =========================================================
# حالة الاتصال
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
        "حدث خطأ في اتصال Gemini Live:"
    )

    st.code(
        st.session_state.gemini_error
    )
