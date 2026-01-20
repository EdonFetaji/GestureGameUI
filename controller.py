from pynput.keyboard import Key, Controller as KeyController
import time


class GameController:
    def __init__(self):
        print("Initializing GameController...")
        self.keyboard = KeyController()
        self.last_key = None
        self.cooldown = 0.1  # seconds between key presses
        self.last_press_time = 0
        print("✓ Keyboard controller ready")

    def execute_gesture(self, gesture, profile):
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_press_time < self.cooldown:
            print(f"    ⏸ Cooldown active (waiting {self.cooldown - (current_time - self.last_press_time):.3f}s)")
            return

        # Get key mapping
        key_map = self._get_profile_keymap(profile)
        print(f"    Profile keymap: {key_map}")

        if gesture not in key_map:
            print(f"    ✗ ERROR: Gesture '{gesture}' not found in keymap!")
            return

        key = key_map[gesture]
        print(f"    Mapped gesture '{gesture}' to key: {key}")

        try:
            print(f"    Pressing key: {key}")
            self.keyboard.press(key)
            time.sleep(0.05)
            self.keyboard.release(key)
            print(f"    ✓ Key released successfully")
            self.last_press_time = current_time
        except Exception as e:
            print(f"    ✗ ERROR pressing key: {e}")

    def _get_profile_keymap(self, profile):
        if profile == "Subway Surfers":
            return {"LEFT": Key.left, "RIGHT": Key.right,
                    "JUMP": Key.up, "DUCK": Key.down}
        elif profile == "Temple Run":
            return {"LEFT": 'a', "RIGHT": 'd',
                    "JUMP": 'w', "DUCK": 's'}
        else:
            print(f"    ✗ WARNING: Unknown profile '{profile}'")
            return {}