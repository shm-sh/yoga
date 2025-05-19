# team.py

import streamlit as st


def show_team_page():
    st.header("🧘♂️ Meet Our Team")

    st.markdown("""
    ### Our Vision
    *"Empowering holistic wellness through AI-driven yoga guidance - making personalized practice accessible to everyone."*
    """)

    # Supervisor Section
    st.divider()
    st.subheader("🎓 Project Supervisor")

    sup_col1, sup_col2 = st.columns([1, 3])
    with sup_col1:
        st.image("assets/team_photos/shivesh_sharma.jpg", width=200)

    with sup_col2:
        st.markdown("""
        **Prof. Shivesh Sharma**  
        *Dean, Research & Consultancy, MNNIT Allahabad*
        **Research Areas:**  
        - Plant Microbial Biology  
        - Environmental Biotechnology 
        - Plant Stress Physiology 

        **Guidance Focus:**  
        ▸ Ethical AI implementation  
        ▸ Real-world system deployment
        """)

    # Core Team Section
    st.subheader("🌟 Core Team")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("assets/team_photos/shaurya.jpg", width=150)
        st.markdown("""
        **Shaurya Modi**  
        *Coding*  
        B.Tech Biotechnology, VIII Semester  
        Expertise: MediaPipe, TensorFlow, Real-time Systems
        """)

    with col2:
        st.image("assets/team_photos/aditya.jpg", width=150)
        st.markdown("""
        **Aditya Narayan**  
        *Ideation*  
        B.Tech Biotechnology, VIII Semester  
        Expertise: S
        """)

    with col3:
        st.image("assets/team_photos/ashish.jpg", width=150)
        st.markdown("""
        **Ashish Kumar**  
        *Documentation and Presentation*  
        B.Tech Biotechnology, VIII Semester  
        Expertise: S
        """)


    st.divider()
    st.markdown("""
    **Academic Affiliation**  
    *Department of Biotechnology*  
    *Motilal Nehri National Institute of Technology Allahabad, Prayagraj*  
    """)