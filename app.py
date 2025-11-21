import streamlit as st
from openai import OpenAI
from utils.ocr import extract_text_from_image
from utils.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
import os

# ----------------------------------
# Load environment + OpenAI client
# ----------------------------------
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------------
# Streamlit Page Settings
# ----------------------------------
st.set_page_config(
    page_title="Structify",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ----------------------------------
# Consistent colors 
# ----------------------------------
st.markdown("""
<style>

/* Make all markdown text readable in dark mode */
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li,
[data-testid="stMarkdown"] span {
    color: inherit !important;
}

/* Fix sidebar dimming */
section[data-testid="stSidebar"] * {
    color: inherit !important;
}

/* Ensure list items don't fade */
li {
    opacity: 1 !important;
}

/* Fix label text in dark mode */
label, .stTextInput label {
    color: inherit !important;
}

/* Ensure chat input stays readable */
.stChatInputContainer * {
    color: inherit !important;
}

/* Buttons remain readable */
.stButton button {
    color: inherit !important;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------
# Sidebar
# ----------------------------------
with st.sidebar:
    st.markdown("""
        <div style="padding-top: 10px;">
            <h1 style="font-size: 28px; margin-bottom: 4px;"> Structify </h1>
            <p style="font-size: 16px; font-weight: 500; color:#444;">
                Your AI-powered Product Story Generator turning messy information into structured, actionable product work
            </p>
            <hr style="margin-top: 10px; margin-bottom: 20px;">
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h3 style="font-size: 20px;">👋 Hello!</h3>
        <p style="font-size: 15px; line-height: 1.55; color: #333; margin-top: -5px;">
            Got scattered notes? Half-baked meeting minutes?  
            A screenshot you took at 9:47 PM so you “don’t forget"?  
        </p>

        <p style="font-size: 15px; line-height: 1.55; color: #333;">
            Drop in whatever you’ve got:
            <ul style="margin-top: 5px; margin-bottom: 5px;">
                <li>Slack threads</li>
                <li>Meeting notes</li>
                <li>Screenshots</li>
                <li>Transcripts</li>
                <li>Emails</li>
            </ul>
        </p>

        <p style="font-size: 15px; line-height: 1.55; color: #333; margin-top: 10px;">
            I’ll convert the chaos into clean, structured:
            <ul>
                <li>User stories</li>
                <li>Summaries</li>
                <li>Acceptance criteria</li>
                <li>Agile subtasks</li>
            </ul>
        </p>

        <p style="font-size: 15px; line-height: 1.55; color: #333; margin-top: 15px;">
            Just pick your input type on the right and I’ll take it from there.
        </p>

        <hr style="margin-top: 25px;">

        <p style="font-size: 13px; color: #777; text-align: center;">
            Powered by <strong>Streamlit</strong> ✕ <strong>OpenAI</strong>
        </p>
    """, unsafe_allow_html=True)


# ----------------------------------
# Main Title
# ----------------------------------
st.title("Let's go!")
#st.markdown("""
#Turn *messy inputs* → **polished, ready-to-paste user stories**.

#Paste notes, upload screenshots, or chat to refine your stories just like ChatGPT.
#""")

# ----------------------------------
# Section 1 — Input Area
# ----------------------------------
input_type = st.selectbox("Choose Input Type:", ["Paste Text", "Upload Screenshot"])
raw_text = ""

if input_type == "Paste Text":
    raw_text = st.text_area(
        "Paste your Slack messages, meeting notes, transcripts, or email threads:",
        height=280,
        placeholder="Paste anything messy here..."
    )

elif input_type == "Upload Screenshot":
    st.markdown("### Upload a screenshot")
    file = st.file_uploader("PNG or JPG (max 10MB):", type=["png", "jpg", "jpeg"])

    if file:
        with st.container():
            st.markdown("""
                <div style='background:#FAFAFA; padding:18px; border-radius:12px;
                    border:1px solid #DDD; box-shadow:0 2px 6px rgba(0,0,0,0.05);
                    margin-top:10px; text-align:center;'>
            """, unsafe_allow_html=True)

            st.image(file, caption="Uploaded Screenshot", width=420)

            st.markdown("</div>", unsafe_allow_html=True)

        raw_text = extract_text_from_image(file)
        st.success("Text extracted from screenshot!")

        with st.expander("Show Extracted Text"):
            st.text_area("", raw_text, height=200)


# ----------------------------------
# Section 2 — Generate Story
# ----------------------------------
if st.button("Generate Story", key="generate"):
    if not raw_text.strip():
        st.error("Please enter or upload some content first.")
    else:
        with st.spinner("Turning chaos into a clean user story..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": raw_text}
                ]
            )

        story = response.choices[0].message.content

        # Save initial story
        st.session_state.story = story
        st.session_state.story_versions = ["Story v1:\n" + story]
        st.session_state.chat_history = []

        st.subheader("Generated Story")
        st.markdown(story)

# ----------------------------------
# Section 3 — ChatGPT-style Refinement
# ----------------------------------
if "story" in st.session_state and st.session_state.story:

    #st.markdown("---")
    #st.subheader("Refine Your Story")

    # Show chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input
    user_msg = st.chat_input("Ask to refine, improve, shorten, expand, or reformat the story...")

    if user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})

        refine_prompt = (
            f"Here is the current story:\n\n{st.session_state.story}\n\n"
            f"User request: {user_msg}\n\n"
            "Return the FULL updated story. Do NOT explain your changes — just show the updated story."
        )

        with st.chat_message("assistant"):
            with st.spinner("Updating story..."):
                refine_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You refine user stories with expert PM clarity."},
                        {"role": "assistant", "content": st.session_state.story},
                        {"role": "user", "content": refine_prompt}
                    ]
                )

                updated_story = refine_response.choices[0].message.content
                st.markdown(updated_story)

        # Save as new version
        st.session_state.story = updated_story
        st.session_state.story_versions.append(
            f"Story v{len(st.session_state.story_versions)+1}:\n{updated_story}"
        )

        # Add assistant reply
        st.session_state.chat_history.append({"role": "assistant", "content": updated_story})


# ----------------------------------
# Section 4 — Version History + Download
# ----------------------------------
if "story_versions" in st.session_state:
    st.markdown("---")
    st.subheader("Story Version History")

    for version in st.session_state.story_versions:
        with st.expander(version.split("\n")[0]):
            st.write("\n".join(version.split("\n")[1:]))

    st.download_button(
        "⬇ Download Final Story",
        data=st.session_state.story,
        file_name="final_story.txt",
        mime="text/plain"
    )
