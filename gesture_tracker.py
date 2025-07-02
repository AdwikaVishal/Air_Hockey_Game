import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, max_hands=2, detection_confidence=0.7, smoothing=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=0.7)
        self.smoothing = smoothing
        self.prev_positions = {"Left": None, "Right": None}

    def _lerp(self, old, new):
        if old is None:
            return new
        return (int(old[0] * (1 - self.smoothing) + new[0] * self.smoothing),
                int(old[1] * (1 - self.smoothing) + new[1] * self.smoothing))

    def update(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        h, w, _ = frame.shape

        current_positions = {"Left": None, "Right": None}

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                hand_label = handedness.classification[0].label  # "Left" or "Right"
                pos = (int(wrist.x * w), int(wrist.y * h))
                # Smooth position using linear interpolation
                current_positions[hand_label] = self._lerp(self.prev_positions[hand_label], pos)

        # If hand not detected, keep previous position
        for hand in ["Left", "Right"]:
            if current_positions[hand] is None:
                current_positions[hand] = self.prev_positions[hand]

        self.prev_positions = current_positions.copy()
        return current_positions
