import cv2
import numpy as np
import mediapipe as mp

MUSCLE_GROUPS = {
    'core': [23, 24, 11, 12],
    'quadriceps': [23, 25, 27, 24, 26, 28],
    'hamstrings': [25, 27, 26, 28],
    'shoulders': [11, 12, 13, 14],
    'biceps': [13, 15, 14, 16],
    'triceps': [11, 13, 12, 14]
}

POSE_MUSCLES = {
    'downdog': ['shoulders', 'hamstrings', 'triceps'],
    'plank': ['core', 'shoulders', 'quadriceps'],
    'warrior2': ['quadriceps', 'shoulders', 'core'],
    'tree': ['core', 'quadriceps'],
    'goddess': ['quadriceps', 'core', 'shoulders']
}


def draw_muscle_overlay(image, landmarks, pose_name, alpha=0.4):
    """Draw semi-transparent muscle engagement visualization"""
    overlay = image.copy()
    height, width = image.shape[:2]

    if pose_name in POSE_MUSCLES:
        engaged_muscles = POSE_MUSCLES[pose_name]
        for muscle in engaged_muscles:
            points = []
            for idx in MUSCLE_GROUPS[muscle]:
                landmark = landmarks[idx]
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                points.append((x, y))

            if len(points) >= 3:
                color = (0, 0, 255) if muscle in ['shoulders', 'biceps', 'triceps'] else (255, 0, 0)
                cv2.fillPoly(overlay, [np.array(points)], color)

    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)