"""
Gesture Recognizer Module.

This module provides backwards compatibility and re-exports the recognizer classes.
For new code, import directly from:
  - gesture_interface (GestureRecognizerInterface, GestureResult)
  - recognizer_mediapipe (GestureRecognizerMP)
  - recognizer_hybrid (HybridGestureRecognizer)
"""

# Re-export for backwards compatibility
from .gesture_interface import GestureRecognizerInterface, GestureResult
from .recognizer_mediapipe import GestureRecognizerMP, LABEL_TO_ACTION
from .recognizer_hybrid import HybridGestureRecognizer

__all__ = [
    "GestureRecognizerInterface",
    "GestureResult",
    "GestureRecognizerMP",
    "HybridGestureRecognizer",
    "LABEL_TO_ACTION",
]
