import math
import mediapipe as mp

# Biomechanical alignment standards for yoga poses
POSE_BIOMECHANICS = {
    "downdog": {
        "angles": {
            "hip": (160, 180),
            "shoulder": (170, 190)
        },
        "feedback": {
            "hip": "Lift hips higher and straighten legs",
            "shoulder": "Press chest towards thighs"
        }
    },
    "warrior2": {
        "angles": {
            "front_knee": (80, 100),
            "back_hip": (160, 180)
        },
        "feedback": {
            "front_knee": "Align front knee over ankle",
            "back_hip": "Rotate back hip forward"
        }
    },
    "tree": {
        "angles": {
            "raised_knee": (160, 180),
            "standing_hip": (170, 190)
        },
        "feedback": {
            "raised_knee": "Bring knee out to the side",
            "standing_hip": "Engage core and square hips"
        }
    },
    "plank": {
        "angles": {
            "shoulder": (170, 190),
            "hip": (170, 190)
        },
        "feedback": {
            "shoulder": "Keep shoulders over wrists",
            "hip": "Maintain straight line from head to heels"
        }
    }
}


def calculate_joint_angle(a, b, c):
    """Calculate the joint angle formed by three landmarks"""
    angle_radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
    angle_degrees = abs(math.degrees(angle_radians))
    return angle_degrees if angle_degrees <= 180 else 360 - angle_degrees


def get_biomechanical_feedback(landmarks, target_pose):
    """Generate posture correction feedback based on joint angles"""
    feedback = []
    target_pose = target_pose.lower()

    if target_pose not in POSE_BIOMECHANICS:
        return feedback

    pose_rules = POSE_BIOMECHANICS[target_pose]
    mp_pose = mp.solutions.pose.PoseLandmark

    try:
        left_shoulder = landmarks[mp_pose.LEFT_SHOULDER]
        left_hip = landmarks[mp_pose.LEFT_HIP]
        left_knee = landmarks[mp_pose.LEFT_KNEE]
        left_ankle = landmarks[mp_pose.LEFT_ANKLE]

        if target_pose == "downdog":
            hip_angle = calculate_joint_angle(left_shoulder, left_hip, left_knee)
            if not pose_rules["angles"]["hip"][0] <= hip_angle <= pose_rules["angles"]["hip"][1]:
                feedback.append(pose_rules["feedback"]["hip"])

        elif target_pose == "warrior2":
            front_knee_angle = calculate_joint_angle(left_hip, left_knee, left_ankle)
            if not pose_rules["angles"]["front_knee"][0] <= front_knee_angle <= pose_rules["angles"]["front_knee"][1]:
                feedback.append(pose_rules["feedback"]["front_knee"])

        elif target_pose == "tree":
            raised_knee_angle = calculate_joint_angle(left_hip, left_knee, left_ankle)
            if not pose_rules["angles"]["raised_knee"][0] <= raised_knee_angle <= pose_rules["angles"]["raised_knee"][
                1]:
                feedback.append(pose_rules["feedback"]["raised_knee"])

        elif target_pose == "plank":
            shoulder_angle = calculate_joint_angle(left_hip, left_shoulder,
                                                   landmarks[mp_pose.LEFT_WRIST])
            if not pose_rules["angles"]["shoulder"][0] <= shoulder_angle <= pose_rules["angles"]["shoulder"][1]:
                feedback.append(pose_rules["feedback"]["shoulder"])

    except Exception as e:
        print(f"Error in biomechanical analysis: {str(e)}")

    return feedback[:2]