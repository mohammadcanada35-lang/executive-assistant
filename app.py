import os
import uuid

import streamlit as st
import streamlit.components.v1 as components
from livekit import api


st.set_page_config(
    page_title="المساعد التنفيذي الذكي",
    page_icon="🤖",
    layout="centered",
)

# =========================
# التصميم
# =========================

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #777;
        margin-bottom: 35px;
    }

    .assistant-card {
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #ddd;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🤖 المساعد التنفيذي الذكي</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">فكّر بوضوح • تواصل بثقة • حافظ على الزخم</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="assistant-card">
        <h2>🎙️ مساعدك الصوتي</h2>
        <p>اضغط على الزر وابدأ المحادثة مع مساعدك التنفيذي.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================
# إعدادات LiveKit
# =========================

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

AGENT_NAME = "assistant-167e"


if not LIVEKIT_URL:
    st.error("LIVEKIT_URL غير موجود")
    st.stop()

if not LIVEKIT_API_KEY:
    st.error("LIVEKIT_API_KEY غير موجود")
    st.stop()

if not LIVEKIT_API_SECRET:
    st.error("LIVEKIT_API_SECRET غير موجود")
    st.stop()


# =========================
# تشغيل المساعد
# =========================

if st.button(
    "🎙️ تشغيل المساعد الصوتي",
    type="primary",
    use_container_width=True,
):

    room_name = "executive-" + uuid.uuid4().hex[:12]
    identity = "user-" + uuid.uuid4().hex[:8]

    try:

        token = (
            api.AccessToken(
                LIVEKIT_API_KEY,
                LIVEKIT_API_SECRET,
            )
            .with_identity(identity)
            .with_name("User")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                )
            )
            .with_room_config(
                api.RoomConfiguration(
                    agents=[
                        api.RoomAgentDispatch(
                            agent_name=AGENT_NAME,
                        )
                    ]
                )
            )
            .to_jwt()
        )

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">

            <script src="https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.umd.min.js"></script>

            <style>

                body {
                    margin: 0;
                    padding: 10px;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    background: transparent;
                }

                #start {
                    width: 100%;
                    max-width: 420px;
                    padding: 18px;
                    border: none;
                    border-radius: 14px;
                    background: #111827;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    cursor: pointer;
                }

                #start:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }

                #status {
                    margin-top: 18px;
                    font-size: 17px;
                    font-weight: 600;
                }

            </style>
        </head>

        <body>

            <button id="start">
                🎙️ ابدأ المحادثة
            </button>

            <div id="status">
                جاهز للمحادثة
            </div>

            <script>

                const LIVEKIT_URL = "__LIVEKIT_URL__";
                const TOKEN = "__TOKEN__";

                let room = null;

                const button = document.getElementById("start");
                const status = document.getElementById("status");

                button.onclick = async function () {

                    try {

                        button.disabled = true;

                        status.innerText = "🔄 جاري الاتصال...";

                        room = new LivekitClient.Room();

                        room.on(
                            LivekitClient.RoomEvent.TrackSubscribed,
                            function(track) {

                                if (
                                    track.kind ===
                                    LivekitClient.Track.Kind.Audio
                                ) {

                                    const audio = track.attach();

                                    audio.autoplay = true;

                                    document.body.appendChild(audio);
                                }
                            }
                        );

                        room.on(
                            LivekitClient.RoomEvent.Disconnected,
                            function() {

                                status.innerText =
                                    "🔴 تم إنهاء المحادثة";

                                button.disabled = false;
                            }
                        );

                        await room.connect(
                            LIVEKIT_URL,
                            TOKEN
                        );

                        await room.localParticipant.setMicrophoneEnabled(
                            true
                        );

                        status.innerText =
                            "🟢 متصل — احچي ويا المساعد الآن";

                    } catch (error) {

                        console.error(error);

                        status.innerText =
                            "❌ تعذر الاتصال بالمساعد";

                        button.disabled = false;
                    }
                };

            </script>

        </body>
        </html>
        """

        html = html.replace(
            "__LIVEKIT_URL__",
            LIVEKIT_URL,
        )

        html = html.replace(
            "__TOKEN__",
            token,
        )

        components.html(
            html,
            height=180,
            scrolling=False,
        )

    except Exception as e:

        st.error("حدث خطأ أثناء تشغيل المساعد")

        st.code(str(e))


st.markdown("---")

st.caption(
    "المساعد التنفيذي الذكي • يعمل بالصوت عبر LiveKit"
        )
