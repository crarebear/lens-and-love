import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Lens & Love Academy",
    page_icon="📸",
    layout="centered"
)

# --- FIREBASE SETUP (PRODUCTION) ---
# This version looks for the password in Streamlit's Secure Cloud Vault
if not firebase_admin._apps:
    try:
        # Check if we are on Streamlit Cloud
        if 'firebase' in st.secrets:
            key_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for local: Use the local file if it exists
            # (You must have firebase_key.json in the folder for this to work locally)
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
            
    except Exception as e:
        st.error(f"🔥 Setup Error: {e}. If you are on the web, did you set up the Secrets?")
        st.stop()

db = firestore.client()

# --- DB FUNCTIONS ---
def get_user_progress(user_id="wife_account"):
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        default_data = {'xp': 0, 'completed_lessons': []}
        doc_ref.set(default_data)
        return default_data

def update_user_progress(user_id, xp, completed_lessons):
    doc_ref = db.collection('users').document(user_id)
    doc_ref.update({
        'xp': xp,
        'completed_lessons': completed_lessons
    })

# --- INITIALIZE SESSION ---
USER_ID = "my_wife" 

if 'initialized' not in st.session_state:
    user_data = get_user_progress(USER_ID)
    st.session_state['xp'] = user_data.get('xp', 0)
    st.session_state['completed_lessons'] = user_data.get('completed_lessons', [])
    st.session_state['initialized'] = True

# --- CURRICULUM ---
curriculum = {
    "Module 1: The Light Chaser": {
        "Lesson 1: Golden Hour": {
            "content": """### 🌅 What is the Golden Hour? \n\n It is the hour right after sunrise or right before sunset. The light is soft, warm, and golden. \n\n **Why it matters:** No harsh shadows under eyes, glowing garden.""",
            "quiz_question": "When is the best time to photograph the dogs?",
            "quiz_options": ["Noon", "Golden Hour", "Midnight"],
            "correct_answer": "Golden Hour",
            "challenge": "Take a photo of a plant in the backyard at 5:00 PM."
        },
        "Lesson 2: Window Light": {
            "content": """### 🪟 The Window Studio \n\n Turn off lamps. Use a big window as your light source. \n\n **Tip:** Don't put the baby with her back to the window (she will be dark). Put the window to her side.""",
            "quiz_question": "To get a sparkle in the baby's eye:",
            "quiz_options": ["Use flash", "Face toward window", "Turn on lamps"],
            "correct_answer": "Face toward window",
            "challenge": "Capture a portrait with a 'catchlight' in her eyes."
        }
    },
    "Module 2: The Action Hero": {
        "Lesson 1: Freezing Motion": {
            "content": """### 🏃‍♂️ Shutter Speed \n\n Fast shutter (1/500+) freezes the dog running. Slow shutter (1/60) is for sleeping babies.""",
            "quiz_question": "The dog is running. What shutter speed?",
            "quiz_options": ["1/60 (Slow)", "1/1000 (Fast)"],
            "correct_answer": "1/1000 (Fast)",
            "challenge": "Take a sharp photo of a moving pet."
        }
    },
    "Module 3: Portrait Perfection": {
        "Lesson 1: The Eyes Have It": {
            "content": """### 👁️ Focus on the Eyes \n\n If the nose is sharp but the eyes are blurry, the photo is ruined. \n\n **Technique:** Tap the screen right on the baby's eye before snapping.""",
            "quiz_question": "Where must the focus always be?",
            "quiz_options": ["The nose", "The eyes", "The background"],
            "correct_answer": "The eyes",
            "challenge": "Take a super close-up of the baby's face with sharp eyes."
        },
        "Lesson 2: Fill the Frame": {
            "content": """### 🖼️ Fill the Frame \n\n Don't leave empty space above her head. \n\n **The Fix:** Get closer. Zoom with your feet.""",
            "quiz_question": "What does 'Fill the Frame' mean?",
            "quiz_options": ["Zoom out", "Get close so the subject takes up the image", "Add a border"],
            "correct_answer": "Get close so the subject takes up the image",
            "challenge": "Take a portrait where the head almost touches the top edge."
        }
    }
}

# --- UI FUNCTIONS ---
def draw_sidebar():
    st.sidebar.title("📸 Lens & Love")
    level = 1 + (st.session_state['xp'] // 50)
    st.sidebar.markdown(f"**Level {level} Photographer**")
    st.sidebar.markdown(f"**XP:** {st.session_state['xp']} ⭐")
    st.sidebar.progress(min(st.session_state['xp'] / 100, 1.0))
    st.sidebar.markdown("---")
    
    mod = st.sidebar.selectbox("Module", list(curriculum.keys()))
    less = st.sidebar.radio("Lesson", list(curriculum[mod].keys()))
    return mod, less

def render_lesson(module, lesson):
    data = curriculum[module][lesson]
    st.title(module)
    st.subheader(lesson)
    
    if lesson in st.session_state['completed_lessons']:
        st.success("✅ Completed")
    
    st.markdown("---")
    st.markdown(data['content'])
    st.markdown("---")
    
    st.subheader("Pop Quiz")
    ans = st.radio("Answer:", data['quiz_options'], key=lesson)
    
    if st.button("Check", key=f"btn_{lesson}"):
        if ans == data['correct_answer']:
            st.balloons()
            if lesson not in st.session_state['completed_lessons']:
                st.session_state['xp'] += 10
                st.session_state['completed_lessons'].append(lesson)
                update_user_progress(USER_ID, st.session_state['xp'], st.session_state['completed_lessons'])
                st.rerun()
        else:
            st.error("Try again!")

    st.markdown("---")
    st.subheader(f"Quest: {data['challenge']}")
    st.file_uploader("Upload result", type=['jpg', 'png'])

if __name__ == "__main__":
    main_mod, main_less = draw_sidebar()
    render_lesson(main_mod, main_less)