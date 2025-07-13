import streamlit as st
import pywhatkit as kit
import pyautogui
import datetime
import time
import os
from dotenv import load_dotenv
import asyncio

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error("⚠️ GEMINI_API_KEY not found in .env")
    st.stop()

provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash"
)
set_tracing_disabled(disabled=True)

whatsapp_agent = Agent(
    name="WhatsApp Post Writer",
    tools=[],
    model=model,
    instructions=(
        "You are a professional copywriter creating WhatsApp broadcast messages. "
        "Donot add *asteriks for headings, use # for headings"
        "Use *asterisks* ONLY for bolding full keywords or small phrases (not full paragraphs). "
        "Do not mix bold and normal words in a way that breaks formatting. "
        "Avoid using partial bold within sentences that could break markdown rendering in WhatsApp. "
        "Avoid markdown other than asterisks. Do not use emojis, hashtags, or markdown titles."
    )
)

# ==== WhatsApp send function (auto send) ====
def send_to_whatsapp_direct(message: str, phone_number: str = "+923001234567"):
    now = datetime.datetime.now()
    try:
        kit.sendwhatmsg(phone_number, message, now.hour, now.minute + 1, wait_time=10)
        time.sleep(15)  # Wait for WhatsApp Web to open
        pyautogui.press("enter")  # Automatically press "Send"
        return {"success": True, "message": "✅ Message sent directly on WhatsApp!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==== Streamlit UI ====
st.set_page_config(page_title="WhatsApp Auto Post Bot", page_icon="💬")
st.title("💬 WhatsApp Channel Post Bot")
st.write("Generate social media content and send it to your WhatsApp automatically.")

# Input fields
prompt = st.text_area("Enter post topic or description:")
whatsapp_number = st.text_input("Enter your WhatsApp number (with country code)", "+923001234567")

# Button to generate and send
if st.button("✍️ Generate & Send to WhatsApp"):
    if not prompt or not whatsapp_number:
        st.warning("⚠️ Please enter both topic and phone number.")
    else:
        with st.spinner("🤖 Generating post..."):
            try:
                result = asyncio.run(Runner.run(
                    starting_agent=whatsapp_agent,
                    input=prompt
                ))
                content = result.final_output.strip()

                if not content:
                    st.error("❌ No content generated.")
                else:
                    st.subheader("📄 Generated Post")
                    st.code(content)

                    send_result = send_to_whatsapp_direct(content, whatsapp_number)
                    if send_result["success"]:
                        st.success(send_result["message"])
                    else:
                        st.error(f"💥 Failed to send: {send_result['error']}")
            except Exception as e:
                st.error(f"💥 Error: {str(e)}")

