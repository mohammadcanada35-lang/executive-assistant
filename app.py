import os
import streamlit as st
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


if not LIVEKIT_URL:
    st.error("LIVEKIT_URL غير موجود")
    st.stop()

if not LIVEKIT_API_KEY:
    st.error("LIVEKIT_API_KEY غير موجود")
    st.stop()

if not LIVEKIT_API_SECRET:
    st.error("LIVEKIT_API_SECRET غير موجود")
    st.stop()


st.success("تم الاتصال بإعدادات LiveKit بنجاح ✅")


if st.button("اختبار LiveKit"):
    try:
        token = (
            api.AccessToken(
                LIVEKIT_API_KEY,
                LIVEKIT_API_SECRET,
            )
            .with_identity("user")
            .with_name("User")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room="executive-assistant",
                )
            )
            .to_jwt()
        )

        st.success("تم إنشاء اتصال LiveKit بنجاح ✅")
        st.code(token)

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
