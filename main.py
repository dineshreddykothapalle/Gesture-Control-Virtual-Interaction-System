# main.py

from handtracking import HandDetector
from mode_switcher import ModeSwitcher
from mouse_mode import run_mouse_mode
from painter_mode import run_painter_mode
from volume_mode import run_volume_mode


def main():
    detector = HandDetector(maxHands=1, detectionCon=0.7)
    switcher = ModeSwitcher(detector)
    mode = "mouse"  # Starting mode

    while True:
        if mode == "mouse":
            mode = run_mouse_mode(detector, switcher)
        elif mode == "volume":
            mode = run_volume_mode(detector, switcher)
        elif mode == "painter":
            mode = run_painter_mode(detector, switcher)
        elif mode == "quit":
            break
        else:
            print(f"[ERROR] Unknown mode: {mode}")
            break


if __name__ == "__main__":
    main()
