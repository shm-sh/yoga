# offline_library.py
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

POSE_DATA = {
    "Downdog": {
        "image": "poses/downdog.jpg",
        "instructions": "1. Start on hands and knees\n2. Lift hips upward\n3. Straighten legs\n4. Heels toward floor",
        "benefits": "Strengthens arms/legs, Stretches hamstrings"
    },
    "Tree": {
        "image": "poses/tree.jpg",
        "instructions": "1. Stand straight\n2. Place foot on inner thigh\n3. Hands in prayer position",
        "benefits": "Improves balance, Strengthens thighs"
    },
    # Add other poses
}


def generate_pose_pdf():
    filename = "yoga_pose_guide.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        name="Title",
        fontSize=24,
        leading=30,
        alignment=1,
        parent=styles["Heading1"]
    )
    elements.append(Paragraph("YOGGI Offline Pose Library", title_style))
    elements.append(Spacer(1, 0.5 * inch))

    # Add poses
    for pose, data in POSE_DATA.items():
        # Pose Name
        elements.append(Paragraph(pose, styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Image
        if os.path.exists(data["image"]):
            img = Image(data["image"], width=4 * inch, height=3 * inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2 * inch))

        # Instructions
        elements.append(Paragraph("<b>Instructions:</b>", styles["Heading3"]))
        elements.append(Paragraph(data["instructions"], styles["BodyText"]))
        elements.append(Spacer(1, 0.1 * inch))

        # Benefits
        elements.append(Paragraph("<b>Benefits:</b>", styles["Heading3"]))
        elements.append(Paragraph(data["benefits"], styles["BodyText"]))
        elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)
    return filename


def integrate_pose_library():
    st.header("🧘 Yoga Pose Library")

    with st.expander("View Pose Instructions"):
        selected_pose = st.selectbox("Select Pose", list(POSE_DATA.keys()))

        col1, col2 = st.columns([1, 2])
        with col1:
            if os.path.exists(POSE_DATA[selected_pose]["image"]):
                st.image(POSE_DATA[selected_pose]["image"], width=300)
        with col2:
            st.subheader(selected_pose)
            st.markdown("**Instructions:**")
            st.write(POSE_DATA[selected_pose]["instructions"])
            st.markdown("**Benefits:**")
            st.write(POSE_DATA[selected_pose]["benefits"])

    st.divider()
    st.subheader("📥 Download Offline Guide")
    if st.button("Generate PDF Guide"):
        with st.spinner("Creating PDF..."):
            pdf_path = generate_pose_pdf()
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name="yoga_pose_guide.pdf",
                    mime="application/octet-stream"
                )
        os.remove(pdf_path)  # Clean up