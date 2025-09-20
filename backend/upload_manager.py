import asyncio
import os
import uuid
from typing import Dict, Optional, Callable, Any
from datetime import datetime
import aiofiles
from fastapi import UploadFile, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class UploadManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.active_uploads: Dict[str, Dict[str, Any]] = {}
        self.chunk_size = 1024 * 1024  # 1MB chunks
        self.max_file_size = 1024 * 1024 * 1024  # 1GB max
    
    async def start_upload(
        self, 
        file: UploadFile, 
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Start a new upload with progress tracking"""
        upload_id = str(uuid.uuid4())
        
        # Validate file size
        if file.size and file.size > self.max_file_size:
            file_size_mb = file.size / (1024 * 1024)
            max_size_mb = self.max_file_size / (1024 * 1024)
            raise HTTPException(
                status_code=413, 
                detail=f"File too large: {file_size_mb:.2f}MB. Maximum size is {max_size_mb:.0f}MB. Please split your data into smaller files or contact support for assistance with larger datasets."
            )
        
        # Create upload record
        upload_info = {
            "upload_id": upload_id,
            "filename": file.filename,
            "file_size": file.size or 0,
            "status": "uploading",
            "progress": 0,
            "started_at": datetime.now(),
            "chunks": [],
            "cancelled": False,
            "error": None
        }
        
        self.active_uploads[upload_id] = upload_info
        
        try:
            # Create temp directory
            temp_dir = f"temp/{upload_id}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Store upload metadata in database
            await self.db.uploads.insert_one({
                "upload_id": upload_id,
                "filename": file.filename,
                "file_size": file.size or 0,
                "upload_time": datetime.now(),
                "file_path": f"{temp_dir}/{file.filename}",
                "status": "uploading",
                "progress": 0
            })
            
            # Start upload task
            asyncio.create_task(
                self._upload_file(upload_id, file, temp_dir, progress_callback)
            )
            
            return upload_id
            
        except Exception as e:
            # Clean up on error
            self.active_uploads.pop(upload_id, None)
            logger.error(f"Upload start failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    async def _upload_file(
        self, 
        upload_id: str, 
        file: UploadFile, 
        temp_dir: str,
        progress_callback: Optional[Callable] = None
    ):
        """Upload file in chunks with progress tracking"""
        try:
            file_path = f"{temp_dir}/{file.filename}"
            total_size = file.size or 0
            uploaded_size = 0
            
            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    # Check if upload was cancelled
                    if self.active_uploads.get(upload_id, {}).get("cancelled", False):
                        await self._cleanup_upload(upload_id, temp_dir)
                        return
                    
                    # Read chunk
                    chunk = await file.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    # Write chunk
                    await f.write(chunk)
                    uploaded_size += len(chunk)
                    
                    # Update progress
                    progress = (uploaded_size / total_size * 100) if total_size > 0 else 100
                    self.active_uploads[upload_id]["progress"] = progress
                    
                    # Update database
                    await self.db.uploads.update_one(
                        {"upload_id": upload_id},
                        {"$set": {"progress": progress}}
                    )
                    
                    # Call progress callback if provided
                    if progress_callback:
                        await progress_callback(upload_id, progress)
                    
                    # Small delay to prevent overwhelming the system
                    await asyncio.sleep(0.01)
            
            # Mark upload as complete
            self.active_uploads[upload_id]["status"] = "completed"
            await self.db.uploads.update_one(
                {"upload_id": upload_id},
                {"$set": {"status": "uploaded", "progress": 100}}
            )
            
            logger.info(f"Upload completed: {upload_id}")
            
        except Exception as e:
            # Handle upload error
            self.active_uploads[upload_id]["status"] = "error"
            self.active_uploads[upload_id]["error"] = str(e)
            
            await self.db.uploads.update_one(
                {"upload_id": upload_id},
                {"$set": {"status": "error", "error": str(e)}}
            )
            
            logger.error(f"Upload failed: {upload_id} - {str(e)}")
            
            # Clean up
            await self._cleanup_upload(upload_id, temp_dir)
    
    async def cancel_upload(self, upload_id: str) -> bool:
        """Cancel an ongoing upload"""
        if upload_id not in self.active_uploads:
            return False
        
        upload_info = self.active_uploads[upload_id]
        if upload_info["status"] in ["completed", "error"]:
            return False
        
        # Mark as cancelled
        upload_info["cancelled"] = True
        upload_info["status"] = "cancelled"
        
        # Update database
        await self.db.uploads.update_one(
            {"upload_id": upload_id},
            {"$set": {"status": "cancelled"}}
        )
        
        # Clean up files
        temp_dir = f"temp/{upload_id}"
        await self._cleanup_upload(upload_id, temp_dir)
        
        logger.info(f"Upload cancelled: {upload_id}")
        return True
    
    async def replace_upload(
        self, 
        upload_id: str, 
        new_file: UploadFile,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Replace an existing upload with a new file"""
        # Cancel existing upload if it's still active
        if upload_id in self.active_uploads:
            await self.cancel_upload(upload_id)
        
        # Start new upload with same ID
        return await self.start_upload(new_file, progress_callback)
    
    async def get_upload_status(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Get current upload status"""
        if upload_id in self.active_uploads:
            return self.active_uploads[upload_id]
        
        # Check database for completed uploads
        upload = await self.db.uploads.find_one({"upload_id": upload_id})
        if upload:
            return {
                "upload_id": upload_id,
                "filename": upload["filename"],
                "file_size": upload["file_size"],
                "status": upload["status"],
                "progress": upload.get("progress", 100),
                "started_at": upload["upload_time"],
                "error": upload.get("error")
            }
        
        return None
    
    async def _cleanup_upload(self, upload_id: str, temp_dir: str):
        """Clean up upload files and remove from active uploads"""
        try:
            # Remove files
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
            
            # Remove from active uploads
            self.active_uploads.pop(upload_id, None)
            
        except Exception as e:
            logger.error(f"Cleanup failed for {upload_id}: {str(e)}")
    
    async def cleanup_old_uploads(self, max_age_hours: int = 24):
        """Clean up old upload files"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        old_uploads = await self.db.uploads.find({
            "upload_time": {"$lt": cutoff_time}
        }).to_list(length=None)
        
        for upload in old_uploads:
            upload_id = upload["upload_id"]
            temp_dir = f"temp/{upload_id}"
            await self._cleanup_upload(upload_id, temp_dir)
            
            # Remove from database
            await self.db.uploads.delete_one({"upload_id": upload_id})
        
        logger.info(f"Cleaned up {len(old_uploads)} old uploads")
