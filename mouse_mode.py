import cv2
import pyautogui
import time

def run_mouse_mode(detector, switcher):
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Reduced resolution for speed
    cap.set(4, 480)

    screen_width, screen_height = pyautogui.size()
    prev_x, prev_y = 0, 0
    smoothening = 3
    prev_index_y = 0
    prev_middle_y = 0
    click_cooldown = 1
    last_click_time = 0
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
            index_x, index_y = lmList[8][1], lmList[8][2]
            middle_x, middle_y = lmList[12][1], lmList[12][2]

            # Always draw tracking line from wrist to index
            cv2.line(frame, lmList[0][1:], (index_x, index_y), (0, 255, 0), 2)

            # Index finger up → cursor movement
            if fingers == [0, 1, 0, 0, 0]:
                screen_x = int(index_x * screen_width / frame.shape[1])
                screen_y = int(index_y * screen_height / frame.shape[0])
                curr_x = prev_x + (screen_x - prev_x) // smoothening
                curr_y = prev_y + (screen_y - prev_y) // smoothening
                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y
                cv2.circle(frame, (index_x, index_y), 10, (0, 255, 0), cv2.FILLED)

            # Left click: middle dips while index still
            if fingers[1] and fingers[2]:
                if time.time() - last_click_time > click_cooldown:
                    if (middle_y - prev_middle_y) > 40 and abs(index_y - prev_index_y) < 15:
                        pyautogui.click()
                        last_click_time = time.time()
                        cv2.putText(frame, "Left Click", (50, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

                    # Right click: index dips while middle still
                    elif (index_y - prev_index_y) > 40 and abs(middle_y - prev_middle_y) < 15:
                        pyautogui.click(button='right')
                        last_click_time = time.time()
                        cv2.putText(frame, "Right Click", (50, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)

            prev_index_y = index_y
            prev_middle_y = middle_y

        # Mode switching
        next_mode = switcher.detectSwitch(frame)
        if next_mode and next_mode != "awaiting_number":
            cap.release()
            cv2.destroyAllWindows()
            return next_mode

        # FPS Display
        cTime = time.time()
        fps = 1 / (cTime - pTime + 1e-5)
        pTime = cTime
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.putText(frame, "Mode: Virtual Mouse", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

        cv2.imshow("Mouse Mode", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return "quit"
