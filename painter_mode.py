import cv2
import numpy as np
import time

def run_painter_mode(detector, switcher):
    brush_thickness = 10
    eraser_thickness = 50
    draw_color = (0, 0, 255)

    canvas = np.zeros((720, 1280, 3), np.uint8)
    xp, yp = 0, 0

    color_map = {
        (50, 50): ((0, 0, 255), "RED"),
        (150, 50): ((0, 255, 0), "GREEN"),
        (250, 50): ((255, 0, 0), "BLUE"),
        (350, 50): ((255, 255, 255), "ERASER")
    }

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame, draw=True)

        if lmList:
            fingers = detector.fingersUp()
            x1, y1 = lmList[8][1], lmList[8][2]
            x2, y2 = lmList[12][1], lmList[12][2]

            if sum(fingers) == 1:
                brush_thickness = 5
            elif sum(fingers) == 2:
                brush_thickness = 15
            elif sum(fingers) == 3:
                brush_thickness = 30

            # Color selection
            if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
                xp, yp = 0, 0
                if y1 < 100:
                    for (bx, by), (color, label) in color_map.items():
                        if bx - 40 < x1 < bx + 40:
                            draw_color = color
                            cv2.putText(frame, f"Selected {label}", (800, 60),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
                cv2.rectangle(frame, (x1, y1 - 25), (x2, y2 + 25), draw_color, cv2.FILLED)

            # Drawing mode: only index up
            elif fingers[1] and not any(fingers[2:]):
                cv2.circle(frame, (x1, y1), 10, draw_color, cv2.FILLED)
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                if draw_color == (255, 255, 255):
                    cv2.line(frame, (xp, yp), (x1, y1), draw_color, eraser_thickness)
                    cv2.line(canvas, (xp, yp), (x1, y1), (0, 0, 0), eraser_thickness)
                else:
                    cv2.line(frame, (xp, yp), (x1, y1), draw_color, brush_thickness)
                    cv2.line(canvas, (xp, yp), (x1, y1), draw_color, brush_thickness)
                xp, yp = x1, y1
            else:
                xp, yp = 0, 0

            # Clear canvas gesture
            if fingers == [0, 1, 1, 1, 1]:
                canvas = np.zeros((720, 1280, 3), np.uint8)
                cv2.putText(frame, "Canvas Cleared", (500, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # Mode switch
        next_mode = switcher.detectSwitch(frame)
        if next_mode and next_mode != "awaiting_number":
            cap.release()
            cv2.destroyAllWindows()
            return next_mode

        # Blending
        img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(frame, img_inv)
        frame = cv2.bitwise_or(frame, canvas)

        # UI buttons
        for (x, y), (color, label) in color_map.items():
            cv2.rectangle(frame, (x - 40, y - 40), (x + 40, y + 40), color, cv2.FILLED)
            cv2.putText(frame, label, (x - 30, y + 60),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 0), 2)

        cv2.putText(frame, "Mode: Painter", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

        cv2.imshow("Painter Mode", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            timestamp = int(time.time())
            cv2.imwrite(f"drawing_{timestamp}.png", canvas)
            print(f"[INFO] Drawing saved as drawing_{timestamp}.png")

        if key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return "quit"
