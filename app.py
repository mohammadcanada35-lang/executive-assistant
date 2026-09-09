import os
import uuid

import streamlit as st
import streamlit.components.v1 as components
from livekit import api


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="المساعد التنفيذي الذكي",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# LIVEKIT SETTINGS
# =========================================================

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


# =========================================================
# CUSTOM STREAMLIT STYLE
# =========================================================

st.markdown(
    """
    <style>

    /* الصفحة */
    .stApp {
        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(99,102,241,0.12),
                transparent 38%
            ),
            #0b1020;
    }

    /* إخفاء عناصر Streamlit الزائدة */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent;
    }

    /* المحتوى */
    .block-container {
        max-width: 720px;
        padding-top: 35px;
        padding-bottom: 30px;
    }

    /* الشعار */
    .logo {
        width: 82px;
        height: 82px;
        margin: 0 auto 18px auto;
        border-radius: 26px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 42px;

        background:
            linear-gradient(
                145deg,
                #6366f1,
                #8b5cf6
            );

        box-shadow:
            0 15px 45px rgba(99,102,241,0.35);
    }

    /* العنوان */
    .title {
        text-align: center;
        color: white;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 7px;
    }

    .subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 16px;
        margin-bottom: 28px;
    }

    /* بطاقة المساعد */
    .assistant-card {
        background:
            linear-gradient(
                145deg,
                rgba(31,41,55,0.90),
                rgba(17,24,39,0.95)
            );

        border: 1px solid rgba(255,255,255,0.08);

        border-radius: 28px;

        padding: 28px 22px;

        text-align: center;

        box-shadow:
            0 20px 60px rgba(0,0,0,0.25);

        margin-bottom: 22px;
    }

    .assistant-name {
        color: white;
        font-size: 23px;
        font-weight: 700;
        margin-bottom: 7px;
    }

    .assistant-description {
        color: #9ca3af;
        font-size: 14px;
        line-height: 1.7;
    }

    /* معلومات */
    .features {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 18px;
    }

    .feature {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.06);
        color: #d1d5db;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 12px;
    }

    /* زر Streamlit */
    div.stButton > button {
        width: 100%;
        min-height: 58px;

        border-radius: 17px;

        font-size: 17px;
        font-weight: 700;

        border: 0;

        background:
            linear-gradient(
                135deg,
                #6366f1,
                #8b5cf6
            );

        color: white;

        box-shadow:
            0 12px 30px rgba(99,102,241,0.25);
    }

    div.stButton > button:hover {
        border: 0;
        color: white;
    }

    /* الفوتر */
    .footer {
        text-align: center;
        color: #6b7280;
        font-size: 12px;
        margin-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="logo">🤖</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="title">المساعد التنفيذي الذكي</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">مساعدك الصوتي لاتخاذ القرار والتواصل بذكاء</div>',
    unsafe_allow_html=True,
)


# =========================================================
# ASSISTANT CARD
# =========================================================

st.markdown(
    """
    <div class="assistant-card">

        <div class="assistant-name">
            Executive AI
        </div>

        <div class="assistant-description">
            تحدث معه بشكل طبيعي، واسأله عن أفكارك،
            خططك، أعمالك، ومهامك اليومية.
        </div>

        <div class="features">

            <div class="feature">
                🎙️ صوت مباشر
            </div>

            <div class="feature">
                🧠 ذكاء اصطناعي
            </div>

            <div class="feature">
                ⚡ استجابة سريعة
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# START CALL
# =========================================================

if st.button(
    "🎙️ بدء المحادثة",
    type="primary",
    use_container_width=True,
):

    room_name = "executive-" + uuid.uuid4().hex[:12]
    identity = "user-" + uuid.uuid4().hex[:8]

    try:

        # إنشاء Token مع Agent Dispatch
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
                    ],
                ),
            )
            .to_jwt()
        )


        # =================================================
        # VOICE INTERFACE
        # =================================================

        html = """
        <!DOCTYPE html>

        <html lang="ar">

        <head>

            <meta charset="UTF-8">

            <meta
                name="viewport"
                content="width=device-width,
                initial-scale=1.0"
            >

            <script
                src="https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.umd.min.js">
            </script>

            <style>

                * {
                    box-sizing: border-box;
                }

                body {

                    margin: 0;

                    padding: 10px;

                    font-family:
                        Arial,
                        sans-serif;

                    background:
                        transparent;

                    color: white;

                    text-align: center;

                }


                .voice-box {

                    max-width: 520px;

                    margin: auto;

                    padding: 25px;

                    border-radius: 26px;

                    background:
                        linear-gradient(
                            145deg,
                            #111827,
                            #0f172a
                        );

                    border:
                        1px solid
                        rgba(255,255,255,0.08);

                    box-shadow:
                        0 20px 50px
                        rgba(0,0,0,0.25);

                }


                .avatar {

                    width: 90px;

                    height: 90px;

                    margin:
                        5px auto 18px auto;

                    border-radius: 50%;

                    display: flex;

                    align-items: center;

                    justify-content: center;

                    font-size: 45px;

                    background:
                        linear-gradient(
                            145deg,
                            #6366f1,
                            #8b5cf6
                        );

                    box-shadow:
                        0 0 0
                        rgba(99,102,241,0);

                    transition:
                        0.3s ease;

                }


                .avatar.active {

                    box-shadow:
                        0 0 0 12px
                        rgba(99,102,241,0.08),
                        0 0 45px
                        rgba(99,102,241,0.35);

                    animation:
                        pulse 1.8s infinite;

                }


                @keyframes pulse {

                    0% {
                        transform: scale(1);
                    }

                    50% {
                        transform: scale(1.05);
                    }

                    100% {
                        transform: scale(1);
                    }

                }


                .name {

                    font-size: 21px;

                    font-weight: 700;

                    margin-bottom: 7px;

                }


                .status {

                    color: #9ca3af;

                    font-size: 14px;

                    margin-bottom: 22px;

                }


                .timer {

                    font-size: 14px;

                    color: #6b7280;

                    margin-bottom: 20px;

                }


                .controls {

                    display: flex;

                    justify-content: center;

                    gap: 12px;

                }


                button {

                    border: none;

                    cursor: pointer;

                    font-size: 15px;

                    font-weight: 700;

                    border-radius: 15px;

                    padding: 15px 20px;

                    transition:
                        0.2s ease;

                }


                #start {

                    width: 100%;

                    background:
                        linear-gradient(
                            135deg,
                            #6366f1,
                            #8b5cf6
                        );

                    color: white;

                }


                #mute {

                    flex: 1;

                    background:
                        #1f2937;

                    color: white;

                }


                #end {

                    flex: 1;

                    background:
                        #7f1d1d;

                    color: white;

                }


                button:disabled {

                    opacity: 0.55;

                    cursor: not-allowed;

                }


                button:active {

                    transform: scale(0.97);

                }


                .hidden {

                    display: none;

                }

            </style>

        </head>


        <body>


            <div class="voice-box">

                <div
                    id="avatar"
                    class="avatar"
                >
                    🤖
                </div>


                <div class="name">
                    Executive AI
                </div>


                <div
                    id="status"
                    class="status"
                >
                    جاهز للمحادثة
                </div>


                <div
                    id="timer"
                    class="timer"
                >
                    00:00
                </div>


                <button id="start">
                    🎙️ ابدأ المحادثة
                </button>


                <div
                    id="controls"
                    class="controls hidden"
                >

                    <button id="mute">
                        🎤 كتم المايك
                    </button>

                    <button id="end">
                        🔴 إنهاء
                    </button>

                </div>

            </div>


            <script>

                const LIVEKIT_URL =
                    "__LIVEKIT_URL__";

                const TOKEN =
                    "__TOKEN__";


                let room = null;

                let muted = false;

                let timerInterval = null;

                let seconds = 0;


                const startButton =
                    document.getElementById(
                        "start"
                    );

                const muteButton =
                    document.getElementById(
                        "mute"
                    );

                const endButton =
                    document.getElementById(
                        "end"
                    );

                const controls =
                    document.getElementById(
                        "controls"
                    );

                const status =
                    document.getElementById(
                        "status"
                    );

                const timer =
                    document.getElementById(
                        "timer"
                    );

                const avatar =
                    document.getElementById(
                        "avatar"
                    );


                function updateTimer() {

                    seconds++;

                    const minutes =
                        Math.floor(
                            seconds / 60
                        );

                    const secs =
                        seconds % 60;

                    timer.innerText =
                        String(minutes)
                            .padStart(2, "0")
                        + ":" +
                        String(secs)
                            .padStart(2, "0");

                }


                function resetInterface() {

                    clearInterval(
                        timerInterval
                    );

                    seconds = 0;

                    timer.innerText =
                        "00:00";

                    avatar.classList.remove(
                        "active"
                    );

                    controls.classList.add(
                        "hidden"
                    );

                    startButton.classList.remove(
                        "hidden"
                    );

                    startButton.disabled =
                        false;

                    muteButton.innerText =
                        "🎤 كتم المايك";

                    muted = false;

                }


                startButton.onclick =
                    async function() {

                    try {

                        startButton.disabled =
                            true;

                        status.innerText =
                            "🔄 جاري الاتصال...";


                        room =
                            new LivekitClient.Room();


                        room.on(
                            LivekitClient.RoomEvent.TrackSubscribed,
                            function(track) {

                                if (
                                    track.kind ===
                                    LivekitClient.Track.Kind.Audio
                                ) {

                                    const audio =
                                        track.attach();

                                    audio.autoplay =
                                        true;

                                    document.body
                                        .appendChild(
                                            audio
                                        );
                                }

                            }
                        );


                        room.on(
                            LivekitClient.RoomEvent.Disconnected,
                            function() {

                                status.innerText =
                                    "🔴 تم إنهاء المحادثة";

                                resetInterface();

                            }
                        );


                        await room.connect(
                            LIVEKIT_URL,
                            TOKEN
                        );


                        await room
                            .localParticipant
                            .setMicrophoneEnabled(
                                true
                            );


                        status.innerText =
                            "🟢 متصل — احچي ويا المساعد";

                        avatar.classList.add(
                            "active"
                        );

                        startButton.classList.add(
                            "hidden"
                        );

                        controls.classList.remove(
                            "hidden"
                        );


                        timerInterval =
                            setInterval(
                                updateTimer,
                                1000
                            );


                    } catch (error) {

                        console.error(
                            error
                        );

                        status.innerText =
                            "❌ تعذر الاتصال";

                        startButton.disabled =
                            false;

                    }

                };


                muteButton.onclick =
                    async function() {

                    if (!room) {
                        return;
                    }


                    muted = !muted;


                    await room
                        .localParticipant
                        .setMicrophoneEnabled(
                            !muted
                        );


                    if (muted) {

                        muteButton.innerText =
                            "🔇 فتح المايك";

                        status.innerText =
                            "🔇 المايك مكتوم";

                    } else {

                        muteButton.innerText =
                            "🎤 كتم المايك";

                        status.innerText =
                            "🟢 متصل — احچي ويا المساعد";

                    }

                };


                endButton.onclick =
                    function() {

                    if (room) {

                        room.disconnect();

                        room = null;

                    }

                    status.innerText =
                        "🔴 تم إنهاء المحادثة";

                    resetInterface();

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
            height=390,
            scrolling=False,
        )


    except Exception as e:

        st.error(
            "حدث خطأ أثناء تشغيل المساعد"
        )

        st.code(str(e))


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        AI Executive Assistant • Powered by LiveKit
    </div>
    """,
    unsafe_allow_html=True,
)
