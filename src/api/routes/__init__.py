"""
API Routes Package
"""
from .health import router as health_router
from .core import router as core_router, set_processor as set_core_processor
from .safety import router as safety_router, set_processor as set_safety_processor
from .features import router as features_router, set_processor as set_features_processor
from .vision import router as vision_router
from .legacy import router as legacy_router
from .audit import router as audit_router

__all__ = [
    "health_router",
    "core_router", 
    "safety_router",
    "features_router",
    "vision_router",
    "legacy_router",
    "audit_router",
    "set_core_processor",
    "set_safety_processor", 
    "set_features_processor",
]
