import asyncio
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional, Callable
from datetime import datetime
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp
from functools import partial

logger = logging.getLogger(__name__)


class ChunkedProcessor:
    def __init__(self, chunk_size: int = 10000, max_workers: int = None):  # type: ignore
        self.chunk_size = chunk_size
        self.max_workers = max_workers or min(mp.cpu_count(), 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    async def process_large_file(
        self,
        file_path: str,
        processing_func: Callable,
        progress_callback: Optional[Callable] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Process a large file in chunks with parallel execution"""
        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            total_rows = self._count_rows(file_path)

            logger.info(
                f"Processing large file: {file_path} ({file_size / (1024*1024):.2f}MB, {total_rows} rows)"
            )

            # Calculate number of chunks
            num_chunks = (total_rows + self.chunk_size - 1) // self.chunk_size

            # Process chunks in parallel
            chunk_results = []
            completed_chunks = 0

            # Create chunk processing tasks
            tasks = []
            for chunk_idx in range(num_chunks):
                start_row = chunk_idx * self.chunk_size
                end_row = min((chunk_idx + 1) * self.chunk_size, total_rows)

                task = asyncio.create_task(
                    self._process_chunk(
                        file_path,
                        start_row,
                        end_row,
                        chunk_idx,
                        processing_func,
                        **kwargs,
                    )
                )
                tasks.append(task)

            # Process chunks with progress tracking
            for task in asyncio.as_completed(tasks):
                try:
                    chunk_result = await task
                    chunk_results.append(chunk_result)
                    completed_chunks += 1

                    # Update progress
                    progress = (completed_chunks / num_chunks) * 100
                    if progress_callback:
                        await progress_callback(progress, completed_chunks, num_chunks)

                    logger.info(
                        f"Completed chunk {completed_chunks}/{num_chunks} ({progress:.1f}%)"
                    )

                except Exception as e:
                    logger.error(f"Chunk processing failed: {str(e)}")
                    raise e

            # Combine results
            combined_result = self._combine_chunk_results(chunk_results)

            logger.info(f"File processing completed: {file_path}")
            return combined_result

        except Exception as e:
            logger.error(f"Large file processing failed: {str(e)}")
            raise e

    async def _process_chunk(
        self,
        file_path: str,
        start_row: int,
        end_row: int,
        chunk_idx: int,
        processing_func: Callable,
        **kwargs,
    ) -> Dict[str, Any]:
        """Process a single chunk of data"""
        try:
            # Read chunk
            chunk_df = self._read_chunk(file_path, start_row, end_row)

            if chunk_df.empty:
                return {
                    "chunk_idx": chunk_idx,
                    "start_row": start_row,
                    "end_row": end_row,
                    "rows_processed": 0,
                    "result": None,
                    "issues": [],
                    "processing_time": 0,
                }

            # Process chunk
            start_time = datetime.now()

            # Run processing function in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, partial(processing_func, chunk_df, **kwargs)
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "chunk_idx": chunk_idx,
                "start_row": start_row,
                "end_row": end_row,
                "rows_processed": len(chunk_df),
                "result": result,
                "issues": result.get("issues", []) if isinstance(result, dict) else [],
                "processing_time": processing_time,
            }

        except Exception as e:
            logger.error(f"Chunk {chunk_idx} processing failed: {str(e)}")
            return {
                "chunk_idx": chunk_idx,
                "start_row": start_row,
                "end_row": end_row,
                "rows_processed": 0,
                "result": None,
                "issues": [],
                "processing_time": 0,
                "error": str(e),
            }

    def _read_chunk(self, file_path: str, start_row: int, end_row: int) -> pd.DataFrame:
        """Read a chunk of data from file"""
        try:
            if file_path.endswith(".csv"):
                return pd.read_csv(
                    file_path, skiprows=start_row, nrows=end_row - start_row
                )
            elif file_path.endswith((".xlsx", ".xls")):
                return pd.read_excel(
                    file_path, skiprows=start_row, nrows=end_row - start_row
                )
            elif file_path.endswith(".json"):
                # For JSON, we need to read the entire file and slice
                # This is not optimal for very large JSON files
                df = pd.read_json(file_path)
                # Ensure DataFrame is returned even if a Series is produced
                return pd.DataFrame(df.iloc[start_row:end_row])
            else:
                raise ValueError(f"Unsupported file format: {file_path}")

        except Exception as e:
            logger.error(f"Failed to read chunk {start_row}-{end_row}: {str(e)}")
            return pd.DataFrame()

    def _count_rows(self, file_path: str) -> int:
        """Count total rows in file efficiently"""
        try:
            if file_path.endswith(".csv"):
                # Use wc command for efficiency on large files
                import subprocess

                result = subprocess.run(
                    ["wc", "-l", file_path], capture_output=True, text=True
                )
                if result.returncode == 0:
                    return int(result.stdout.split()[0]) - 1  # Subtract header
                else:
                    # Fallback to pandas
                    return len(pd.read_csv(file_path))
            elif file_path.endswith((".xlsx", ".xls")):
                # For Excel, we need to read to count rows
                return len(pd.read_excel(file_path))
            elif file_path.endswith(".json"):
                return len(pd.read_json(file_path))
            else:
                raise ValueError(f"Unsupported file format: {file_path}")

        except Exception as e:
            logger.error(f"Failed to count rows: {str(e)}")
            # Fallback to reading the file
            try:
                if file_path.endswith(".csv"):
                    return len(pd.read_csv(file_path))
                elif file_path.endswith((".xlsx", ".xls")):
                    return len(pd.read_excel(file_path))
                elif file_path.endswith(".json"):
                    return len(pd.read_json(file_path))
                else:
                    # Unsupported file types fallback
                    return 0
            except Exception:
                return 0

    def _combine_chunk_results(
        self, chunk_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine results from all chunks"""
        try:
            # Filter out failed chunks
            successful_chunks = [
                r for r in chunk_results if r.get("result") is not None
            ]
            failed_chunks = [r for r in chunk_results if r.get("result") is None]

            if not successful_chunks:
                return {
                    "success": False,
                    "error": "All chunks failed to process",
                    "failed_chunks": len(failed_chunks),
                    "total_chunks": len(chunk_results),
                }

            # Combine issues from all chunks
            all_issues = []
            total_rows_processed = 0
            total_processing_time = 0

            for chunk_result in successful_chunks:
                all_issues.extend(chunk_result.get("issues", []))
                total_rows_processed += chunk_result.get("rows_processed", 0)
                total_processing_time += chunk_result.get("processing_time", 0)

            # Calculate overall quality score
            quality_score = self._calculate_quality_score(
                all_issues, total_rows_processed
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(all_issues)

            return {
                "success": True,
                "total_rows_processed": total_rows_processed,
                "total_chunks": len(chunk_results),
                "successful_chunks": len(successful_chunks),
                "failed_chunks": len(failed_chunks),
                "issues": all_issues,
                "quality_score": quality_score,
                "recommendations": recommendations,
                "total_processing_time": total_processing_time,
                "average_chunk_time": (
                    total_processing_time / len(successful_chunks)
                    if successful_chunks
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Failed to combine chunk results: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_chunks": len(chunk_results),
            }

    def _calculate_quality_score(
        self, issues: List[Dict[str, Any]], total_rows: int
    ) -> float:
        """Calculate overall quality score from chunk issues"""
        if not issues or total_rows == 0:
            return 1.0

        # Weight issues by severity
        severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}

        total_penalty = 0
        for issue in issues:
            penalty = severity_weights.get(issue.get("severity", "medium"), 0.3)
            # Adjust penalty based on affected rows percentage
            affected_rows = len(issue.get("affected_rows", []))
            if affected_rows > 0:
                affected_percentage = affected_rows / total_rows
                penalty *= affected_percentage
            total_penalty += penalty

        # Normalize penalty
        max_possible_penalty = len(issues) * 1.0
        normalized_penalty = min(total_penalty / max_possible_penalty, 1.0)

        return max(0.0, 1.0 - normalized_penalty)

    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on detected issues"""
        recommendations = []

        # Count issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue.get("issue_type", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        # Generate specific recommendations
        if "missing_values" in issue_types:
            recommendations.append(
                f"Address {issue_types['missing_values']} missing value issues across chunks"
            )

        if "duplicates" in issue_types:
            recommendations.append("Remove duplicate rows to ensure data uniqueness")

        if "format_errors" in issue_types:
            recommendations.append("Standardize date and text formats across columns")

        if "outliers" in issue_types:
            recommendations.append("Review and validate outlier values for accuracy")

        # General recommendations
        recommendations.append(
            "Consider implementing data validation rules for future uploads"
        )
        recommendations.append("Document data quality standards and expected formats")

        return recommendations

    async def cleanup(self):
        """Clean up resources"""
        self.executor.shutdown(wait=True)
        logger.info("ChunkedProcessor cleanup completed")


# Memory-efficient data processing functions
def analyze_chunk_quality(chunk_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data quality for a single chunk"""
    from data_processor import DataProcessor

    processor = DataProcessor()
    quality_report = processor.analyze_quality(chunk_df)

    return {
        "issues": [issue.dict() for issue in quality_report.issues],
        "quality_score": quality_report.quality_score,
        "total_rows": quality_report.total_rows,
        "total_columns": quality_report.total_columns,
    }


def apply_chunk_fixes(
    chunk_df: pd.DataFrame, issues: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Apply fixes to a single chunk"""
    from data_processor import DataProcessor

    processor = DataProcessor()
    df_fixed, fixes_applied = processor.apply_fixes(chunk_df, issues)

    return {
        "fixed_df": df_fixed,
        "fixes_applied": [fix.dict() for fix in fixes_applied],
        "comparison": processor.generate_comparison(chunk_df, df_fixed),
    }
