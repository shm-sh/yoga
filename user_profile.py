# user_profile.py
import streamlit as st


class UserProfile:
    def __init__(self):
        self.profile = {
            'name': 'New User',
            'age': 25,
            'weight': 65,
            'height': 170,
            'goals': ['Flexibility'],
            'experience': 'Beginner',
            'health_notes': ''
        }

    def save_profile(self):
        st.session_state.user_profile = self.profile

    def load_profile(self):
        if 'user_profile' in st.session_state:
            self.profile = st.session_state.user_profile
        return self.profile

    def update_profile(self, updates):
        self.profile.update(updates)
        self.save_profile()