import cv2
import numpy as np
import heartpy as hp
from collections import deque
from cvzone.FaceDetectionModule import FaceDetector


class HeartRateMonitor:
    def __init__(self):
        self.detector = FaceDetector()
        self.buffer_size = 300  # Increased buffer for better accuracy
        self.ppg_signal = deque(maxlen=self.buffer_size)
        self.sample_rate = 30
        self.roi = (100, 100, 200, 200)  # Forehead region
        self.last_hr = 72  # Default resting HR
        self.hr_history = []

    def process_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame, bboxs = self.detector.findFaces(frame, draw=False)

        if bboxs:
            x, y, w, h = self.roi
            forehead = frame[y:y + h, x:x + w]
            if forehead.size > 0:
                # Use green channel for better PPG signal
                avg_pixel = np.mean(forehead[:, :, 1])
                self.ppg_signal.append(avg_pixel)

                # Draw forehead ROI for visualization
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "HR Measurement Zone", (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        return frame

    def get_heart_rate(self):
        if len(self.ppg_signal) == self.buffer_size:
            try:
                # Process PPG signal
                filtered = hp.filter_signal(list(self.ppg_signal),
                                            cutoff=[0.7, 2.5],
                                            sample_rate=self.sample_rate,
                                            filtertype='bandpass')

                # Analyze heart rate
                wd, m = hp.process(filtered, self.sample_rate)
                if m['bpm'] > 40 and m['bpm'] < 180:  # Valid HR range
                    self.last_hr = int(m['bpm'])
                    self.hr_history.append(self.last_hr)

                    # Keep only last 10 readings
                    if len(self.hr_history) > 10:
                        self.hr_history.pop(0)
            except:
                pass

        return self.last_hr