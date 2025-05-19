import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
from tensorflow.keras.models import load_model
from streamlit_option_menu import option_menu
from yoga_pose_library import integrate_pose_library
from ai_recommendation import get_ai_recommendation, show_recommendation_ui
from yoga_nidra import show_yoga_nidra_interface
from posture_corrector import get_biomechanical_feedback
from ppg_processor import HeartRateMonitor
from emg_visualizer import draw_muscle_overlay
from user_profile import UserProfile
from session_tracker import SessionTracker
from feedback_system import FeedbackSystem, show_feedback_ui
from team import show_team_page

# ====================== APP CONFIGURATION ======================
st.set_page_config(
    page_title="Swasthaverse- Yoga Companion",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Initialize session states
if 'hr_monitor' not in st.session_state:
    st.session_state.update({
        'hr_monitor': HeartRateMonitor(),
        'webcam_active': False,
        'show_hr': False,
        'show_emg': False,
        'emg_opacity': 0.4,
        'user_profile': UserProfile().load_profile(),
        'session_tracker': SessionTracker(),
        'session_start': None,
        'feedback_system': FeedbackSystem()
    })

# ====================== POSE DETECTION SETUP ======================
MODEL_PATH = "C:\\Users\\shaur\\OneDrive\\Desktop\\Abhishekpandey1909-SwasthaVerse-7acaa7a\\Abhishekpandey1909-SwasthaVerse-7acaa7a\\yoga_pose_neural_network_model.h5"
LABELS = ["downdog", "goddess", "plank", "tree", "warrior2"]
POSE_DISPLAY_NAMES = ["Downward Dog", "Goddess", "Plank", "Tree", "Warrior II"]

try:
    model = load_model(MODEL_PATH)
except Exception as e:
    st.error(f"Failed to load model: {str(e)}")
    model = None

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

# ====================== CORE FUNCTIONS ======================
def extract_landmarks(results):
    if results.pose_landmarks:
        return np.array([[lm.x, lm.y, lm.z, lm.visibility]
                         for lm in results.pose_landmarks.landmark]).flatten()
    return np.zeros(132)

def get_pose_feedback(predicted_pose, target_pose, confidence):
    if confidence < 70:
        return "No pose detected", (255, 0, 0)
    elif predicted_pose != target_pose:
        return f"Adjust to {target_pose}", (255, 165, 0)
    elif confidence < 85:
        return "Good form!", (255, 255, 0)
    else:
        return "Perfect!", (0, 255, 0)

def process_frame(frame, target_pose):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    annotated_image = image.copy()

    if st.session_state.show_hr:
        annotated_image = st.session_state.hr_monitor.process_frame(annotated_image)
        hr = st.session_state.hr_monitor.get_heart_rate()
        cv2.putText(annotated_image, f"Heart Rate: {hr} BPM",
                    (annotated_image.shape[1] - 250, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        st.session_state.current_hr = hr

    if results.pose_landmarks:
        if st.session_state.show_emg:
            annotated_image = draw_muscle_overlay(
                annotated_image,
                results.pose_landmarks.landmark,
                target_pose.lower(),
                alpha=st.session_state.emg_opacity
            )

        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(
                color=(0, 255, 0), thickness=2, circle_radius=2
            ),
            connection_drawing_spec=mp_drawing.DrawingSpec(
                color=(255, 0, 0), thickness=2
            )
        )

        landmarks = extract_landmarks(results)
        if landmarks.sum() != 0 and model:
            landmarks = landmarks.reshape(1, -1)
            predictions = model.predict(landmarks, verbose=0)
            pred_index = np.argmax(predictions)
            predicted_pose = LABELS[pred_index]
            confidence = predictions[0][pred_index] * 100

            feedback, color = get_pose_feedback(predicted_pose, target_pose, confidence)
            biomech_feedback = get_biomechanical_feedback(
                results.pose_landmarks.landmark,
                target_pose.lower()
            )

            y_position = 50
            for text in [
                f"Target: {target_pose}",
                f"Detected: {predicted_pose} ({confidence:.1f}%)",
                feedback
            ]:
                cv2.putText(annotated_image, text, (20, y_position),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                y_position += 40

            y_position += 20
            for correction in biomech_feedback:
                cv2.putText(annotated_image, "• " + correction, (20, y_position),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                y_position += 30

    else:
        cv2.putText(annotated_image, "No person detected", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    return annotated_image

# ====================== STREAMLIT UI ======================
def home_tab():
    st.header("Real-Time Yoga Pose Correction")

    # Pose selection with display names mapped to model labels
    target_display = st.selectbox("Select Pose", POSE_DISPLAY_NAMES)
    target_pose = LABELS[POSE_DISPLAY_NAMES.index(target_display)]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Webcam Session"):
            st.session_state.webcam_active = True
            st.session_state.session_start = datetime.now()
    with col2:
        if st.button("Stop Webcam Session"):
            if st.session_state.webcam_active:
                try:
                    session_end = datetime.now()
                    duration = (session_end - st.session_state.session_start).total_seconds() / 60
                    avg_hr = st.session_state.hr_monitor.get_heart_rate() if st.session_state.show_hr else None

                    st.session_state.session_tracker.add_session(
                        duration=duration,
                        poses=[target_pose],
                        avg_hr=avg_hr
                    )

                    show_feedback_ui(target_pose)

                except Exception as e:
                    st.error(f"Error saving session: {str(e)}")

            st.session_state.webcam_active = False

    if st.session_state.webcam_active:
        cap = cv2.VideoCapture(0)
        frame_placeholder = st.empty()

        try:
            while cap.isOpened() and st.session_state.webcam_active:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to access webcam")
                    break

                processed_frame = process_frame(frame, target_pose)
                frame_placeholder.image(processed_frame, channels="RGB")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

def main():
    st.title("🧘 Swasthaverse - AI Yoga Assistant")
    st.caption("B.Tech Major Project under the guidance of Prof. Shivesh Sharma")

    with st.sidebar:
        selected = option_menu(
            "Main Menu",
            ["Home", "AI Recommendations", "Pose Library", "Yoga Nidra", "Team"],
            icons=["house", "robot", "book", "moon", "people"],
            default_index=0,
            styles={
                "container": {"padding": "5px"},
                "nav-link": {"font-size": "16px"}
            }
        )

        # Progress Tracker Section
        st.divider()
        st.subheader("📈 Progress Tracker")
        tracker = st.session_state.session_tracker
        stats = tracker.get_stats()

        col1, col2 = st.columns(2)
        col1.metric("Total Sessions", stats['total_sessions'])
        col2.metric("Total Duration", f"{stats['total_duration']:.1f} min")

        st.write("**Session History**")
        history_df = tracker.get_history_df()
        if not history_df.empty:
            st.line_chart(history_df.set_index('date')['duration'])
            with st.expander("View All Sessions"):
                st.dataframe(history_df, hide_index=True)
        else:
            st.info("No sessions recorded yet")

        # Feedback History Section
        st.divider()
        st.subheader("📝 Feedback History")
        feedback_df = st.session_state.feedback_system.get_feedback_history(
            st.session_state.user_profile['name']
        )
        if not feedback_df.empty:
            with st.expander("View Feedback History"):
                st.dataframe(feedback_df[['timestamp', 'pose', 'rating', 'comments']],
                             hide_index=True)
        else:
            st.info("No feedback submitted yet")

        # User Profile Section
        st.divider()
        st.subheader("👤 User Profile")
        profile = UserProfile()
        current_profile = profile.load_profile()

        with st.expander("View/Edit Profile"):
            with st.form("profile_form"):
                name = st.text_input("Name", current_profile['name'])
                age = st.number_input("Age", 1, 100, current_profile['age'])
                weight = st.number_input("Weight (kg)", 30, 200, current_profile['weight'])
                height = st.number_input("Height (cm)", 100, 250, current_profile['height'])
                experience = st.selectbox(
                    "Experience Level",
                    ['Beginner', 'Intermediate', 'Advanced'],
                    index=['Beginner', 'Intermediate', 'Advanced'].index(current_profile['experience'])
                )
                goals = st.multiselect(
                    "Primary Goals",
                    ['Flexibility', 'Strength', 'Stress Relief', 'Balance', 'Rehabilitation'],
                    default=current_profile['goals']
                )
                health_notes = st.text_area("Health Notes", current_profile['health_notes'])

                if st.form_submit_button("Save Profile"):
                    profile.update_profile({
                        'name': name,
                        'age': age,
                        'weight': weight,
                        'height': height,
                        'experience': experience,
                        'goals': goals,
                        'health_notes': health_notes
                    })
                    st.success("Profile updated successfully!")

        # Vital Signs Section
        st.divider()
        st.subheader("Vital Signs Monitor")
        st.session_state.show_hr = st.checkbox("Enable Heart Rate Monitoring")

        if st.session_state.show_hr:
            if 'current_hr' in st.session_state:
                hr_history = st.session_state.hr_monitor.hr_history
                current_hr = st.session_state.current_hr

                st.metric(label="Heart Rate",
                          value=f"{current_hr} BPM",
                          delta=None if len(hr_history) < 2 else current_hr - hr_history[-2])

                if len(hr_history) > 1:
                    st.line_chart(hr_history)
            else:
                st.info("Heart rate will appear once webcam starts")

        # Muscle Engagement Section
        st.divider()
        st.subheader("Muscle Engagement")
        st.session_state.show_emg = st.checkbox("Show Muscle Activation")

        if st.session_state.show_emg:
            st.markdown("**Color Code:**")
            st.markdown("- 🔴 Core & Leg Muscles")
            st.markdown("- 🔵 Arm & Shoulder Muscles")
            st.slider("Overlay Opacity", 0.1, 1.0, 0.4, key="emg_opacity")

    if selected == "Home":
        home_tab()
    elif selected == "Pose Library":
        integrate_pose_library()
    elif selected == "Yoga Nidra":
        show_yoga_nidra_interface()
    elif selected == "AI Recommendations":
        st.header("✨ AI-Powered Recommendations")
        user_input = show_recommendation_ui()
        if user_input:
            with st.spinner("Generating personalized recommendations..."):
                recommendations = get_ai_recommendation({
                    **user_input,
                    **st.session_state.user_profile
                })
                st.markdown(recommendations)
                st.divider()
                st.caption("ℹ️ These recommendations are generated by Google Gemini AI")
    elif selected == "Team":
        show_team_page()

if __name__ == "__main__":
    main()