"""
Gesture Recognizer Factory.

Provides a factory pattern for creating gesture recognizers based on type,
plus a singleton manager for shared access across the app.
"""

from enum import Enum, auto
from typing import Optional
import threading

from .gesture_interface import GestureRecognizerInterface
from .recognizer_mediapipe import GestureRecognizerMP
from .recognizer_hybrid import HybridGestureRecognizer
from .paths import asset_path


class RecognizerType(Enum):
    """
    Available gesture recognizer implementations.
    
    MEDIAPIPE_TASKS: Uses the pre-trained gesture_recognizer.task model.
                     Good for recognizing specific poses (Victory, ILoveYou, etc.)
                     
    HYBRID_POSE:     Uses MediaPipe Hands with custom pose classification.
                     Better for motion-based gestures (swipe left/right).
    """
    MEDIAPIPE_TASKS = "MEDIATYPE_TASKS"
    HYBRID_POSE = "HYBRID_POSE"


class RecognizerFactory:
    """
    Factory for creating gesture recognizer instances.
    
    Usage:
        recognizer = RecognizerFactory.create(RecognizerType.MEDIAPIPE_TASKS)
        # or
        recognizer = RecognizerFactory.create(RecognizerType.HYBRID_POSE)
    """
    
    @staticmethod
    def create(
        recognizer_type: RecognizerType=RecognizerType.MEDIAPIPE_TASKS,
        model_path: Optional[str] = None,
        min_score: float = 0.60,
        mirror_view: bool = True,
        **kwargs,
    ) -> GestureRecognizerInterface:
        """
        Create a gesture recognizer of the specified type.
        
        Args:
            recognizer_type: The type of recognizer to create
            model_path: Path to model file (only used for MEDIAPIPE_TASKS)
            min_score: Minimum confidence threshold
            mirror_view: Whether to flip the frame horizontally
            **kwargs: Additional arguments passed to the recognizer constructor
            
        Returns:
            An instance of GestureRecognizerInterface
            
        Raises:
            ValueError: If an unknown recognizer type is provided
        """
        if recognizer_type == RecognizerType.MEDIAPIPE_TASKS:
            if model_path is None:
                model_path = asset_path("gesture_recognizer.task")
            return GestureRecognizerMP(
                model_path=model_path,
                min_score=min_score,
                mirror_view=mirror_view,
                **kwargs,
            )
        
        elif recognizer_type == RecognizerType.HYBRID_POSE:
            return HybridGestureRecognizer(
                min_detection_confidence=min_score,
                mirror_view=mirror_view,
                **kwargs,
            )
        
        else:
            raise ValueError(f"Unknown recognizer type: {recognizer_type}")
    
    @staticmethod
    def get_available_types() -> list[RecognizerType]:
        """Get list of all available recognizer types."""
        return list(RecognizerType)
    
    @staticmethod
    def get_type_description(recognizer_type: RecognizerType) -> str:
        """Get a human-readable description of a recognizer type."""
        descriptions = {
            RecognizerType.MEDIAPIPE_TASKS: (
                "MediaPipe Tasks API - Uses pre-trained model for gesture recognition. "
                "Best for: Victory, ILoveYou, Pointing_Up, Closed_Fist, Thumb_Up gestures."
            ),
            RecognizerType.HYBRID_POSE: (
                "Hybrid Pose-Based - Uses finger position tracking with motion detection. "
                "Best for: Motion-based gestures like swiping left/right."
            ),
        }
        return descriptions.get(recognizer_type, "Unknown recognizer type")


class RecognizerSingleton:
    """
    Singleton manager for the gesture recognizer instance.
    
    Provides a single shared recognizer instance across the entire application.
    Thread-safe initialization.
    
    Usage:
        # Configure once at app startup
        RecognizerSingleton.configure(RecognizerType.MEDIAPIPE_TASKS)
        
        # Get the instance anywhere in the app
        recognizer = RecognizerSingleton.get_instance()
        result = recognizer.process(frame)
        
        # Switch to a different recognizer type
        RecognizerSingleton.configure(RecognizerType.HYBRID_POSE)
    """
    
    _instance: Optional[GestureRecognizerInterface] = None
    _current_type: Optional[RecognizerType] = None
    _lock = threading.Lock()
    
    @classmethod
    def configure(
        cls,
        recognizer_type: RecognizerType,
        model_path: Optional[str] = None,
        min_score: float = 0.60,
        mirror_view: bool = True,
        force_recreate: bool = False,
        **kwargs,
    ) -> GestureRecognizerInterface:
        """
        Configure and create the singleton recognizer instance.
        
        Args:
            recognizer_type: The type of recognizer to create
            model_path: Path to model file (only for MEDIAPIPE_TASKS)
            min_score: Minimum confidence threshold
            mirror_view: Whether to flip the frame horizontally
            force_recreate: If True, recreate even if same type exists
            **kwargs: Additional arguments for the recognizer
            
        Returns:
            The configured recognizer instance
        """
        with cls._lock:
            # Skip if same type already exists and not forcing recreate
            if (
                not force_recreate
                and cls._instance is not None
                and cls._current_type == recognizer_type
            ):
                print(f"[RecognizerSingleton] Reusing existing {recognizer_type.name} instance")
                return cls._instance
            
            # Cleanup existing instance
            if cls._instance is not None:
                print(f"[RecognizerSingleton] Cleaning up old {cls._current_type.name} instance")
                cls._instance.cleanup()
                cls._instance = None
            
            # Create new instance
            print(f"[RecognizerSingleton] Creating new {recognizer_type.name} instance")
            cls._instance = RecognizerFactory.create(
                recognizer_type=recognizer_type,
                model_path=model_path,
                min_score=min_score,
                mirror_view=mirror_view,
                **kwargs,
            )
            cls._current_type = recognizer_type
            
            return cls._instance
    
    @classmethod
    def get_instance(cls) -> GestureRecognizerInterface:
        """
        Get the current recognizer instance.
        
        If not configured, creates a default MEDIAPIPE_TASKS recognizer.
        
        Returns:
            The gesture recognizer instance
        """
        with cls._lock:
            if cls._instance is None:
                print("[RecognizerSingleton] No instance configured, creating default MEDIAPIPE_TASKS")
                cls._instance = RecognizerFactory.create(RecognizerType.MEDIAPIPE_TASKS)
                cls._current_type = RecognizerType.MEDIAPIPE_TASKS
            return cls._instance
    
    @classmethod
    def get_current_type(cls) -> Optional[RecognizerType]:
        """Get the current recognizer type, or None if not configured."""
        return cls._current_type
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if a recognizer instance exists."""
        return cls._instance is not None
    
    @classmethod
    def cleanup(cls) -> None:
        """Clean up the singleton instance."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.cleanup()
                cls._instance = None
                cls._current_type = None
                print("[RecognizerSingleton] Instance cleaned up")


# Convenience function
def get_recognizer() -> GestureRecognizerInterface:
    """
    Get the singleton recognizer instance.
    
    Shorthand for RecognizerSingleton.get_instance()
    """
    return RecognizerSingleton.get_instance()
