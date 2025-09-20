from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json
import logging
from data_processor import DataProcessor
from ai_service import AIService
from models import DataUpload, DataQualityReport, DataFix, ConversationMessage
from upload_manager import UploadManager
from error_handler import ErrorHandler, ErrorType, ErrorSeverity, handle_errors
from chunked_processor import ChunkedProcessor, analyze_chunk_quality, apply_chunk_fixes
from file_validator import FileValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Doctor API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.data_doctor

# Initialize services
data_processor = DataProcessor()
ai_service = AIService()
upload_manager = UploadManager(db)
error_handler = ErrorHandler()
chunked_processor = ChunkedProcessor(chunk_size=50000, max_workers=8)
file_validator = FileValidator()


class DataUploadResponse(BaseModel):
    upload_id: str
    filename: str
    file_size: int
    upload_time: datetime
    status: str


class DataQualityResponse(BaseModel):
    upload_id: str
    issues_found: List[Dict[str, Any]]
    quality_score: float
    recommendations: List[str]


class DataFixResponse(BaseModel):
    upload_id: str
    fixes_applied: List[DataFix]
    cleaned_data_url: str
    before_after_comparison: Dict[str, Any]


class UploadStatusResponse(BaseModel):
    upload_id: str
    status: str
    progress: float
    filename: str
    file_size: int
    error: Optional[str] = None


class ProgressUpdate(BaseModel):
    upload_id: str
    progress: float
    stage: str
    message: str


class ValidationError(BaseModel):
    type: str
    message: str
    details: Optional[str] = None
    suggestion: str


class ValidationWarning(BaseModel):
    type: str
    message: str
    details: Optional[str] = None
    suggestion: str


class FileValidationResponse(BaseModel):
    is_valid: bool
    errors: List[ValidationError] = []
    warnings: List[ValidationWarning] = []
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

        # Perform comprehensive validation
        validation_result = await file_validator.validate_file(file)

        # Convert to response format
        errors = [
            ValidationError(**error) for error in validation_result.get("errors", [])
        ]
        warnings = [
            ValidationWarning(**warning)
            for warning in validation_result.get("warnings", [])
        ]

        return FileValidationResponse(
            is_valid=validation_result["is_valid"],
            errors=errors,
            warnings=warnings,
            file_info=validation_result.get("file_info", {}),
            suggestions=validation_result.get("suggestions", []),
        )

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

        # TEMPORARILY SKIP VALIDATION FOR DEBUGGING
        print(f"🐛 DEBUG: Skipping validation for file: {file.filename}")

        # Start upload with progress tracking
        upload_id = await upload_manager.start_upload(file)
        print(f"🐛 DEBUG: Upload manager returned upload_id: {upload_id}")

        # Get upload info
        upload_info = await upload_manager.get_upload_status(upload_id) or {}
        print(f"🐛 DEBUG: Upload info: {upload_info}")

        return DataUploadResponse(
            upload_id=upload_id,
            filename=file.filename if file.filename is not None else "uploaded_file",
            file_size=upload_info.get("file_size", 0),
            upload_time=upload_info.get("started_at", datetime.now()),
            status=upload_info.get("status", "uploading"),
        )

    except HTTPException:
        raise
    except Exception as e:
        safe_filename = file.filename if file.filename is not None else "uploaded_file"
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
        print(f"🔍 Checking status for upload_id: {upload_id}")

        # Use upload manager instead of direct database query
        upload_status = await upload_manager.get_upload_status(upload_id)
        if not upload_status:
            print(f"❌ Upload not found in upload manager")
            # Check if it exists in other collections (when database is enabled)
            # quality_report = await db.quality_reports.find_one({"upload_id": upload_id})
            # if quality_report:
            #     print(f"✅ Found in quality_reports collection")
            #     return {
            #         "upload_id": upload_id,
            #         "status": "analyzed",
            #         "filename": "unknown",
            #         "file_size": 0,
            #         "progress": 100.0,
            #     }
            raise HTTPException(status_code=404, detail="Upload not found")

        print(f"✅ Found upload: {upload_status.get('filename', 'unknown')}")
        print(f"📊 Status: {upload_status.get('status', 'unknown')}")
        print(f"📊 Progress: {upload_status.get('progress', 0)}")
        print(f"📊 Error: {upload_status.get('error', 'None')}")
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
        print(f"❌ Error getting upload status: {str(e)}")
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


@app.post("/upload/{upload_id}/replace", response_model=DataUploadResponse)
@handle_errors(ErrorType.FILE_PROCESSING, ErrorSeverity.MEDIUM)
async def replace_upload(upload_id: str, file: UploadFile = File(...)):
    """Replace an existing upload with a new file"""
    try:
        new_upload_id = await upload_manager.replace_upload(upload_id, file)

        # Get upload info
        upload_info = await upload_manager.get_upload_status(new_upload_id) or {}

        return DataUploadResponse(
            upload_id=new_upload_id,
            filename=file.filename if file.filename is not None else "uploaded_file",
            file_size=upload_info.get("file_size", 0),
            upload_time=upload_info.get("started_at", datetime.now()),
            status=upload_info.get("status", "uploading"),
        )
    except HTTPException:
        raise
    except Exception as e:
        safe_filename = file.filename if file.filename is not None else "uploaded_file"
        error_id = error_handler.handle_file_processing_error(e, safe_filename)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_id": error_id,
                "message": "Upload replacement failed. Please try again.",
            },
        )


@app.post("/analyze/{upload_id}", response_model=DataQualityResponse)
@handle_errors(ErrorType.FILE_PROCESSING, ErrorSeverity.MEDIUM)
async def analyze_data_quality(upload_id: str, background_tasks: BackgroundTasks):
    """Analyze data quality and detect issues with support for large files"""
    try:
        logger.info(f"🔍 Starting analysis for upload_id: {upload_id}")

        # Get upload data
        upload = await db.uploads.find_one({"upload_id": upload_id})
        if not upload:
            logger.error(f"❌ Upload not found: {upload_id}")
            raise HTTPException(status_code=404, detail="Upload not found")

        logger.info(f"✅ Found upload: {upload['filename']}")

        # Check file size to determine processing method
        file_size = upload.get("file_size", 0)
        file_path = upload["file_path"]

        # If file is large (>100MB), use chunked processing
        if file_size > 100 * 1024 * 1024:  # 100MB
            logger.info(
                f"📊 Large file detected ({file_size / (1024*1024):.2f}MB), using chunked processing"
            )

            # Use chunked processing for large files
            result = await chunked_processor.process_large_file(
                file_path,
                analyze_chunk_quality,
                progress_callback=None,  # Could add progress callback here
            )

            if not result["success"]:
                raise HTTPException(
                    status_code=500, detail=result.get("error", "Analysis failed")
                )

            # Create quality report from chunked results
            quality_report = DataQualityReport(
                upload_id=upload_id,
                quality_score=result["quality_score"],
                total_rows=result["total_rows_processed"],
                total_columns=0,  # Will be determined from first chunk
                issues=[],  # Will be populated from result["issues"]
                recommendations=result["recommendations"],
            )

            # Convert issues to DataIssue objects
            for issue_data in result["issues"]:
                from models import DataIssue, IssueType

                issue = DataIssue(
                    issue_type=IssueType(issue_data["issue_type"]),
                    column=issue_data["column"],
                    description=issue_data["description"],
                    affected_rows=issue_data["affected_rows"],
                    severity=issue_data["severity"],
                    suggested_fix=issue_data.get("suggested_fix"),
                    confidence=issue_data.get("confidence", 0.8),
                )
                quality_report.issues.append(issue)

        else:
            # Use regular processing for smaller files
            logger.info(f"📊 Loading data from: {file_path}")
            df = data_processor.load_data(file_path)
            logger.info(f"📊 Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

            logger.info("🔍 Running quality analysis...")
            quality_report = data_processor.analyze_quality(df)
            quality_report.upload_id = upload_id
            logger.info(
                f"✅ Analysis complete. Score: {quality_report.quality_score}, Issues: {len(quality_report.issues)}"
            )

        # Store analysis results
        logger.info("💾 Storing analysis results...")
        await db.quality_reports.insert_one(
            {
                "upload_id": upload_id,
                "report": quality_report.dict(),
                "created_at": datetime.now(),
            }
        )

        # Update upload status
        logger.info("📝 Updating upload status...")
        await db.uploads.update_one(
            {"upload_id": upload_id}, {"$set": {"status": "analyzed"}}
        )

        logger.info("✅ Analysis endpoint completed successfully")
        return DataQualityResponse(
            upload_id=upload_id,
            issues_found=[issue.dict() for issue in quality_report.issues],
            quality_score=quality_report.quality_score,
            recommendations=quality_report.recommendations,
        )

    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.handle_file_processing_error(e, upload_id)
        logger.error(f"❌ Error in analyze_data_quality: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_id": error_id,
                "message": "Analysis failed. Please try again.",
            },
        )


@app.post("/fix/{upload_id}", response_model=DataFixResponse)
async def fix_data_issues(upload_id: str):
    """Apply automated fixes to data issues"""
    try:
        # Get upload and quality report
        upload = await db.uploads.find_one({"upload_id": upload_id})
        quality_report = await db.quality_reports.find_one({"upload_id": upload_id})

        if not upload or not quality_report:
            raise HTTPException(status_code=404, detail="Upload or analysis not found")

        # Load original data
        df_original = data_processor.load_data(upload["file_path"])

        # Apply fixes
        df_fixed, fixes_applied = data_processor.apply_fixes(
            df_original, quality_report["report"]["issues"]
        )

        # Save cleaned data
        cleaned_file_path = f"cleaned/{upload_id}_cleaned.csv"
        os.makedirs("cleaned", exist_ok=True)
        df_fixed.to_csv(cleaned_file_path, index=False)

        # Generate before/after comparison
        comparison = data_processor.generate_comparison(df_original, df_fixed)

        # Store fix results
        await db.data_fixes.insert_one(
            {
                "upload_id": upload_id,
                "fixes_applied": [fix.dict() for fix in fixes_applied],
                "cleaned_data_path": cleaned_file_path,
                "comparison": comparison,
                "created_at": datetime.now(),
            }
        )

        # Update upload status
        await db.uploads.update_one(
            {"upload_id": upload_id}, {"$set": {"status": "fixed"}}
        )

        return DataFixResponse(
            upload_id=upload_id,
            fixes_applied=fixes_applied,
            cleaned_data_url=f"/download/{upload_id}",
            before_after_comparison=comparison,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{upload_id}")
async def download_cleaned_data(upload_id: str):
    """Download cleaned dataset"""
    try:
        fix_record = await db.data_fixes.find_one({"upload_id": upload_id})
        if not fix_record:
            raise HTTPException(status_code=404, detail="Cleaned data not found")

        file_path = fix_record["cleaned_data_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        from fastapi.responses import FileResponse

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
        # Get the upload record
        upload = await db.uploads.find_one({"upload_id": upload_id})
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")

        file_path = upload["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Original file not found")

        from fastapi.responses import FileResponse

        return FileResponse(
            path=file_path,
            filename=upload["filename"],
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
@handle_errors(ErrorType.AI_SERVICE, ErrorSeverity.MEDIUM)
async def chat_with_ai(upload_id: str, message: ConversationMessage):
    """Chat with AI about data issues and fixes"""
    try:
        logger.info(f"Chat request for upload_id: {upload_id}")

        # Get context about the upload
        upload = await db.uploads.find_one({"upload_id": upload_id})
        quality_report = await db.quality_reports.find_one({"upload_id": upload_id})
        fix_record = await db.data_fixes.find_one({"upload_id": upload_id})

        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")

        # Generate AI response
        logger.info("Generating AI response...")
        ai_response = await ai_service.generate_response(
            message.content, upload, quality_report, fix_record
        )

        # Store conversation
        conversation_entry = {
            "upload_id": upload_id,
            "user_message": message.content,
            "ai_response": ai_response,
            "timestamp": datetime.now(),
        }
        await db.conversations.insert_one(conversation_entry)

        logger.info("Chat response generated successfully")
        return {"response": ai_response}

    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.handle_ai_service_error(e, "chat")
        logger.error(f"Chat error: {str(e)}")
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
    """Get chat history for a specific upload"""
    try:
        conversations = []
        async for conv in db.conversations.find({"upload_id": upload_id}).sort(
            "timestamp", 1
        ):
            conv["_id"] = str(conv["_id"])
            conversations.append(conv)

        return {"conversations": conversations}
    except Exception as e:
        error_id = error_handler.log_error(
            e, {"upload_id": upload_id}, ErrorSeverity.LOW
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get chat history: {str(e)}"
        )


@app.get("/history")
async def get_upload_history():
    """Get list of all uploads and their status with download information"""
    try:
        uploads = []
        async for upload in db.uploads.find().sort("upload_time", -1):
            upload["_id"] = str(upload["_id"])

            # Only include successfully uploaded files in history
            if upload.get("status") in ["uploaded", "analyzed", "fixed"]:
                # Get quality report if available
                quality_report = await db.quality_reports.find_one(
                    {"upload_id": upload["upload_id"]}
                )
                if quality_report:
                    upload["quality_score"] = quality_report.get("report", {}).get(
                        "quality_score", 0
                    )
                    upload["issues_count"] = len(
                        quality_report.get("report", {}).get("issues", [])
                    )

                # Get fix record if available
                fix_record = await db.data_fixes.find_one(
                    {"upload_id": upload["upload_id"]}
                )
                if fix_record:
                    upload["has_cleaned_data"] = True
                    upload["cleaned_data_path"] = fix_record.get("cleaned_data_path")
                    upload["fixes_applied"] = fix_record.get("fixes_applied", [])
                else:
                    upload["has_cleaned_data"] = False

                uploads.append(upload)

        return {"uploads": uploads}
    except Exception as e:
        error_id = error_handler.log_error(e, {}, ErrorSeverity.LOW)
        raise HTTPException(
            status_code=500, detail=f"Failed to get upload history: {str(e)}"
        )


@app.get("/lineage/{upload_id}")
async def get_data_lineage(upload_id: str):
    """Get data lineage and transformation history"""
    try:
        lineage = []

        # Get upload info
        upload = await db.uploads.find_one({"upload_id": upload_id})
        if upload:
            lineage.append(
                {
                    "step": "upload",
                    "timestamp": upload["upload_time"],
                    "description": f"Uploaded {upload['filename']}",
                    "data_shape": "Original data",
                }
            )

        # Get quality analysis
        quality_report = await db.quality_reports.find_one({"upload_id": upload_id})
        if quality_report:
            lineage.append(
                {
                    "step": "analysis",
                    "timestamp": quality_report["created_at"],
                    "description": f"Quality analysis completed - Score: {quality_report['report']['quality_score']}",
                    "issues_found": len(quality_report["report"]["issues"]),
                }
            )

        # Get fixes applied
        fix_record = await db.data_fixes.find_one({"upload_id": upload_id})
        if fix_record:
            lineage.append(
                {
                    "step": "fixes",
                    "timestamp": fix_record["created_at"],
                    "description": f"Applied {len(fix_record['fixes_applied'])} fixes",
                    "fixes": fix_record["fixes_applied"],
                }
            )

        return {"lineage": lineage}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/errors/summary")
async def get_error_summary(hours: int = 24):
    """Get error summary for monitoring"""
    try:
        summary = error_handler.get_error_summary(hours)
        return summary
    except Exception as e:
        logger.error(f"Failed to get error summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get error summary")


@app.post("/errors/{error_id}/resolve")
async def resolve_error(error_id: str):
    """Mark an error as resolved"""
    try:
        success = error_handler.mark_error_resolved(error_id)
        if not success:
            raise HTTPException(status_code=404, detail="Error not found")
        return {"message": "Error marked as resolved", "error_id": error_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resolve error")


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
    for upload_id in list(upload_manager.active_uploads.keys()):
        await upload_manager.cancel_upload(upload_id)

    logger.info("✅ Data Doctor API shutdown completed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
