import pandas as pd
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class FileValidator:
    """Comprehensive file validation with detailed error reporting"""
    
    def __init__(self):
        self.supported_formats = {
            'csv': ['text/csv', 'application/csv'],
            'excel': [
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel'
            ],
            'json': ['application/json', 'text/json']
        }
        
        self.max_file_size = 1024 * 1024 * 1024  # 1GB
        self.min_rows = 1
        self.max_columns = 1000
        self.required_headers = ['Name', 'Email']  # Example required headers
    
    async def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """Comprehensive file validation with detailed error reporting"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'file_info': {},
            'suggestions': []
        }
        
        try:
            # Basic file validation
            await self._validate_basic_properties(file, validation_result)
            
            if not validation_result['is_valid']:
                return validation_result
            
            # Content validation
            await self._validate_file_content(file, validation_result)
            
            # Schema validation
            await self._validate_schema(file, validation_result)
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            validation_result['is_valid'] = False
            validation_result['errors'].append({
                'type': 'validation_error',
                'message': 'An unexpected error occurred during validation',
                'details': str(e),
                'suggestion': 'Please try uploading the file again or contact support if the issue persists'
            })
        
        return validation_result
    
    async def _validate_basic_properties(self, file: UploadFile, result: Dict[str, Any]):
        """Validate basic file properties"""
        
        # Check file size
        if file.size and file.size > self.max_file_size:
            result['is_valid'] = False
            result['errors'].append({
                'type': 'file_too_large',
                'message': f'File size exceeds the maximum limit of 1GB',
                'details': f'Your file is {file.size / (1024*1024*1024):.2f}GB, but the maximum allowed size is 1GB',
                'suggestion': 'Please split your data into smaller files or compress the file to reduce its size'
            })
        
        # Check file format
        if not self._is_supported_format(file):
            result['is_valid'] = False
            result['errors'].append({
                'type': 'unsupported_format',
                'message': f'Unsupported file format: {file.content_type}',
                'details': f'The file "{file.filename}" is not in a supported format',
                'suggestion': 'Please upload a CSV, Excel (.xlsx, .xls), or JSON file'
            })
        
        # Check filename
        if not file.filename or file.filename.strip() == '':
            result['warnings'].append({
                'type': 'missing_filename',
                'message': 'File has no name',
                'suggestion': 'Consider renaming your file to something descriptive'
            })
        
        result['file_info'] = {
            'filename': file.filename,
            'size': file.size,
            'content_type': file.content_type
        }
    
    def _is_supported_format(self, file: UploadFile) -> bool:
        """Check if file format is supported"""
        if not file.content_type:
            return False
        
        for format_type, mime_types in self.supported_formats.items():
            if file.content_type in mime_types:
                return True
        
        # Check by file extension as fallback
        if file.filename:
            ext = file.filename.lower().split('.')[-1]
            if ext in ['csv', 'xlsx', 'xls', 'json']:
                return True
        
        return False
    
    async def _validate_file_content(self, file: UploadFile, result: Dict[str, Any]):
        """Validate file content structure"""
        try:
            # Read file content based on type
            content = await file.read()
            file.file.seek(0)  # Reset file pointer
            
            if file.content_type in self.supported_formats['csv']:
                await self._validate_csv_content(content, result)
            elif file.content_type in self.supported_formats['excel']:
                await self._validate_excel_content(content, result)
            elif file.content_type in self.supported_formats['json']:
                await self._validate_json_content(content, result)
                
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append({
                'type': 'content_read_error',
                'message': 'Unable to read file content',
                'details': f'Error reading file: {str(e)}',
                'suggestion': 'Please ensure the file is not corrupted and try again'
            })
    
    async def _validate_csv_content(self, content: bytes, result: Dict[str, Any]):
        """Validate CSV content"""
        try:
            # Try to read CSV
            df = pd.read_csv(io.BytesIO(content), nrows=5)  # Read first 5 rows for validation
            
            # Check if file is empty
            if df.empty:
                result['is_valid'] = False
                result['errors'].append({
                    'type': 'empty_file',
                    'message': 'The CSV file is empty',
                    'details': 'No data rows found in the file',
                    'suggestion': 'Please ensure your CSV file contains data rows'
                })
                return
            
            # Check for headers
            if df.columns.tolist() == [f'Unnamed: {i}' for i in range(len(df.columns))]:
                result['warnings'].append({
                    'type': 'missing_headers',
                    'message': 'No column headers detected',
                    'details': 'The first row should contain column names',
                    'suggestion': 'Add a header row with descriptive column names like "Name", "Email", "Date"'
                })
            
            # Check for minimum rows
            if len(df) < self.min_rows:
                result['warnings'].append({
                    'type': 'insufficient_data',
                    'message': f'Very few data rows ({len(df)} rows)',
                    'suggestion': 'Consider adding more data for meaningful analysis'
                })
            
            # Check for too many columns
            if len(df.columns) > self.max_columns:
                result['is_valid'] = False
                result['errors'].append({
                    'type': 'too_many_columns',
                    'message': f'Too many columns ({len(df.columns)} columns)',
                    'details': f'The file has {len(df.columns)} columns, but the maximum allowed is {self.max_columns}',
                    'suggestion': 'Consider splitting your data into multiple files or removing unnecessary columns'
                })
            
            result['file_info'].update({
                'rows': len(df),
                'columns': len(df.columns),
                'headers': df.columns.tolist()
            })
            
        except pd.errors.EmptyDataError:
            result['is_valid'] = False
            result['errors'].append({
                'type': 'empty_csv',
                'message': 'The CSV file appears to be empty or corrupted',
                'suggestion': 'Please check your file and ensure it contains valid CSV data'
            })
        except pd.errors.ParserError as e:
            result['is_valid'] = False
            result['errors'].append({
                'type': 'csv_parse_error',
                'message': 'Unable to parse CSV file',
                'details': f'CSV parsing error: {str(e)}',
                'suggestion': 'Please ensure your CSV file is properly formatted with consistent delimiters'
            })
    
    async def _validate_excel_content(self, content: bytes, result: Dict[str, Any]):
        """Validate Excel content"""
        try:
            # Try to read Excel
            df = pd.read_excel(io.BytesIO(content), nrows=5)
            
            if df.empty:
                result['is_valid'] = False
                result['errors'].append({
                    'type': 'empty_excel',
                    'message': 'The Excel file is empty',
                    'details': 'No data found in the first worksheet',
                    'suggestion': 'Please ensure your Excel file contains data in the first worksheet'
                })
                return
            
            # Check for headers
            if df.columns.tolist() == [f'Unnamed: {i}' for i in range(len(df.columns))]:
                result['warnings'].append({
                    'type': 'missing_headers',
                    'message': 'No column headers detected in Excel file',
                    'details': 'The first row should contain column names',
                    'suggestion': 'Add a header row with descriptive column names'
                })
            
            result['file_info'].update({
                'rows': len(df),
                'columns': len(df.columns),
                'headers': df.columns.tolist()
            })
            
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append({
                'type': 'excel_read_error',
                'message': 'Unable to read Excel file',
                'details': f'Excel reading error: {str(e)}',
                'suggestion': 'Please ensure your Excel file is not corrupted and is in .xlsx or .xls format'
            })
    
    async def _validate_json_content(self, content: bytes, result: Dict[str, Any]):
        """Validate JSON content"""
        try:
            # Try to parse JSON
            data = json.loads(content.decode('utf-8'))
            
            if not data:
                result['is_valid'] = False
                result['errors'].append({
                    'type': 'empty_json',
                    'message': 'The JSON file is empty',
                    'suggestion': 'Please ensure your JSON file contains data'
                })
                return
            
            # Check if it's an array of objects (tabular data)
            if isinstance(data, list):
                if len(data) == 0:
                    result['is_valid'] = False
                    result['errors'].append({
                        'type': 'empty_json_array',
                        'message': 'The JSON array is empty',
                        'suggestion': 'Please add data objects to your JSON array'
                    })
                    return
                
                # Check first object for structure
                if isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    result['file_info'].update({
                        'rows': len(data),
                        'columns': len(headers),
                        'headers': headers
                    })
                else:
                    result['warnings'].append({
                        'type': 'json_structure',
                        'message': 'JSON array contains non-object elements',
                        'suggestion': 'For best results, use an array of objects where each object represents a row'
                    })
            else:
                result['warnings'].append({
                    'type': 'json_format',
                    'message': 'JSON is not in array format',
                    'suggestion': 'For tabular data, consider using an array of objects'
                })
            
        except json.JSONDecodeError as e:
            result['is_valid'] = False
            result['errors'].append({
                'type': 'json_parse_error',
                'message': 'Invalid JSON format',
                'details': f'JSON parsing error: {str(e)}',
                'suggestion': 'Please ensure your JSON file is properly formatted'
            })
        except UnicodeDecodeError:
            result['is_valid'] = False
            result['errors'].append({
                'type': 'encoding_error',
                'message': 'File encoding error',
                'details': 'Unable to decode the file as UTF-8',
                'suggestion': 'Please save your file with UTF-8 encoding'
            })
    
    async def _validate_schema(self, file: UploadFile, result: Dict[str, Any]):
        """Validate data schema and structure"""
        if not result['file_info'].get('headers'):
            return
        
        headers = result['file_info']['headers']
        
        # Check for required headers (example)
        missing_required = []
        for required in self.required_headers:
            if required not in headers:
                missing_required.append(required)
        
        if missing_required:
            result['warnings'].append({
                'type': 'missing_required_headers',
                'message': f'Missing recommended headers: {", ".join(missing_required)}',
                'details': f'The file is missing these recommended columns: {", ".join(missing_required)}',
                'suggestion': f'Consider adding columns named: {", ".join(missing_required)}'
            })
        
        # Check for duplicate headers
        if len(headers) != len(set(headers)):
            duplicates = [h for h in headers if headers.count(h) > 1]
            result['warnings'].append({
                'type': 'duplicate_headers',
                'message': f'Duplicate column names found: {", ".join(set(duplicates))}',
                'suggestion': 'Please rename duplicate columns to make them unique'
            })
        
        # Check for empty header names
        empty_headers = [i for i, h in enumerate(headers) if not h or h.strip() == '']
        if empty_headers:
            result['warnings'].append({
                'type': 'empty_headers',
                'message': f'Empty column names found in columns: {", ".join(map(str, empty_headers))}',
                'suggestion': 'Please provide names for all columns'
            })

# Import io for BytesIO
import io
