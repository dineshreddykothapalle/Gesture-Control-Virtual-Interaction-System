import cv2
import numpy as np
import math
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def run_volume_mode(detector, switcher):
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    # Audio setup
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    vol_min, vol_max = volume.GetVolumeRange()[:2]

    pTime = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame, draw=True)

        if lmList:
            fingers = detector.fingersUp()
            x1, y1 = lmList[4][1], lmList[4][2]   # Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2]   # Index tip
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            # Visual markers
            cv2.circle(frame, (x1, y1), 12, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 12, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

            # Volume control
            length = math.hypot(x2 - x1, y2 - y1)

            # Apply 70% sensitivity: cap volume at 70%
            max_vol_level = vol_max * 0.7
            vol = np.interp(length, [50, 180], [vol_min, max_vol_level])
            volume.SetMasterVolumeLevel(vol, None)

            # Calculate percent from actual volume level
            current_level = volume.GetMasterVolumeLevel()
            vol_percent = int(np.interp(current_level, [vol_min, max_vol_level], [0, 100]))
            vol_bar = np.interp(current_level, [vol_min, max_vol_level], [400, 150])

            # Visual bar and label
            cv2.rectangle(frame, (50, 150), (85, 400), (0, 0, 0), 2)
            cv2.rectangle(frame, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, f'{vol_percent} %', (40, 430),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Mode switching
        next_mode = switcher.detectSwitch(frame)
        if next_mode and next_mode != "awaiting_number":
            cap.release()
            cv2.destroyAllWindows()
            return next_mode

        # FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime + 1e-5)
        pTime = cTime
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Mode label
        cv2.putText(frame, "Mode: Volume Control", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

        cv2.imshow("Volume Mode", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return "quit"