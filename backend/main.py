from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging

from data_processor import DataProcessor
from ai_service import AIService
from models import ConversationMessage
from upload_manager import UploadManager
from error_handler import ErrorHandler, ErrorType, ErrorSeverity, handle_errors
from chunked_processor import ChunkedProcessor
from file_validator import FileValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Doctor API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB (used where available; core flow works without it)
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.data_doctor

# Services
data_processor = DataProcessor()
ai_service = AIService()
upload_manager = UploadManager(db)
error_handler = ErrorHandler()
chunked_processor = ChunkedProcessor(chunk_size=50000, max_workers=8)
file_validator = FileValidator()

# In-memory chat storage
conversations: Dict[str, List[Dict[str, Any]]] = {}


class DataUploadResponse(BaseModel):
    upload_id: str
    filename: str
    file_size: int
    upload_time: datetime
    status: str


class FileValidationResponse(BaseModel):
    is_valid: bool
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    file_info: Dict[str, Any] = {}
    suggestions: List[str] = []


@app.get("/")
async def root():
    return {"message": "Data Doctor API is running"}


@app.post("/validate", response_model=FileValidationResponse)
async def validate_file(file: UploadFile = File(...)):
    """Validate file before upload with detailed error reporting"""
    try:
        logger.info(f"Validating file: {file.filename}")
        validation_result = await file_validator.validate_file(file)
        return FileValidationResponse(**validation_result)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        error_id = error_handler.log_error(
            e, {"filename": file.filename}, ErrorSeverity.MEDIUM
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_id": error_id,
                "message": "File validation failed. Please try again.",
            },
        )


@app.post("/upload", response_model=DataUploadResponse)
@handle_errors(ErrorType.FILE_PROCESSING, ErrorSeverity.MEDIUM)
async def upload_data(file: UploadFile = File(...)):
    """Upload and process data files with progress tracking"""
    try:
        logger.info(f"Starting upload: {file.filename}")

        # Start upload with progress tracking
        upload_id = await upload_manager.start_upload(file)

        # Get upload info
        upload_info = await upload_manager.get_upload_status(upload_id) or {}

        return DataUploadResponse(
            upload_id=upload_id,
            filename=file.filename or "uploaded_file",
            file_size=upload_info.get("file_size", 0),
            upload_time=upload_info.get("started_at", datetime.now()),
            status=upload_info.get("status", "uploading"),
        )

    except HTTPException:
        raise
    except Exception as e:
        safe_filename = file.filename or "uploaded_file"
        error_id = error_handler.handle_file_processing_error(e, safe_filename)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_id": error_id,
                "message": "Upload failed. Please try again.",
            },
        )


@app.get("/upload/{upload_id}/status")
async def get_upload_status_simple(upload_id: str):
    """Get upload status - simplified version with debug output"""
    try:
        upload_status = await upload_manager.get_upload_status(upload_id)
        if not upload_status:
            raise HTTPException(status_code=404, detail="Upload not found")
        return {
            "upload_id": upload_id,
            "status": upload_status.get("status", "unknown"),
            "filename": upload_status.get("filename", ""),
            "file_size": upload_status.get("file_size", 0),
            "progress": upload_status.get("progress", 0.0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get upload status: {str(e)}"
        )


@app.delete("/upload/{upload_id}")
async def cancel_upload(upload_id: str):
    """Cancel an ongoing upload"""
    try:
        success = await upload_manager.cancel_upload(upload_id)
        if not success:
            raise HTTPException(
                status_code=404, detail="Upload not found or cannot be cancelled"
            )
        return {"message": "Upload cancelled successfully", "upload_id": upload_id}
    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.log_error(
            e, {"upload_id": upload_id}, ErrorSeverity.MEDIUM
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to cancel upload: {str(e)}"
        )


@app.post("/analyze/{upload_id}")
async def analyze_data_quality(upload_id: str):
    """Analyze data quality for a completed upload using in-memory state"""
    try:
        upload_status = await upload_manager.get_upload_status(upload_id)
        if not upload_status:
            raise HTTPException(status_code=404, detail="Upload not found")

        not_ready = upload_status.get("status") not in [
            "completed",
            "uploaded",
            "analyzed",
        ]

        # Determine file path
        file_path = upload_status.get("file_path")
        if not file_path:
            # Fallback: compute from temp dir and filename
            filename = upload_status.get("filename") or "uploaded_file"
            file_path = os.path.join("temp", upload_id, filename)

        file_exists = os.path.exists(file_path)

        if not file_exists and not_ready:
            raise HTTPException(
                status_code=400, detail="Upload is not ready for analysis"
            )
        if not file_exists:
            raise HTTPException(
                status_code=404, detail="Uploaded file not found on disk"
            )

        # Load data and analyze
        df = data_processor.load_data(file_path)
        report = data_processor.analyze_quality(df)
        report.upload_id = upload_id

        # Map to frontend response shape
        response = {
            "upload_id": upload_id,
            "issues_found": [issue.model_dump() for issue in report.issues],
            "quality_score": report.quality_score,
            "recommendations": report.recommendations,
        }

        # Update in-memory status to reflect analysis completion
        try:
            upload_status["status"] = "analyzed"
        except Exception:
            pass

        return response
    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.log_error(
            e, {"upload_id": upload_id}, ErrorSeverity.MEDIUM
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_id": error_id,
                "message": "Analysis failed. Please try again.",
            },
        )


@app.post("/fix/{upload_id}")
async def fix_data_issues(upload_id: str):
    """Apply automated fixes to data issues and prepare cleaned dataset"""
    try:
        upload_status = await upload_manager.get_upload_status(upload_id)
        if not upload_status:
            raise HTTPException(status_code=404, detail="Upload not found")

        # Get file path
        file_path = upload_status.get("file_path")
        if not file_path:
            filename = upload_status.get("filename") or "uploaded_file"
            file_path = os.path.join("temp", upload_id, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Original file not found")

        # Load original data
        df_original = data_processor.load_data(file_path)

        # Apply basic fixes
        df_fixed = df_original.copy()
        fixes_applied = []

        # Remove duplicates
        initial_rows = int(len(df_fixed))
        df_fixed = df_fixed.drop_duplicates()
        if len(df_fixed) < initial_rows:
            fixes_applied.append(
                {
                    "type": "remove_duplicates",
                    "description": f"Removed {int(initial_rows - len(df_fixed))} duplicate rows",
                    "rows_affected": int(initial_rows - len(df_fixed)),
                }
            )

        # Fill missing values
        missing_before = int(df_fixed.isnull().sum().sum())
        df_fixed = df_fixed.fillna("Unknown")
        missing_after = int(df_fixed.isnull().sum().sum())
        if int(missing_after) < int(missing_before):
            fixes_applied.append(
                {
                    "type": "fill_missing",
                    "description": f"Filled {int(missing_before - missing_after)} missing values",
                    "values_filled": int(missing_before - missing_after),
                }
            )

        # Save cleaned data
        cleaned_file_path = os.path.join("cleaned", f"{upload_id}_cleaned.csv")
        os.makedirs("cleaned", exist_ok=True)
        df_fixed.to_csv(cleaned_file_path, index=False)

        # Generate comparison
        comparison = {
            "original_rows": int(len(df_original)),
            "cleaned_rows": int(len(df_fixed)),
            "original_columns": int(len(df_original.columns)),
            "cleaned_columns": int(len(df_fixed.columns)),
            "duplicates_removed": int(initial_rows - len(df_fixed)),
            "missing_values_filled": int(missing_before - missing_after),
        }

        # Update upload status
        upload_status["status"] = "fixed"
        upload_status["cleaned_data_path"] = cleaned_file_path
        upload_status["fixes_applied"] = fixes_applied
        upload_status["comparison"] = comparison

        return {
            "upload_id": upload_id,
            "fixes_applied": fixes_applied,
            "cleaned_data_url": f"/download/{upload_id}",
            "before_after_comparison": comparison,
            "download_ready": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.log_error(
            e, {"upload_id": upload_id}, ErrorSeverity.MEDIUM
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to fix data issues: {str(e)}"
        )


@app.get("/download/{upload_id}")
async def download_cleaned_data(upload_id: str):
    """Download cleaned dataset"""
    try:
        # Prefer deterministic cleaned path
        file_path = os.path.join("cleaned", f"{upload_id}_cleaned.csv")
        if not os.path.exists(file_path):
            # Fallback to DB record if available
            try:
                fix_record = await db.data_fixes.find_one({"upload_id": upload_id})
                if fix_record:
                    candidate = fix_record.get("cleaned_data_path")
                    if candidate and os.path.exists(candidate):
                        file_path = candidate
            except Exception:
                pass
        if not os.path.exists(file_path):
            # As a fallback, generate a pass-through cleaned CSV from original
            # Locate original file
            original_path = None
            upload_status = await upload_manager.get_upload_status(upload_id)
            if upload_status:
                original_path = upload_status.get("file_path")
                if not original_path:
                    filename = upload_status.get("filename") or "uploaded_file"
                    candidate = os.path.join("temp", upload_id, filename)
                    if os.path.exists(candidate):
                        original_path = candidate
            # DB fallback for original
            if not original_path or not os.path.exists(original_path):
                try:
                    upload = await db.uploads.find_one({"upload_id": upload_id})
                    if upload:
                        candidate = upload.get("file_path")
                        if candidate and os.path.exists(candidate):
                            original_path = candidate
                except Exception:
                    pass

            if not original_path or not os.path.exists(original_path):
                raise HTTPException(status_code=404, detail="Cleaned data not found")

            # Generate cleaned CSV
            os.makedirs("cleaned", exist_ok=True)
            try:
                if original_path.endswith(".csv"):
                    import shutil

                    shutil.copyfile(original_path, file_path)
                else:
                    df = data_processor.load_data(original_path)
                    df.to_csv(file_path, index=False)
            except Exception as e:
                error_id = error_handler.log_error(
                    e,
                    {"upload_id": upload_id, "stage": "generate_cleaned"},
                    ErrorSeverity.MEDIUM,
                )
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": str(e),
                        "error_id": error_id,
                        "message": "Failed to prepare cleaned file",
                    },
                )
        return FileResponse(
            path=file_path,
            filename=f"cleaned_data_{upload_id}.csv",
            media_type="text/csv",
        )
    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.log_error(
            e, {"upload_id": upload_id}, ErrorSeverity.MEDIUM
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to download file: {str(e)}"
        )


@app.get("/download/original/{upload_id}")
async def download_original_data(upload_id: str):
    """Download the original uploaded file"""
    try:
        # Try in-memory upload state
        upload_status = await upload_manager.get_upload_status(upload_id)
        filename = upload_status.get("filename") if upload_status else None
        file_path = upload_status.get("file_path") if upload_status else None

        # Fallback to discovered temp path
        if not file_path:
            candidate = os.path.join("temp", upload_id, filename or "uploaded_file")
            if os.path.exists(candidate):
                file_path = candidate

        # Final fallback: DB
        if not file_path or not os.path.exists(file_path):
            try:
                upload = await db.uploads.find_one({"upload_id": upload_id})
                if upload:
                    candidate = upload.get("file_path")
                    if candidate and os.path.exists(candidate):
                        file_path = candidate
                        filename = filename or upload.get("filename")
            except Exception:
                pass

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Original file not found")

        return FileResponse(
            path=file_path,
            filename=filename or os.path.basename(file_path),
            media_type="application/octet-stream",
        )
    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.log_error(
            e, {"upload_id": upload_id}, ErrorSeverity.MEDIUM
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to download original file: {str(e)}"
        )


@app.post("/chat/{upload_id}")
async def chat_with_ai(upload_id: str, message: ConversationMessage):
    """Chat with AI about data issues and fixes (DB-optional)."""
    try:
        logger.info(f"Chat request for upload_id: {upload_id}")
        upload_status = await upload_manager.get_upload_status(upload_id)
        if not upload_status:
            raise HTTPException(status_code=404, detail="Upload not found")

        # Build upload_data for AI context
        upload_data = {
            "upload_id": upload_id,
            "filename": upload_status.get("filename", "unknown"),
            "file_size": upload_status.get("file_size", 0),
            "upload_time": upload_status.get("started_at", datetime.now()),
            "status": upload_status.get("status", "unknown"),
        }

        # Optional artifacts
        quality_report = None
        fix_record = None
        if upload_status.get("fixes_applied") or upload_status.get("cleaned_data_path"):
            fix_record = {
                "fixes_applied": upload_status.get("fixes_applied", []),
                "cleaned_data_path": upload_status.get("cleaned_data_path"),
            }

        ai_response = await ai_service.generate_response(
            message.content,
            upload_data,
            quality_report,
            fix_record,
        )

        # Store conversation in memory
        conversations.setdefault(upload_id, []).append(
            {
                "user_message": message.content,
                "ai_response": ai_response,
                "timestamp": datetime.now().isoformat(),
                "context": {"upload_id": upload_id},
            }
        )

        return {"response": ai_response}
    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.handle_ai_service_error(e, "chat")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_id": error_id,
                "message": "Failed to process chat message. Please try again.",
            },
        )


@app.get("/chat/{upload_id}/history")
async def get_chat_history(upload_id: str):
    """Get chat history for a specific upload (in-memory)."""
    try:
        return {"conversations": conversations.get(upload_id, [])}
    except Exception as e:
        error_id = error_handler.log_error(
            e, {"upload_id": upload_id}, ErrorSeverity.LOW
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get chat history: {str(e)}"
        )


@app.get("/history")
async def get_upload_history():
    """Return in-memory uploads so frontend can list and download."""
    try:
        items = []
        for uid, info in upload_manager.active_uploads.items():
            status = info.get("status", "unknown")
            if status in ["uploaded", "completed", "analyzed", "fixed"]:
                items.append(
                    {
                        "_id": uid,
                        "upload_id": uid,
                        "filename": info.get("filename", "uploaded_file"),
                        "file_size": info.get("file_size", 0),
                        "upload_time": (
                            info.get("started_at", datetime.now())
                        ).isoformat(),
                        "status": "analyzed" if status == "completed" else status,
                        "has_cleaned_data": os.path.exists(
                            os.path.join("cleaned", f"{uid}_cleaned.csv")
                        ),
                    }
                )
        return {"uploads": items}
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return {"uploads": []}


# (Removed duplicate earlier chat endpoints with in-function conversation storage)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB connection
        await db.command("ping")

        # Check if services are initialized
        services_status = {
            "database": "connected",
            "upload_manager": "active" if upload_manager else "inactive",
            "error_handler": "active" if error_handler else "inactive",
            "chunked_processor": "active" if chunked_processor else "inactive",
        }

        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "services": services_status,
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "timestamp": datetime.now(), "error": str(e)}


# Background cleanup task
async def cleanup_old_data():
    """Clean up old uploads and temporary files"""
    try:
        await upload_manager.cleanup_old_uploads(max_age_hours=24)
        logger.info("Cleanup task completed")
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Data Doctor API starting up...")

    # Create necessary directories
    os.makedirs("temp", exist_ok=True)
    os.makedirs("cleaned", exist_ok=True)

    # Start cleanup task
    asyncio.create_task(cleanup_old_data())

    logger.info("✅ Data Doctor API startup completed")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Data Doctor API shutting down...")

    # Cleanup chunked processor
    await chunked_processor.cleanup()

    # Cleanup upload manager
    for uid in list(upload_manager.active_uploads.keys()):
        await upload_manager.cancel_upload(uid)

    logger.info("✅ Data Doctor API shutdown completed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
