import logging

# Pragmatic Dependency
try:
    from src.infra.audit import get_audit_manager
    _AUDIT_AVAILABLE = True
except ImportError:
    _AUDIT_AVAILABLE = False

logger = logging.getLogger("core_audit")

class AuditLogger:
    """
    Wrapper for Audit Logging.
    """
    def __init__(self):
        self.manager = None
        if not _AUDIT_AVAILABLE:
             return
             
        try:
            self.manager = get_audit_manager()
        except Exception as e:
            logger.warning(f"Failed to init AuditManager: {e}")

    def log_processing(self, user_id: str, input_text: str, output_text: str, seasoning: int, ai_model: str) -> None:
        if not self.manager:
            return
        try:
            self.manager.log_processing(
                user_id=user_id,
                input_text=input_text,
                output_text=output_text,
                seasoning=seasoning,
                ai_model=ai_model
            )
        except Exception as e:
            logger.warning(f"Audit log failed: {e}")
