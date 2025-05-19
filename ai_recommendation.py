# ai_recommendation.py
import google.generativeai as genai
import streamlit as st
from datetime import datetime

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


def get_ai_recommendation(user_input):
    """Get yoga recommendations using Google Gemini with enhanced parameters"""
    prompt = f"""
     As an expert yoga therapist with 20 years experience, create a personalized yoga plan considering:

     **Personal Profile**
     - Age: {user_input['age']}
     - Gender: {user_input['gender']}
     - Weight: {user_input['weight']} kg
     - Height: {user_input['height']} cm
     - BMI: {user_input['weight'] / ((user_input['height'] / 100) ** 2):.1f}

     **Health Status**
     - Fitness Level: {user_input['fitness_level']}
     - Chronic Conditions: {', '.join(user_input['health_conditions'])}
     - Recent Injuries: {', '.join(user_input['injuries'])}
     - Sleep Quality: {user_input['sleep_quality']}/5
     - Stress Level: {user_input['stress_level']}/5
     - Medication: {user_input['medications']}

     **Lifestyle Factors**
     - Daily Activity: {user_input['activity_level']}
     - Available Time: {user_input['time_available']} mins/day
     - Preferred Style: {user_input['yoga_style']}
     - Equipment: {', '.join(user_input['equipment'])}

     **Goals & Preferences**
     - Primary Goal: {user_input['goals']}
     - Secondary Goals: {', '.join(user_input['secondary_goals'])}
     - Menstrual Phase: {user_input.get('menstrual_phase', 'N/A')}
     - Preference: {user_input['intensity_preference']} intensity

     Provide:
     1. 4 personalized poses with timing recommendations
     2. Modifications for health constraints
     3. Breathing technique suggestions
     4. Ideal practice time of day
     5. Progress milestones
     6. Equipment usage tips

     Format with markdown headers and bullet points.
     """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return get_fallback_recommendations(user_input)


def get_fallback_recommendations(user_input):
    """Enhanced local recommendations"""
    base_poses = {
        "Beginner": [
            "**Cat-Cow Stretch** (5-10 mins): Improves spinal flexibility",
            "**Legs-Up-the-Wall** (5-15 mins): Reduces stress and swelling"
        ],
        "Intermediate": [
            "**Sun Salutations** (10-15 rounds): Full-body warmup",
            "**Bridge Pose** (3-5 mins): Strengthens back muscles"
        ],
        "Advanced": [
            "**Wheel Pose** (1-3 mins): Opens chest and shoulders",
            "**Forearm Stand** (30-60 secs): Builds core strength"
        ]
    }

    modifications = []
    if "Back Pain" in user_input["health_conditions"]:
        modifications.append("Use yoga block support in forward folds")
    if user_input["time_available"] < 20:
        modifications.append("Focus on short flow sequences")

    return "\n\n".join([
        "## Personalized Recommendations",
        "### Suggested Poses:",
        *base_poses.get(user_input["fitness_level"], []),
        "### Modifications:"
        ###*modifications if modifications else ["No modifications needed"]
    ])


def show_recommendation_ui():
    """Enhanced Streamlit input form with 15+ parameters"""
    with st.form("user_profile"):
        st.subheader("🧘 Advanced Yoga Profile")

        with st.expander("Basic Information", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.slider("Age", 18, 80, 30)
                weight = st.number_input("Weight (kg)", 40, 200, 65)
            with col2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                height = st.number_input("Height (cm)", 140, 220, 170)
            with col3:
                fitness_level = st.selectbox(
                    "Fitness Level",
                    ["Beginner", "Intermediate", "Advanced"]
                )
                activity_level = st.selectbox(
                    "Daily Activity Level",
                    ["Sedentary", "Light", "Moderate", "Active"]
                )

        with st.expander("Health Details"):
            col1, col2 = st.columns(2)
            with col1:
                health_conditions = st.multiselect(
                    "Health Conditions",
                    ["Hypertension", "Diabetes", "Arthritis",
                     "Osteoporosis", "Migraines", "Anxiety", "None"]
                )
                injuries = st.multiselect(
                    "Recent Injuries (last 6 months)",
                    ["Neck", "Shoulder", "Back", "Knee", "Wrist", "None"]
                )
            with col2:
                stress_level = st.slider("Stress Level (1-5)", 1, 5, 3)
                sleep_quality = st.slider("Sleep Quality (1-5)", 1, 5, 3)
                medications = st.text_input("Current Medications")

        with st.expander("Preferences & Goals"):
            col1, col2 = st.columns(2)
            with col1:
                goals = st.selectbox(
                    "Primary Goal",
                    ["Stress Relief", "Weight Management", "Mobility",
                     "Strength", "Rehabilitation", "Spiritual Growth"]
                )
                secondary_goals = st.multiselect(
                    "Secondary Goals",
                    ["Better Sleep", "Improved Posture", "Balance",
                     "Flexibility", "Mindfulness", "Pain Relief"]
                )
                yoga_style = st.selectbox(
                    "Preferred Style",
                    ["Hatha", "Vinyasa", "Restorative", "Yin",
                     "Ashtanga", "Kundalini", "No Preference"]
                )
            with col2:
                time_available = st.slider("Time Available (mins/day)", 10, 120, 30)
                equipment = st.multiselect(
                    "Available Equipment",
                    ["Yoga Mat", "Blocks", "Strap", "Bolster",
                     "Blanket", "Chair", "None"]
                )
                intensity_preference = st.selectbox(
                    "Intensity Preference",
                    ["Gentle", "Moderate", "Challenging"]
                )
                if gender == "Female":
                    menstrual_phase = st.selectbox(
                        "Menstrual Phase (optional)",
                        ["Follicular", "Ovulation", "Luteal",
                         "Menses", "Prefer not to say"],
                        index=4
                    )

        if st.form_submit_button("Generate AI Recommendations"):
            params = {
                "age": age,
                "gender": gender,
                "weight": weight,
                "height": height,
                "fitness_level": fitness_level,
                "activity_level": activity_level,
                "health_conditions": health_conditions,
                "injuries": injuries,
                "stress_level": stress_level,
                "sleep_quality": sleep_quality,
                "medications": medications,
                "goals": goals,
                "secondary_goals": secondary_goals,
                "yoga_style": yoga_style,
                "time_available": time_available,
                "equipment": equipment,
                "intensity_preference": intensity_preference
            }
            if gender == "Female":
                params["menstrual_phase"] = menstrual_phase

            return params
    return None