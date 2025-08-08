import cv2
import time
import pyttsx3


class ModeSwitcher:
    def __init__(self, detector):
        self.detector = detector
        self.switch_mode = None
        self.voice = pyttsx3.init()
        self.voice.setProperty('rate', 150)
        self.voice.setProperty('volume', 1.0)
        self.start_time = None
        self.awaiting_number = False
        self.mode_map = {
            1: "mouse",
            2: "volume",
            3: "painter"
        }

    def speak(self, text):
        self.voice.say(text)
        self.voice.runAndWait()

    def detectSwitch(self, frame):
        frame = self.detector.findHands(frame)
        lmList = self.detector.findPosition(frame, draw=True)
        if not lmList:
            self.start_time = None
            return None

        fingers = self.detector.fingersUp()
        cv2.putText(frame, f"Fingers: {sum(fingers)}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Step 1: Fist gesture (all fingers down)
        if fingers == [0, 0, 0, 0, 0] and not self.awaiting_number:
            if self.start_time is None:
                self.start_time = time.time()
            elif time.time() - self.start_time > 3:  # Hold fist for 5s
                self.awaiting_number = True
                self.speak(
                    "Mode switch activated. Show 1 for Mouse, 2 for Volume, 3 for Painter.")
                cv2.putText(frame, "Show number to switch mode", (400, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                return "awaiting_number"
        else:
            self.start_time = None

        # Step 2: Show number gesture after fist
        if self.awaiting_number:
            num_fingers = sum(fingers)
            if num_fingers in self.mode_map:
                new_mode = self.mode_map[num_fingers]
                self.speak(f"Switching to {new_mode} mode.")
                self.awaiting_number = False
                time.sleep(1)  # slight pause to prevent double detection
                return new_mode

        return None
