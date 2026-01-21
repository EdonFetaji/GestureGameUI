from pynput.keyboard import Key, Controller as KeyController
import time


class GameController:
    def __init__(self):
        self.keyboard = KeyController()
        self.cooldown = 0.12
        self.last_press_time = 0.0

    def execute_action(self, action, profile):
        keymap = self._get_profile_keymap(profile)
        if action not in keymap:
            return

        now = time.time()
        if now - self.last_press_time < self.cooldown:
            return

        key = keymap[action]
        try:
            self.keyboard.press(key)
            time.sleep(0.05)
            self.keyboard.release(key)
            self.last_press_time = now
        except Exception as e:
            print(f"[Controller] Error pressing key: {e}")

    def _get_profile_keymap(self, profile):
        if profile == "Subway Surfers":
            return {
                "LEFT": Key.left,
                "RIGHT": Key.right,
                "JUMP": Key.up,
                "DUCK": Key.down,
                "SPACE": Key.space,   # ✅ NEW
            }
        elif profile == "Temple Run":
            return {
                "LEFT": "a",
                "RIGHT": "d",
                "JUMP": "w",
                "DUCK": "s",
                "SPACE": Key.space,   # ✅ NEW
            }
        else:
            return {}
