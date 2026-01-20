A computer vision-based game controller that lets you play games using hand gestures. Control games like Subway Surfers and Temple Run without touching your keyboard.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.13-orange.svg)

> **⚠️ IMPORTANT - Branch Information**  
> This project has two branches with different gesture systems:
> - **`main` branch**: Uses motion-based swiping gestures for LEFT/RIGHT
> - **`test` branch**: Uses static hand poses (Victory ✌️ and I Love You 🤟) for LEFT/RIGHT
> 
> Choose the branch that best fits your needs. Most users find the `test` branch more stable.

>Example Games you can play: 
> 
> https://poki.com/en/g/subway-surfers
> 
> https://chromedino.com/
> 
> https://poki.com/en/g/temple-run-2
## Table of Contents

- [Branch Differences](#branch-differences)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Gesture Reference](#gesture-reference)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)
- [Performance Tips](#performance-tips)
- [Contributing](#contributing)
- [License](#license)

## Branch Differences

This project has **two branches** with different gesture control systems:

### 🌿 `main` Branch - Motion-Based Control

**LEFT/RIGHT Gestures:** Swiping hand movements

| Gesture | Action |
|---------|--------|
| Swipe LEFT (←) | LEFT |
| Swipe RIGHT (→) | RIGHT |
| Swipe UP (↑) | JUMP |
| Swipe DOWN (↓) | DUCK |

**Pros:**
- Natural swiping motion
- Feels like physically pushing left/right
- Four directional movements all use same technique

**Cons:**
- Requires precise hand movement
- Can trigger accidentally from shaky hands
- Harder to keep hand steady

### 🧪 `test` Branch - Static Pose Control

**LEFT/RIGHT Gestures:** Static hand poses (Victory & I Love You signs)

| Gesture | Action |
|---------|--------|
| Victory ✌️ (Index + Middle) | LEFT |
| I Love You 🤟 (Thumb + Index + Pinky) | RIGHT |
| Fist 👊 | DUCK |
| Index Up ☝️ | JUMP |

**Pros:**
- ✅ More stable - no movement needed
- ✅ Less false positives
- ✅ Easier to control
- ✅ Better for beginners

**Cons:**
- Need to learn specific hand shapes
- May be less intuitive initially

### Which Branch Should You Use?

**Choose `main` if:**
- You prefer natural swiping motions
- You have steady hands
- You want all four directions to feel consistent

**Choose `test` if:**
- You want maximum stability
- You have shaky hands or camera vibration
- You're getting too many false triggers
- You prefer static poses over motion

**To switch branches:**
```bash
# Switch to main branch (swiping gestures)
git checkout main

# Switch to test branch (static poses)
git checkout test
```

## Features

### Control Systems by Branch

**📌 Main Branch - Motion-Based Control**
- Swipe gestures (up, down, left, right)
- Movement trajectory analysis
- High-speed gesture detection
- All four directions use swiping motion

**📌 Test Branch - Pose-Based Control** ⭐ **RECOMMENDED FOR STABILITY**
- Static hand poses (no movement needed)
- Victory sign (✌️) for LEFT
- I Love You sign (🤟) for RIGHT
- Fist and pointing gestures
- More stable and reliable

### Core Features (Both Branches)

✓ Real-time hand tracking using MediaPipe  
✓ Multiple game profiles (Subway Surfers, Temple Run)  
✓ Customizable key mappings  
✓ Visual feedback with hand skeleton overlay  
✓ Performance monitoring (FPS, latency)  
✓ Cooldown system to prevent multiple triggers  
✓ Mirror view for natural control  
✓ Testing tools for calibration  

## How It Works

The system uses Google's MediaPipe Hands to detect and track your hand in real-time through your webcam. It analyzes hand landmarks to recognize specific gestures, then translates them into keyboard commands for game control.

```
Camera Feed → MediaPipe Hand Detection → Gesture Recognition → Keyboard Commands → Game
```

**The gesture recognition method differs by branch:**
- **`main` branch**: Tracks hand movement over time to detect swipe directions
- **`test` branch**: Analyzes finger positions to identify static hand poses

### Gesture Recognition Pipeline

1. **Capture**: Webcam captures video frames at 30+ FPS
2. **Detection**: MediaPipe identifies 21 hand landmarks
3. **Analysis**: 
   - `main` branch: Tracks wrist position across frames to detect movement
   - `test` branch: Counts extended fingers and identifies specific combinations
4. **Classification**: Gestures are classified based on movement or pose
5. **Execution**: Corresponding keyboard keys are pressed
6. **Cooldown**: Brief delay prevents accidental multiple triggers

## Installation

### Prerequisites

- Python 3.8 or higher
- Webcam
- Windows/Linux/MacOS

### Step 1: Clone or Download

```bash
git clone https://github.com/edonfetaji/GestureGameUI
cd GestureGameUI
```

**Choose your branch:**
```bash
# For static pose gestures (Victory, I Love You) - Recommended for stability
git checkout test

# OR for swiping motion gestures - More natural feel
git checkout main
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt includes:**
- opencv-python==4.8.1.78
- mediapipe==0.10.13
- numpy==1.26.4
- pynput==1.7.6

### Step 3: Verify Installation

**Test Branch:**
```bash
python pose_test.py
```

**Main Branch:**
```bash
python pose_test.py
```

If you see the camera feed and gesture detection, you're ready to go!

## Quick Start

### Step 0: Choose Your Branch

**First, decide which control system you want:**

```bash
# For static pose gestures (Victory, I Love You signs) - MORE STABLE
git checkout test

# For swiping motion gestures - MORE NATURAL
git checkout main
```

### Testing Gestures (Recommended First Step)

**Test Branch (Pose-Based):**
```bash
python pose_test.py
```

**Main Branch (Motion-Based):**
```bash
python pose_test.py
```

This will guide you through testing each gesture one by one:

**Test Branch:**
1. FIST → DUCK
2. INDEX UP → JUMP
3. VICTORY → LEFT
4. I LOVE YOU → RIGHT

**Main Branch:**
1. Swipe UP → JUMP
2. Swipe RIGHT → RIGHT
3. Swipe LEFT → LEFT
4. Swipe DOWN → DUCK

### Running the Controller

**Both branches use the same main program:**
```bash
python pose_main.py
```

**Controls:**
- `SPACE` - Toggle control ON/OFF (start disabled for safety)
- `P` - Switch game profile
- `Q` - Quit

### Using with Games

1. Start your game (Subway Surfers, Temple Run, etc.)
2. Run `python pose_main.py`
3. Position the camera window so you can see both game and your hand
4. Press `SPACE` to enable control
5. Make gestures to play:
   - **Test branch**: Hold static hand poses
   - **Main branch**: Make quick swiping motions

## Gesture Reference

### 🧪 Test Branch - Pose-Based Gestures (RECOMMENDED)

**Static hand poses - no movement required**

| Gesture | Visual | Fingers Extended | Action |
|---------|--------|------------------|--------|
| **FIST** | 👊 | None | DUCK |
| **INDEX UP** | ☝️ | Index only | JUMP |
| **VICTORY** | ✌️ | Index + Middle | LEFT |
| **I LOVE YOU** | 🤟 | Thumb + Index + Pinky | RIGHT |
| **OPEN PALM** | ✋ | All | IDLE |

**To use test branch:**
```bash
git checkout test
python pose_test.py  # Test gestures
python pose_main.py  # Run controller
```

---

### 🌿 Main Branch - Motion-Based Gestures

**Quick swiping movements**

| Gesture | Direction | Visual | Action |
|---------|-----------|--------|--------|
| **Swipe Up** | ↑ | Quick upward hand motion | JUMP |
| **Swipe Down** | ↓ | Quick downward hand motion | DUCK |
| **Swipe Left** | ← | Quick left hand motion | LEFT |
| **Swipe Right** | → | Quick right hand motion | RIGHT |

**Requirements for swipes:**
- Move hand quickly (not slow drift)
- Clear directional movement
- Minimum distance threshold
- Return to neutral position between gestures

**To use main branch:**
```bash
git checkout main
python pose_test.py  # Test gestures
python pose_main.py  # Run controller  # Run controller (works with both systems)
```

---

### Comparison

| Aspect | Main Branch (Swipes) | Test Branch (Poses) |
|--------|---------------------|---------------------|
| **Stability** | Moderate | High |
| **Learning Curve** | Easy | Medium |
| **False Positives** | More likely | Less likely |
| **Hand Steadiness** | Must be steady | Can be shaky |
| **Natural Feel** | Very natural | Less intuitive |
| **Best For** | Smooth control | Reliable control |

## Usage Guide

### Basic Workflow

1. **Choose your branch**
   - Run `git checkout test` for pose-based gestures
   - Run `git checkout main` for motion-based gestures

2. **Position yourself**
   - Sit 2-3 feet from camera
   - Ensure good lighting
   - Center your hand in frame

3. **Test gestures first**
   - **Test branch**: Run `pose_test.py` to verify all gestures work
   - **Main branch**: Run `gesture_test.py` to verify all gestures work
   - Practice each gesture until confident

4. **Start your game**
   - Launch Subway Surfers, Temple Run, or similar game
   - Position game window appropriately

5. **Run controller**
   - Execute `python pose_main.py` (works for both branches)
   - Control starts DISABLED for safety

6. **Enable and play**
   - Press `SPACE` to enable
   - **Test branch**: Hold static hand poses
   - **Main branch**: Make quick swiping motions
   - Press `SPACE` again to pause control

### Game Profiles

The system includes pre-configured profiles:

**Subway Surfers** (Arrow Keys)
- LEFT → Left Arrow
- RIGHT → Right Arrow
- JUMP → Up Arrow
- DUCK → Down Arrow

**Temple Run** (WASD Keys)
- LEFT → A
- RIGHT → D
- JUMP → W
- DUCK → S

Switch profiles with the `P` key while running.

### Custom Game Configuration

Edit `controller.py` to add your own game:

```python
def _get_profile_keymap(self, profile):
    if profile == "Your Game":
        return {
            "LEFT": 'your_left_key',
            "RIGHT": 'your_right_key',
            "JUMP": 'your_jump_key',
            "DUCK": 'your_duck_key'
        }
```

## Project Structure

```
gesture-game-controller/
│
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
│
├── pose_gesture_controller.py         # Main gesture recognition engine
│                                      # (Test: pose-based / Main: motion-based)
├── gesture_recognizer.py              # Legacy motion-based recognition (Main branch)
│
├── pose_main.py                       # Main program (works on both branches)
├── pose_test.py                       # Gesture testing (Test branch - static poses)
├── gesture_test.py                    # Gesture testing (Main branch - swipes)
│
├── controller.py                      # Keyboard control and game profiles
├── ui_controller.py                   # UI rendering and overlays
├── ui_overlay.py                      # Legacy UI components
├── performance_tracker.py             # FPS and latency tracking
│
└── REFACTORING_README.md              # Details on test branch refactoring
```

### Branch-Specific Files

**Test Branch (`test`):**
- `pose_gesture_controller.py` - Uses static pose detection (Victory, I Love You)
- `pose_test.py` - Tests FIST, INDEX UP, VICTORY, I LOVE YOU gestures
- `ui_controller.py` - Shows "Victory sign = LEFT" guide

**Main Branch (`main`):**
- `pose_gesture_controller.py` - Uses movement detection (swipes)
- `gesture_test.py` - Tests UP, DOWN, LEFT, RIGHT swipe gestures  
- `gesture_recognizer.py` - Original motion-based algorithm
- `ui_controller.py` - Shows "Swipe left = LEFT" guide

**Both Branches:**
- `pose_main.py` - Main controller program
- `controller.py` - Game profile key mappings
- `performance_tracker.py` - Performance monitoring

## Technical Details

### Hand Tracking

Uses **MediaPipe Hands** to detect 21 landmarks per hand:

```
Landmark IDs:
0  - Wrist
4  - Thumb tip
8  - Index tip
12 - Middle tip
16 - Ring tip
20 - Pinky tip
```

### Gesture Detection Algorithms

The two branches use different detection approaches:

---

#### 🧪 Test Branch - Pose-Based Detection

**Algorithm: Static Hand Pose Recognition**

```python
# Count extended fingers
fingers = {
    'thumb': is_thumb_extended(),
    'index': is_finger_extended(8, 6),
    'middle': is_finger_extended(12, 10),
    'ring': is_finger_extended(16, 14),
    'pinky': is_finger_extended(20, 18)
}

# Classify based on combination
if no fingers → FIST (DUCK)
if only index → JUMP
if index + middle → VICTORY (LEFT)
if thumb + index + pinky → I LOVE YOU (RIGHT)
```

**Key Technique:**
- Compares fingertip Y-coordinate to PIP joint Y-coordinate
- Finger is "extended" if tip is above (lower Y) the PIP joint
- Thumb uses different geometry (X-distance from wrist)
- No movement tracking needed

**Advantages:**
- ✅ Stable - not affected by hand shake
- ✅ Low false positive rate
- ✅ Works with camera vibration
- ✅ Clear gesture boundaries

---

#### 🌿 Main Branch - Motion-Based Detection

**Algorithm: Trajectory Analysis**

```python
# Track wrist position over time
history = deque(maxlen=12)  # Last 12 frames
history.append((x, y, timestamp))

# Apply EMA smoothing
x_smooth, y_smooth = ema_update(x, y)

# Calculate movement vector
dx = final_x - initial_x
dy = final_y - initial_y
angle = arctan2(dy, dx)
distance = sqrt(dx² + dy²)

# Classify by angle (degrees)
-45° to 45° → RIGHT
45° to 135° → DOWN (DUCK)
-135° to -45° → UP (JUMP)
±135° to ±180° → LEFT
```

**Key Techniques:**
- Exponential Moving Average (EMA) smoothing reduces jitter
- 12-frame history buffer for stable trajectory
- Minimum velocity threshold prevents drift
- Deadzone filter ignores tiny movements

**Advantages:**
- ✅ Natural swiping motion
- ✅ Feels intuitive
- ✅ All four directions use same technique
- ✅ Familiar for touchscreen users

---

### Performance Optimizations

**Both Branches:**
- EMA (Exponential Moving Average) smoothing reduces jitter
- Cooldown periods prevent double-triggering (0.4-0.5s)
- Efficient MediaPipe model (model_complexity=1)
- Mirror view flip for natural control

**Test Branch Specific:**
- Simple binary finger state detection (up/down)
- No frame history needed
- Instant gesture recognition

**Main Branch Specific:**
- Frame buffering for stable detection (12 frame history)
- Movement velocity calculations
- Angle-based direction classification

### Configuration Parameters

**Test Branch (Pose-Based):**
```python
cooldown_s = 0.4        # Seconds between gestures
mirror_view = True      # Flip camera horizontally
debug = False           # Print detection details
min_detection_confidence = 0.5
min_tracking_confidence = 0.5
```

**Main Branch (Motion-Based):**
```python
buffer_size = 12        # Frame history length
ema_alpha = 0.3         # Smoothing factor (0-1)
dx_thresh = 0.12        # Horizontal movement threshold
dy_thresh = 0.12        # Vertical movement threshold
vmin = 0.08             # Minimum velocity
deadzone = 0.015        # Ignore tiny movements
cooldown_s = 0.5        # Seconds between gestures
mirror_view = True      # Flip camera horizontally
debug = False           # Print detection details
```

## Troubleshooting

### Branch-Specific Issues

**Problem**: Too many false triggers on `main` branch (swipes)
- **Solution**: Switch to `test` branch for static poses: `git checkout test`
- **Reason**: Motion detection can be overly sensitive to hand shake

**Problem**: Gestures feel unnatural on `test` branch (poses)
- **Solution**: Switch to `main` branch for swiping: `git checkout main`
- **Reason**: Some users prefer familiar swiping motions

**Problem**: Can't remember which gestures are in which branch
- **Solution**: See [Branch Differences](#branch-differences) section
- **Quick Reference**:
  - `main`: All four directions use swipes
  - `test`: FIST, INDEX UP, VICTORY, I LOVE YOU

### Camera Issues

**Problem**: "Failed to read from camera"
- **Solution**: Check if camera is being used by another application
- **Solution**: Try a different camera index in `cv2.VideoCapture(0)` → try 1, 2, etc.

**Problem**: Low FPS / Laggy video
- **Solution**: Close other applications using the camera
- **Solution**: Reduce resolution in code (currently 1280x720)
- **Solution**: Lower MediaPipe model complexity to 0

### Gesture Detection Issues

**Problem**: Gestures not detected
- **Solution**: Ensure good lighting on your hand
- **Solution**: Keep hand centered in frame
- **Solution**: Make clear, distinct gestures
- **Solution**: Run `pose_test.py` to calibrate

**Problem**: Wrong gestures detected
- **Solution**: Extend/close fingers more clearly
- **Solution**: Hold poses steadily
- **Solution**: Increase cooldown time in code

**Problem**: Multiple triggers from one gesture
- **Solution**: Cooldown system should prevent this
- **Solution**: Increase `cooldown_s` parameter
- **Solution**: Return to IDLE (open palm) between gestures

### Game Control Issues

**Problem**: Keys not being pressed
- **Solution**: Make sure controller is enabled (press SPACE)
- **Solution**: Check game is in focus (click on game window)
- **Solution**: Verify correct game profile is selected

**Problem**: Wrong keys being pressed
- **Solution**: Press `P` to switch profiles
- **Solution**: Edit `controller.py` to match your game's controls

### Performance Issues

**Problem**: High latency
- **Solution**: Close unnecessary background applications
- **Solution**: Use pose-based system (faster than motion-based)
- **Solution**: Reduce camera resolution

**Problem**: System lag
- **Solution**: Check CPU usage, close heavy applications
- **Solution**: Update graphics drivers
- **Solution**: Try lowering MediaPipe confidence thresholds

## Performance Tips

### For Best Results

1. **Lighting**: Bright, even lighting on your hand
2. **Background**: Plain, contrasting background
3. **Distance**: 2-3 feet from camera optimal
4. **Stability**: Keep hand in center of frame
5. **Camera**: Use external webcam if laptop camera is poor

### Optimal Settings

**Camera Position:**
- Eye level or slightly above
- Centered on your play area
- No backlighting (windows behind you)

**Hand Position:**
- Palm facing camera
- Fingers clearly visible
- Not too close (>1 foot) or far (>5 feet)

**Environment:**
- Well-lit room
- No shadows on hand
- Minimal background motion

### System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 4GB
- Webcam: 720p @ 30fps
- Python 3.8+

**Recommended:**
- CPU: Quad-core 2.5 GHz+
- RAM: 8GB+
- Webcam: 1080p @ 60fps
- Python 3.10+

## Advanced Usage

### Debug Mode

Enable detailed logging:

```python
recognizer = PoseGestureController(debug=True)
```

This prints:
- Extended finger detection
- Gesture classification reasoning
- Timing information

### Custom Cooldown

Adjust trigger frequency:

```python
recognizer = PoseGestureController(cooldown_s=0.3)  # Faster
recognizer = PoseGestureController(cooldown_s=0.7)  # Slower
```

### UI Customization

Toggle UI elements in `ui_controller.py`:

```python
ui_controller.show_skeleton = False     # Hide hand skeleton
ui_controller.show_status_panel = False # Hide status info
ui_controller.show_gesture_guide = False # Hide gesture guide
```

### Recording Sessions

Add frame recording:

```python
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('session.avi', fourcc, 20.0, (1280, 720))
# In main loop:
out.write(display)
```

## Known Limitations

- Single hand detection only
- Requires visible hand (no gloves that hide fingers)
- Sensitive to lighting conditions
- May conflict with existing keyboard shortcuts in some games
- Cooldown prevents very rapid consecutive gestures
- Mirror mode can be confusing initially

## Future Enhancements

Potential improvements:
- [ ] Two-hand gesture support
- [ ] Custom gesture training
- [ ] Mobile app version
- [ ] Wireless connectivity
- [ ] Gesture macros (combos)
- [ ] VR/AR integration
- [ ] Machine learning gesture customization
- [ ] Multi-language UI
- [ ] Cloud-based gesture profiles

## Contributing

Contributions welcome! Areas for improvement:

1. **New Gestures**: Add more gesture types
2. **Game Profiles**: Pre-configure more games
3. **Performance**: Optimization and efficiency
4. **UI/UX**: Better visual feedback
5. **Documentation**: Tutorials and guides

**To contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Credits

**Technologies Used:**
- [MediaPipe](https://google.github.io/mediapipe/) - Google's hand tracking
- [OpenCV](https://opencv.org/) - Computer vision library
- [PyNput](https://pynput.readthedocs.io/) - Keyboard control
- [NumPy](https://numpy.org/) - Numerical computing

## License

This project is provided as-is for educational and personal use. 

**Note**: Ensure you have permission to use automation tools with any games you play, as some games may have policies against automated input.

## Support

Having issues? Try these resources:

1. Read [Troubleshooting](#troubleshooting) section
2. Check `REFACTORING_README.md` for pose system details
3. Run `pose_test.py` to diagnose gesture detection
4. Review code comments for implementation details

## Changelog

### Version 2.0 (Test Branch)
- ✨ Added pose-based gesture system
- ✨ Victory and I Love You gestures for LEFT/RIGHT
- ⚡ Improved stability and accuracy
- 🎨 Enhanced UI with gesture guide
- 📝 Comprehensive documentation
- 🔧 Removed movement tracking for LEFT/RIGHT
- ✅ Static pose detection for all gestures

### Version 1.0 (Main Branch - Current Stable)
- 🎉 Initial release
- ✅ Motion-based gesture recognition
- ✅ Swiping gestures for all four directions
- ✅ Basic game profiles (Subway Surfers, Temple Run)
- ✅ Performance tracking
- ✅ Hand skeleton visualization
- ✅ EMA smoothing and trajectory analysis

### Branch Comparison

| Feature | Main (v1.0) | Test (v2.0) |
|---------|-------------|-------------|
| LEFT/RIGHT Control | Swipe motions | Static poses |
| UP/DOWN Control | Swipe motions | Static poses |
| Stability | Good | Excellent |
| Intuitiveness | High | Medium |
| False Positives | Moderate | Low |

---

**Ready to play hands-free?** 

1. Choose your branch: `git checkout test` (poses) or `git checkout main` (swipes)
2. Test gestures: `python pose_test.py` or `python gesture_test.py`
3. Start playing: `python pose_main.py`

⭐ If you found this project useful, consider giving it a star!

💡 **Tip**: Most users find the `test` branch more stable for gaming!