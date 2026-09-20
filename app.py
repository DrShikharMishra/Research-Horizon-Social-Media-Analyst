import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd
import io
import datetime
from PIL import Image

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Research Horizon | Ops App", page_icon="📊", layout="wide")

# --- SECURE API SETUP ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.error("🚨 API Key not found! Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- INITIALIZE LEAD TRACKER DATABASE (Session State) ---
if 'leads_db' not in st.session_state:
    st.session_state.leads_db = pd.DataFrame(columns=[
        "Date", "Channel", "Source", "Country", "Stage", "Specialty", 
        "Cycle", "Prior Research", "Question", "Qualified", "Status", "Lost Reason"
    ])

# --- SYSTEM PROMPT (Brand Brain) ---
BASE_PROMPT = """
TITLE: Research Horizon Social Media Architect & Strategist

[ROLE AND PERSONA]
You are the Senior Digital Marketing Strategist and Social Media Manager for "Research Horizon." 
You strictly enforce the 30-Day Playbook and ICMJE ethical guidelines.
Never sell authorship. Never recommend the Instagram "Boost" button. 
Advise exclusively on Click-to-WhatsApp (CTWA) Meta Ads for India/Pakistan/UAE.

[BRAND BRAIN & BANNED PHRASES]
Refuse to generate copy containing: "guaranteed publication", "100% acceptance rate", "author slots", "limited slots", or any emojis acting as spam. 
Tone: A senior resident explaining something clearly to a junior. Specific over grand. Numbers over adjectives. Teaching posts end with no call to action.

[IMAGE ANALYSIS PROTOCOL]
If the user uploads an image, analyze it ruthlessly:
- If it is an ad creative: Check it for the banned phrases above. Ensure there is no manufactured urgency or personal attribute calling (e.g. "Are you struggling?").
- If it is a Meta Ads screenshot: Read the numbers (Spend, CPC, CTR) and check if they hit our CAC ceilings. Give actionable advice.
"""

# --- SIDEBAR KNOWLEDGE BASE ---
with st.sidebar:
    st.header("🧠 Live Knowledge Base")
    uploaded_files = st.file_uploader("Upload files (PDF, TXT, CSV)", type=["pdf", "txt", "csv"], accept_multiple_files=True)
    dynamic_knowledge = ""
    if uploaded_files:
        for file in uploaded_files:
            if file.name.endswith('.txt'):
                dynamic_knowledge += f"\n[DATA: {file.name}]\n" + file.getvalue().decode('utf-8')
            elif file.name.endswith('.csv'):
                dynamic_knowledge += f"\n[DATA: {file.name}]\n" + pd.read_csv(file).to_string()
            elif file.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
                text = "".join([page.extract_text() + "\n" for page in pdf_reader.pages])
                dynamic_knowledge += f"\n[DATA: {file.name}]\n" + text

FINAL_SYSTEM_PROMPT = BASE_PROMPT + ("\n[NEW DATA]\n" + dynamic_knowledge if dynamic_knowledge else "")
model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=FINAL_SYSTEM_PROMPT)

# --- MAIN UI: TWO TABS ---
st.title("📈 Research Horizon | Internal Ops")
tab1, tab2 = st.tabs(["🤖 AI Strategist & Content Planner", "📋 Phase 1: Lead Tracker"])

# ==========================================
# TAB 1: THE STRATEGIST (Now with Vision)
# ==========================================
with tab1:
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    prompt_to_send = None

    if col1.button("🛠️ Daily Brief & Teardown"):
        prompt_to_send = "Give me the Daily Brief. What is our number one priority today based on the 30-day organic rebuild rules?"
    if col2.button("📅 Gen: 3:1 Content Calendar"):
        prompt_to_send = "Generate a 4-post content calendar for this week using the strict 3:1 matrix (Method, Navigation, Proof, Offer)."
    if col3.button("📝 Extract from Founder Transcript"):
        prompt_to_send = "I need you to act as the Transcript Extractor. I will paste a transcript next. Prepare to extract teachable claims, propose pillars, and isolate specific hooks."
    if col4.button("📊 Meta Ads Scaling Plan"):
        prompt_to_send = "Give me the Meta Ads Campaign Console rules: CPC ceilings by market (India, Pakistan, Gulf) and the ABO budget architecture."

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])
    
    # Display chat history
    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            # If the user uploaded images previously, they will be in the parts list (we only render text here for simplicity)
            for part in message.parts:
                if hasattr(part, 'text'):
                    st.markdown(part.text)

    # --- IMAGE UPLOADER FOR CHAT ---
    st.divider()
    vision_files = st.file_uploader("🖼️ Upload Ad Creatives or Data Screenshots for the AI to audit:", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    # Text Input
    user_input = st.chat_input("Ask me to analyze metrics, audit the uploaded images, or build campaigns...")
    
    # Combine user input from either quick action or text bar
    final_input = prompt_to_send if prompt_to_send else user_input

    if final_input:
        # Prepare the payload (combining text and images)
        payload = [final_input]
        
        if vision_files:
            for f in vision_files:
                img = Image.open(f)
                payload.append(img)
                
        with st.chat_message("user"):
            st.markdown(final_input)
            if vision_files:
                cols = st.columns(len(vision_files))
                for idx, f in enumerate(vision_files):
                    cols[idx].image(f, width=200)
                    
        with st.chat_message("assistant"):
            response = st.session_state.chat_session.send_message(payload)
            st.markdown(response.text)

# ==========================================
# TAB 2: LEAD TRACKER (PHASE 1 APP)
# ==========================================
with tab2:
    st.markdown("### 📥 Fast Lead Capture")
    st.markdown("*The form must be completable in under 30 seconds on a phone, one-handed.*")
    
    with st.form("lead_capture_form", clear_on_submit=True):
        colA, colB, colC = st.columns(3)
        with colA:
            channel = st.radio("Channel", ["WhatsApp", "Instagram DM"], horizontal=True)
            source = st.selectbox("Source", ["Organic", "Ad: India", "Ad: Gulf", "Ad: Pakistan", "Referral", "Unknown"])
            country = st.selectbox("Country", ["India", "Pakistan", "UAE", "Saudi Arabia", "USA", "Other"])
        with colB:
            stage = st.selectbox("Training Stage", ["Student", "Intern", "Resident", "Graduated", ""])
            specialty = st.text_input("Specialty (e.g., Cardiology, GI)")
            cycle = st.selectbox("Match Cycle", ["2027", "2028", "2029", "Fellowship", "N/A"])
        with colC:
            research = st.selectbox("Prior Research", ["None", "Case report", "Abstract", "Publication", ""])
            question = st.text_input("Their Question (Feeds Content Bank)")
            status = st.selectbox("Pipeline Status", ["New", "Qualified", "Quoted", "Enrolled", "Lost"])
        
        lost_reason = ""
        if status == "Lost":
            lost_reason = st.selectbox("Lost Reason", ["Price", "Timing", "Went elsewhere", "Went quiet", "Not a fit"])

        submit_lead = st.form_submit_button("➕ Save Lead")

        if submit_lead:
            is_qualified = bool(stage != "" and specialty != "" and research != "")
            if status == "New" and is_qualified:
                status = "Qualified" 

            new_lead = pd.DataFrame([{
                "Date": datetime.date.today(),
                "Channel": channel, "Source": source, "Country": country,
                "Stage": stage, "Specialty": specialty, "Cycle": cycle,
                "Prior Research": research, "Question": question, 
                "Qualified": is_qualified, "Status": status, "Lost Reason": lost_reason
            }])
            st.session_state.leads_db = pd.concat([st.session_state.leads_db, new_lead], ignore_index=True)
            st.success("Lead captured successfully!")

    st.divider()
    st.markdown("### 📊 Active Pipeline Kanban")
    k1, k2, k3, k4, k5 = st.columns(5)
    
    def display_leads(status_filter, column):
        filtered = st.session_state.leads_db[st.session_state.leads_db["Status"] == status_filter]
        column.markdown(f"**{status_filter} ({len(filtered)})**")
        for _, row in filtered.iterrows():
            with column.container(border=True):
                st.caption(f"{row['Date']} | {row['Country']}")
                st.write(f"**{row['Stage']} - {row['Specialty']}**")
                st.caption(f"Src: {row['Source']} | Qual: {'✅' if row['Qualified'] else '❌'}")

    display_leads("New", k1)
    display_leads("Qualified", k2)
    display_leads("Quoted", k3)
    display_leads("Enrolled", k4)
    display_leads("Lost", k5)

    st.divider()
    st.markdown("### 💾 Raw Data Export")
    st.dataframe(st.session_state.leads_db, use_container_width=True)
