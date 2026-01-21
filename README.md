# 🎮 Gesture Game Controller UI

A cross-platform **desktop application** that lets users control browser games  
(**Subway Surfers** / **Temple Run 2**) using **hand gestures** detected from a webcam.

The project uses:
- 🧠 **MediaPipe Gesture Recognizer (Tasks API)** for accurate gesture detection
- 🖥 **PySide6 (Qt)** for a modern desktop launcher UI
- 🎮 **pynput** to send keyboard input to games
- 📦 **PyInstaller** to package the app for **macOS** and **Windows**

---

## ✨ Features

### 🧭 Gesture-controlled launcher
You can navigate the launcher **without mouse or keyboard**:
- 👊 **Closed_Fist** → Move/hover through buttons
- 👍 **Thumb_Up** → Select / Click the hovered button

### 🎮 Game control (background)
When a game is selected:
1. The game opens in your browser
2. Gesture recognition runs **in the background**
3. Gestures are translated into keyboard inputs for the game

### 🧪 Test mode
A camera window for testing:
- live gesture name + confidence
- FPS and latency
- hand skeleton visualization

---

## 🧠 Gesture mappings

### 🎮 Game gestures → actions

| Gesture (MediaPipe label) | Action | Meaning |
|---------------------------|--------|--------|
| ✌️ Victory                | LEFT   | Move left |
| 🤟 ILoveYou               | RIGHT  | Move right |
| ☝️ Pointing_Up            | JUMP   | Jump |
| ✊ Closed_Fist             | DUCK   | Duck / Roll |
| 👍 Thumb_Up               | SPACE  | Space key |

### 🧭 Launcher gestures → UI navigation

| Gesture | Action |
|-------|--------|
| 👊 Closed_Fist | Move selection |
| 👍 Thumb_Up | Select / Click |

---

## 🗂 Project structure

```
GestureControlGameUI/
├─ app/
│  ├─ __init__.py
│  ├─ gesture_test.py          # Test mode with live camera preview
│  ├─ run_launcher.py          # Main entry point
│  ├─ assets/
│  │  └─ gesture_recognizer.task   # Pre-trained MediaPipe model
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ background_runner.py      # Runs gesture recognition in background
│  │  ├─ controller.py             # Keyboard input via pynput
│  │  ├─ gesture_interface.py      # Abstract interface for recognizers
│  │  ├─ paths.py                  # Asset path resolution (dev/packaged)
│  │  ├─ performance.py            # FPS & latency tracking
│  │  ├─ recognizer.py             # Legacy recognizer (compatibility)
│  │  ├─ recognizer_factory.py     # Factory + singleton for recognizers
│  │  ├─ recognizer_hybrid.py      # Hybrid: MediaPipe Hands + custom poses
│  │  ├─ recognizer_mediapipe.py   # MediaPipe Tasks API recognizer
│  │  └─ ui_gesture_worker.py      # QThread worker for UI gestures
│  └─ ui/
│     ├─ __init__.py
│     ├─ qt_launcher.py            # PySide6 launcher window
│     └─ ui_draw.py                # Overlay drawing utilities
├─ hooks/
│  └─ hook-mediapipe.py            # PyInstaller hook for MediaPipe
├─ requirements.txt
└─ README.md
```

---

## 🔩 How the system works

### Architecture overview
```
gesture_interface.py (Abstract base class)
        ↑
        ├── recognizer_mediapipe.py (MediaPipe Tasks API)
        └── recognizer_hybrid.py (MediaPipe Hands + custom poses)
                ↑
        recognizer_factory.py (Factory + Singleton manager)
```

### Launcher flow
```
run_launcher.py
  ↓
qt_launcher.py (MainWindow)
  ↓
ui_gesture_worker.py (camera + UI gestures in QThread)
  ↓
recognizer_factory.py → creates recognizer instance
  ↓
Closed_Fist → move hover
Thumb_Up → click button
```

### Game flow
```
User selects a game
  ↓
Browser opens game URL
  ↓
background_runner.py starts
  ↓
recognizer_factory.py → MEDIAPIPE_TASKS or HYBRID_POSE
  ↓
controller.py presses keys via pynput
```

### Test mode
```
gesture_test.py
  ↓
recognizer_factory.py
  ↓
ui_draw.py overlays + skeleton
```

### Recognizer types
| Type | Description |
|------|-------------|
| `MEDIAPIPE_TASKS` | Uses pre-trained `gesture_recognizer.task` model. Best for static poses (Victory, ILoveYou, etc.) |
| `HYBRID_POSE` | Uses MediaPipe Hands with custom pose classification. Better for motion-based gestures (swipes) |

---

## 🎮 Supported games

- 🚇 **Subway Surfers (Poki)**  
  https://poki.com/en/g/subway-surfers

- 🏃 **Temple Run 2 (Poki)**  
  https://poki.com/en/g/temple-run-2

⚠️ **Important:** Keep the browser tab focused so key presses go to the game.

---

## ⚙️ Installation & running (development)

### 1️⃣ Create virtual environment

**macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the launcher
```bash
python -m app.run_launcher
```

### 4️⃣ Run test mode
```bash
python -m app.gesture_test
```

---

## 📦 Packaging the app (PyInstaller)

### ⚠️ Why a custom hook is required
MediaPipe Tasks uses compiled native libraries  
(`mediapipe.tasks.c`). PyInstaller does **not** bundle these automatically.

This project includes:
```
hooks/hook-mediapipe.py
```
to ensure all MediaPipe native binaries are included.

---

### 🍎 Build on macOS (.app)

```bash
pyinstaller --noconfirm --clean --windowed \
  --name "GestureGameController" \
  --additional-hooks-dir hooks \
  --add-data "app/assets/gesture_recognizer.task:app/assets" \
  app/run_launcher.py
```

Output:
```
dist/GestureGameController.app
```

If macOS blocks the app:
```bash
xattr -dr com.apple.quarantine dist/GestureGameController.app
```

---

### 🪟 Build on Windows (.exe)

```powershell
pyinstaller --noconfirm --clean --windowed `
  --name "GestureGameController" `
  --additional-hooks-dir hooks `
  --add-data "app\assets\gesture_recognizer.task;app\assets" `
  app\run_launcher.py
```

Output:
```
dist\GestureGameController\GestureGameController.exe
```

---

## 🧯 Troubleshooting

### ❌ Game doesn’t respond
- Browser tab not focused
- Camera permission not granted
- Poor lighting
- Hand too far from camera

### ❌ Gestures trigger multiple times
- Use edge-trigger logic (`IDLE → ACTION`)
- Cooldown is already implemented in workers

### ❌ Packaging error:
`No module named mediapipe.tasks.c`
- Make sure you build with:
  ```
  --additional-hooks-dir hooks
  ```

---

## 📌 Notes
This project covers the following features:
- MediaPipe Tasks API usage
- Gesture-driven UI navigation
- Background processing with Qt threads
- Cross-platform desktop packaging

