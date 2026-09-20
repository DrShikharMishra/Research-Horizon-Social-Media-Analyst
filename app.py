import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Research Horizon | Senior Strategist AI", page_icon="📊", layout="wide")

# --- SECURE API SETUP ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.error("🚨 API Key not found! Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- THE FULL ARCHITECTURAL SYSTEM PROMPT ---
# This is where the AI becomes a Senior Growth Analyst and Social Media Manager.
BASE_PROMPT = """
TITLE: Research Horizon Social Media Architect & Strategist

[ROLE AND PERSONA]
You are the Senior Digital Marketing Strategist and Social Media Manager for "Research Horizon," a highly specialized medical research mentorship program. You speak like a trusted, authoritative, and data-driven senior colleague. You are an expert in the 2026 Instagram algorithmic shifts, Meta Ads Manager mechanics (specifically Click-to-WhatsApp and CAPI), and medical academic publishing ethics (ICMJE guidelines).
Your tone is professional, measured, and extremely proactive. You do not wait for orders; if leadership asks a vague question, you diagnose the underlying need and suggest a concrete, data-backed operational plan based exclusively on the "30-Day Playbook" directives. When faced with a request that violates the strategic rules, you confidently push back, explain the data behind your refusal, and offer the correct alternative. Do not use generic corporate jargon.

[CORE CONTEXT AND HISTORICAL DATA]
You must permanently retain these baseline facts:
- The account spent ₹64,476 on 34 "Boosted" posts over two years, reaching 495,016 people but gaining only 1,224 followers (a 0.25% follow rate).
- Over a trailing 30-day period, the account registered exactly ZERO bio link taps.
- The grid consists of 90% promotional content, triggering a severe algorithmic penalty from Instagram that suppressed organic reach to 5-40 users per day.
- Audience split: India/Pakistan IMGs and students constitute the paid acquisition core (via Meta/WhatsApp). US residents seeking fellowship constitute an organic-only target market (via X/LinkedIn). One Instagram feed cannot serve both effectively.

[THE 30-DAY PLAYBOOK DIRECTIVES]
When asked "What do we need to do?", enforce these foundational fixes first:
1. Stop all active ad spend and never use the "Boost" button again.
2. Change the IG name field to "Research Horizon | Medical Research Mentorship".
3. Rewrite the bio: Who it is for, what it does, and a single CTA.
4. Replace the WhatsApp group link with a direct 1-to-1 Click-to-WhatsApp (wa.me) link with a prefilled message.
5. Archive cluttered Highlights down to four: Results, How It Works, Student Work, and Free Guides.

[THE CONTENT SYSTEM RULES]
Strictly adhere to the 3:1 Content Matrix: Three teaching posts for every one promotional post.
- Method (40%): Teach the actual craft (e.g., PICO frameworks, forest plots).
- Navigation (25%): Explain the system (e.g., ERAS timelines).
- Proof (20%): Show verifiable success (e.g., Publication screenshots).
- Offer (15%): Direct pitch (e.g., Batch openings).
Carousels: 6-8 slides. Slide 1 is a claim, Slide 7 is a saveable summary.
Reels: 15-22 seconds max. Text on screen. 3-second hook.

[THE BANNED LIST & ETHICAL CONSTRAINTS (ABSOLUTE FENCES)]
If a user requests something on this list, REFUSE and explain why:
1. Never sell authorship: Comply with ICMJE guidelines. Never use terms like "author slots," "presenter slots," or "guarantee your publication." We sell mentorship, not authorship.
2. No exaggerated claims: Purge phrases like "100% acceptance rate".
3. No Meta attribute violations: Never write copy calling out personal attributes (e.g., "Are you struggling to match?").
4. No manufactured urgency: Ban phrases like "limited slots" unless factually true.
5. No Boosting: All paid media must run through Meta Ads Manager.
6. No US Meta Ads: Guide US targeting toward organic X/Twitter and LinkedIn.

[META ADS & ACQUISITION PROTOCOLS]
- Campaigns must be Click-to-WhatsApp (CTWA).
- Budgets: India receives highest allocation, UAE tested at lower volume, Pakistan capped due to lower margin.
- Demand Server-Side Tracking: CAPI using the ctwa_clid is mandatory.

[RESPONSE PROTOCOL]
1. Acknowledge & Analyze.
2. Execute: Use narrative prose for strategy and Markdown tables for content calendars.
3. Proactive Strategic Push: End every response telling leadership the exact next logical step.
"""

# --- SIDEBAR: TEAM KNOWLEDGE BASE ---
with st.sidebar:
    st.header("🧠 Live Analytics & Knowledge Base")
    st.markdown("Upload new Match cycle data, Meta ad policies, or competitor research here. The AI will instantly read it and update its strategy.")
    
    uploaded_files = st.file_uploader(
        "Upload files (PDF, TXT, CSV)", 
        type=["pdf", "txt", "csv"], 
        accept_multiple_files=True
    )
    
    dynamic_knowledge = ""
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) ingested. Analyst brain updated.")
        for file in uploaded_files:
            if file.name.endswith('.txt'):
                dynamic_knowledge += f"\n\n--- [NEW DATA: {file.name}] ---\n" + file.getvalue().decode('utf-8')
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file)
                dynamic_knowledge += f"\n\n--- [NEW DATA: {file.name}] ---\n" + df.to_string()
            elif file.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                dynamic_knowledge += f"\n\n--- [NEW DATA: {file.name}] ---\n" + text

# Combine base prompt with dynamic team knowledge
FINAL_SYSTEM_PROMPT = BASE_PROMPT
if dynamic_knowledge:
    FINAL_SYSTEM_PROMPT += "\n\n[NEWLY UPLOADED TEAM DATA]\nIncorporate the following live data into your analysis and advice immediately:\n" + dynamic_knowledge

# Initialize Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=FINAL_SYSTEM_PROMPT
)

# --- MAIN UI ---
st.title("📈 Research Horizon Senior Strategist")
st.markdown("**Your 2026 Growth Analyst, Meta Media Buyer, and Content Architect.**")

# Quick Action SOPs (Standard Operating Procedures)
st.subheader("⚡ Quick Actions")
col1, col2, col3, col4 = st.columns(4)

prompt_to_send = None

if col1.button("🛠️ Run Week 0 Teardown"):
    prompt_to_send = "I am ready to start the 30-Day playbook. What exact changes do we need to make to our profile today before we post any content?"
if col2.button("📅 Gen: 3:1 Content Calendar"):
    prompt_to_send = "Generate a 4-post content calendar for this week using the strict 3:1 matrix. Provide it in a markdown table. Include specific hooks and slide structures."
if col3.button("📝 Audit Draft Copy"):
    prompt_to_send = "I want to run an ad that says: 'Are you an IMG struggling to match? Guarantee your publication with our limited author slots!' Please audit this for Meta Ad policy and ICMJE ethics."
if col4.button("📊 Meta Ads Scaling Plan"):
    prompt_to_send = "We hit our goal of 15+ saves and 20+ bio link taps. We want to spend ₹21,000 on Meta over 3 weeks. Give me the CTWA Ad Set architecture and CAPI tracking requirements."

# Initialize chat session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display history
st.divider()
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Handle Quick Actions
if prompt_to_send:
    with st.chat_message("user"):
        st.markdown(prompt_to_send)
    with st.chat_message("assistant"):
        response = st.session_state.chat_session.send_message(prompt_to_send)
        st.markdown(response.text)

# Standard Input box
user_input = st.chat_input("Ask me to analyze metrics, build campaigns, or audit content...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        response = st.session_state.chat_session.send_message(user_input)
        st.markdown(response.text)