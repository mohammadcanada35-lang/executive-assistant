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


# =========================
# LiveKit settings
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


st.success("إعدادات LiveKit جاهزة ✅")


# =========================
# Start voice assistant
# =========================

if st.button("🎙️ تشغيل المساعد الصوتي", type="primary"):

    # غرفة جديدة لكل جلسة
    room_name = f"executive-{uuid.uuid4().hex[:12]}"

    try:
        token = (
            api.AccessToken(
                LIVEKIT_API_KEY,
                LIVEKIT_API_SECRET,
            )
            .with_identity(f"user-{uuid.uuid4().hex[:8]}")
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

        st.success("جاري تشغيل المساعد الصوتي... 🎙️")

        # واجهة LiveKit داخل التطبيق
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.umd.min.js"></script>

            <style>
                body {{
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background: transparent;
                    text-align: center;
                }}

                button {{
                    background: #111827;
                    color: white;
                    border: none;
                    padding: 14px 24px;
                    border-radius: 10px;
                    font-size: 16px;
                    cursor: pointer;
                }}

                #status {{
                    margin: 15px;
                    font-size: 16px;
                }}
            </style>
        </head>

        <body>

            <button id="start">🎙️ ابدأ المحادثة</button>

            <div id="status">اضغط الزر واسمح للمايكروفون</div>

            <script>
                const LIVEKIT_URL = "{LIVEKIT_URL}";
                const TOKEN = "{token}";

                let room = null;

                const button = document.getElementById("start");
                const status = document.getElementById("status");

                button.onclick = async function() {{

                    try {{

                        button.disabled = true;
                        status.innerText = "جاري الاتصال...";

                        room = new LivekitClient.Room();

                        room.on(
                            LivekitClient.RoomEvent.TrackSubscribed,
                            (track) => {{

                                if (track.kind === LivekitClient.Track.Kind.Audio) {{
                                    const element = track.attach();
                                    document.body.appendChild(element);
                                    element.autoplay = true;
                                }}

                            }}
                        );

                        room.on(
                            LivekitClient.RoomEvent.Disconnected,
                            () => {{
                                status.innerText = "تم إنهاء الاتصال";
                                button.disabled = false;
                            }}
                        );

                        await room.connect(LIVEKIT_URL, TOKEN);

                        await room.startAudio();

                        await room.localParticipant.setMicrophoneEnabled(true);

                        status.innerText = "🟢 متصل — احچي ويا المساعد الآن";

                    }} catch (error) {{

                        console.error(error);

                        status.innerText =
                            "❌ حدث خطأ: " + error.message;

                        button.disabled = false;
                    }}
                }};
            </script>

        </body>
        </html>
        """

        components.html(
            html,
            height=180,
            scrolling=False,
        )

    except Exception as e:
        st.error(f"حدث
