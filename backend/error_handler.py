import asyncio
import logging
import traceback
from typing import Any, Dict, Optional, Callable, Type
from datetime import datetime, timedelta
from enum import Enum
import functools

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorType(Enum):
    NETWORK = "network"
    DATABASE = "database"
    FILE_PROCESSING = "file_processing"
    AI_SERVICE = "ai_service"
    VALIDATION = "validation"
    SYSTEM = "system"

class RetryableError(Exception):
    """Exception that can be retried"""
    def __init__(self, message: str, retry_after: int = 5, max_retries: int = 3):
        self.message = message
        self.retry_after = retry_after
        self.max_retries = max_retries
        super().__init__(message)

class NonRetryableError(Exception):
    """Exception that should not be retried"""
    pass

class ErrorHandler:
    def __init__(self):
        self.error_log: Dict[str, Dict[str, Any]] = {}
        self.retry_configs = {
            ErrorType.NETWORK: {"max_retries": 3, "backoff_factor": 2, "base_delay": 1},
            ErrorType.DATABASE: {"max_retries": 2, "backoff_factor": 1.5, "base_delay": 2},
            ErrorType.FILE_PROCESSING: {"max_retries": 1, "backoff_factor": 1, "base_delay": 1},
            ErrorType.AI_SERVICE: {"max_retries": 2, "backoff_factor": 2, "base_delay": 3},
            ErrorType.VALIDATION: {"max_retries": 0, "backoff_factor": 1, "base_delay": 0},
            ErrorType.SYSTEM: {"max_retries": 1, "backoff_factor": 1, "base_delay": 5}
        }
    
    def log_error(
        self, 
        error: Exception, 
        context: Dict[str, Any], 
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_type: ErrorType = ErrorType.SYSTEM
    ) -> str:
        """Log an error and return error ID"""
        error_id = f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(error)}"
        
        error_info = {
            "error_id": error_id,
            "timestamp": datetime.now(),
            "error_type": error_type.value,
            "severity": severity.value,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
            "resolved": False
        }
        
        self.error_log[error_id] = error_info
        
        # Log to console based on severity
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(severity, logging.ERROR)
        
        logger.log(log_level, f"Error {error_id}: {str(error)}")
        
        return error_id
    
    async def retry_with_backoff(
        self,
        func: Callable,
        error_type: ErrorType,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic and exponential backoff"""
        config = self.retry_configs[error_type]
        max_retries = config["max_retries"]
        backoff_factor = config["backoff_factor"]
        base_delay = config["base_delay"]
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except RetryableError as e:
                last_exception = e
                if attempt < max_retries:
                    delay = base_delay * (backoff_factor ** attempt)
                    logger.warning(f"Retryable error on attempt {attempt + 1}: {str(e)}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Max retries exceeded for {func.__name__}")
                    break
                    
            except NonRetryableError as e:
                logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
                raise e
                
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = base_delay * (backoff_factor ** attempt)
                    logger.warning(f"Unexpected error on attempt {attempt + 1}: {str(e)}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Max retries exceeded for {func.__name__}")
                    break
        
        # If we get here, all retries failed
        if last_exception:
            self.log_error(
                last_exception,
                {"function": func.__name__, "args": str(args), "kwargs": str(kwargs)},
                ErrorSeverity.HIGH,
                error_type
            )
            raise last_exception
    
    def handle_database_error(self, error: Exception, operation: str) -> str:
        """Handle database-specific errors"""
        context = {"operation": operation, "error_type": "database"}
        
        if "connection" in str(error).lower():
            severity = ErrorSeverity.HIGH
            error_type = ErrorType.DATABASE
        elif "timeout" in str(error).lower():
            severity = ErrorSeverity.MEDIUM
            error_type = ErrorType.DATABASE
        else:
            severity = ErrorSeverity.MEDIUM
            error_type = ErrorType.DATABASE
        
        return self.log_error(error, context, severity, error_type)
    
    def handle_file_processing_error(self, error: Exception, filename: str) -> str:
        """Handle file processing errors"""
        context = {"filename": filename, "error_type": "file_processing"}
        
        if "permission" in str(error).lower():
            severity = ErrorSeverity.HIGH
        elif "not found" in str(error).lower():
            severity = ErrorSeverity.MEDIUM
        elif "format" in str(error).lower():
            severity = ErrorSeverity.MEDIUM
        else:
            severity = ErrorSeverity.MEDIUM
        
        return self.log_error(error, context, severity, ErrorType.FILE_PROCESSING)
    
    def handle_ai_service_error(self, error: Exception, service: str) -> str:
        """Handle AI service errors"""
        context = {"service": service, "error_type": "ai_service"}
        
        if "rate limit" in str(error).lower():
            severity = ErrorSeverity.MEDIUM
        elif "authentication" in str(error).lower():
            severity = ErrorSeverity.HIGH
        elif "quota" in str(error).lower():
            severity = ErrorSeverity.HIGH
        else:
            severity = ErrorSeverity.MEDIUM
        
        return self.log_error(error, context, severity, ErrorType.AI_SERVICE)
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = {
            error_id: error_info 
            for error_id, error_info in self.error_log.items()
            if error_info["timestamp"] > cutoff_time
        }
        
        # Group by severity
        severity_counts = {}
        error_type_counts = {}
        
        for error_info in recent_errors.values():
            severity = error_info["severity"]
            error_type = error_info["error_type"]
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "severity_breakdown": severity_counts,
            "error_type_breakdown": error_type_counts,
            "time_range_hours": hours,
            "unresolved_errors": len([e for e in recent_errors.values() if not e["resolved"]])
        }
    
    def mark_error_resolved(self, error_id: str) -> bool:
        """Mark an error as resolved"""
        if error_id in self.error_log:
            self.error_log[error_id]["resolved"] = True
            self.error_log[error_id]["resolved_at"] = datetime.now()
            return True
        return False

# Decorator for automatic error handling
def handle_errors(error_type: ErrorType = ErrorType.SYSTEM, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Decorator to automatically handle errors in functions"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            try:
                return await error_handler.retry_with_backoff(func, error_type, *args, **kwargs)
            except Exception as e:
                error_id = error_handler.log_error(
                    e,
                    {"function": func.__name__, "args": str(args), "kwargs": str(kwargs)},
                    severity,
                    error_type
                )
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": str(e),
                        "error_id": error_id,
                        "message": "An error occurred while processing your request"
                    }
                )
        return wrapper
    return decorator
