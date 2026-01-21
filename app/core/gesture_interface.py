"""
Abstract interface for gesture recognition implementations.

This defines the contract that all gesture recognizers must follow,
allowing easy swapping between different recognition backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import numpy as np


@dataclass
class GestureResult:
    """
    Standardized result from gesture recognition.
    
    Attributes:
        frame: The processed frame (possibly mirrored)
        action: The detected action ("LEFT", "RIGHT", "JUMP", "DUCK", "SPACE", "IDLE")
        raw_label: The raw gesture label from the recognizer (e.g., "Victory", "Closed_Fist")
        confidence: Confidence score (0.0 - 1.0)
        landmarks: Hand landmarks for visualization (format depends on implementation)
    """
    frame: np.ndarray
    action: str
    raw_label: Optional[str]
    confidence: float
    landmarks: Optional[Any]


class GestureRecognizerInterface(ABC):
    """
    Abstract base class for gesture recognition.
    
    All gesture recognizer implementations must inherit from this class
    and implement the required methods.
    """
    
    @abstractmethod
    def process(self, frame_bgr: np.ndarray) -> GestureResult:
        """
        Process a single BGR frame and detect gestures.
        
        Args:
            frame_bgr: Input frame in BGR format (as returned by cv2.VideoCapture)
            
        Returns:
            GestureResult containing the processed frame, detected action,
            raw label, confidence score, and optional landmarks.
        """
        pass
    
    @abstractmethod
    def draw_landmarks(self, frame: np.ndarray, landmarks: Any) -> np.ndarray:
        """
        Draw hand landmarks on the frame for visualization.
        
        Args:
            frame: The frame to draw on
            landmarks: Hand landmarks returned from process()
            
        Returns:
            Frame with landmarks drawn
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this recognizer implementation."""
        pass

    @property
    @abstractmethod
    def keyMap(self) -> dict[str,str]:
        """Return the gesture key map of this recognizer implementation."""
        pass
    
    def cleanup(self) -> None:
        """
        Optional cleanup method. Override if your implementation
        needs to release resources.
        """
        pass
