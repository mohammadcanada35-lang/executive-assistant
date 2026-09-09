import os
import uuid

import streamlit as st
import streamlit.components.v1 as components
from livekit import api


st.set_page_config(
    page_title="AI Executive Assistant",
    page_icon="🤖",
)

st.title("🤖 AI Executive Assistant")
st.write("المساعد التنفيذي الصوتي")


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


st.success("إعدادات LiveKit جاهزة ✅")


if st.button("🎙️ تشغيل المساعد الصوتي", type="primary"):

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
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    text-align: center;
                }

                button {
                    background: #111827;
                    color: white;
                    border: none;
                    padding: 14px 25px;
                    border-radius: 10px;
                    font-size: 17px;
                    cursor: pointer;
                }

                button:disabled {
                    opacity: 0.6;
                }

                #status {
                    margin-top: 15px;
                    font-size: 16px;
                }
            </style>
        </head>

        <body>

            <button id="start">
                🎙️ ابدأ المحادثة
            </button>

            <div id="status">
                اضغط الزر لبدء المحادثة
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

                        status.innerText = "جاري الاتصال...";

                        room = new LivekitClient.Room();

                        room.on(
                            LivekitClient.RoomEvent.TrackSubscribed,
                            function(track) {

                                if (
                                    track.kind ===
                                    LivekitClient.Track.Kind.Audio
                                ) {
                                    const audio = track.attach();
                                    document.body.appendChild(audio);
                                    audio.autoplay = true;
                                }

                            }
                        );

                        room.on(
                            LivekitClient.RoomEvent.Disconnected,
                            function() {
                                status.innerText =
                                    "تم إنهاء الاتصال";
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
                            "❌ حدث خطأ أثناء الاتصال";

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
            height=220,
            scrolling=False,
        )

    except Exception as e:
        st.error("حدث خطأ أثناء إنشاء الاتصال")
        st.code(str(e))
