# feedback_system.py
import streamlit as st
import pandas as pd
from urllib.parse import quote
import os
from datetime import datetime


class FeedbackSystem:
    def __init__(self):
        self.feedback_file = "feedback_history.csv"
        self._initialize_storage()

    def _initialize_storage(self):
        if not os.path.exists(self.feedback_file):
            pd.DataFrame(columns=[
                'timestamp', 'user', 'pose', 'rating', 'comments', 'email_initiated'
            ]).to_csv(self.feedback_file, index=False)

    def save_feedback(self, user_name, pose, rating, comments):
        new_entry = pd.DataFrame([{
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': user_name,
            'pose': pose,
            'rating': rating,
            'comments': comments,
            'email_initiated': False
        }])

        new_entry.to_csv(self.feedback_file, mode='a', header=False, index=False)
        return new_entry

    def get_feedback_history(self, user_name):
        try:
            df = pd.read_csv(self.feedback_file)
            return df[df['user'] == user_name]
        except:
            return pd.DataFrame()


def show_feedback_ui(target_pose):
    with st.form("feedback_form"):
        st.subheader("Session Feedback")
        rating = st.slider("Rate your session (1-5)", 1, 5, 4)
        comments = st.text_area("Additional comments")

        if st.form_submit_button("Send Feedback"):
            user_profile = st.session_state.user_profile
            feedback_system = st.session_state.feedback_system

            # Save feedback locally
            new_feedback = feedback_system.save_feedback(
                user_name=user_profile['name'],
                pose=target_pose,
                rating=rating,
                comments=comments
            )

            # Create mailto link
            subject = f"YOGGI Feedback - {target_pose} ({rating}⭐)"
            body = f"""User: {user_profile['name']}
Pose: {target_pose}
Rating: {rating}/5
Comments: {comments}

Sent via YOGGI App"""

            mailto_link = f"mailto:fgj9074@gmail.com?subject={quote(subject)}&body={quote(body)}"

            st.markdown(f"""
            **Click below to send feedback email:**
            <a href="{mailto_link}" target="_blank" style="
                display: inline-block;
                padding: 0.5rem 1rem;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 1rem;">
                📧 Send Email Now
            </a>
            """, unsafe_allow_html=True)

            st.session_state.feedback_system = feedback_system
            st.success("Feedback saved! Please send the email using the button above.")