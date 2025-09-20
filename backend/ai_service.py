import openai
import os
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

class AIService:
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
        )
        self.model = "gpt-3.5-turbo"
    
    async def generate_response(self, user_message: str, upload_data: Optional[Dict], 
                              quality_report: Optional[Dict], fix_record: Optional[Dict]) -> str:
        """Generate AI response based on user message and data context"""
        
        # Build context from available data
        context = self._build_context(upload_data, quality_report, fix_record)
        
        # Create system prompt
        system_prompt = self._create_system_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    def _build_context(self, upload_data: Optional[Dict], quality_report: Optional[Dict], 
                      fix_record: Optional[Dict]) -> str:
        """Build context string from available data"""
        context_parts = []
        
        if upload_data:
            context_parts.append(f"Dataset: {upload_data.get('filename', 'Unknown')}")
            context_parts.append(f"File size: {upload_data.get('file_size', 0)} bytes")
            context_parts.append(f"Upload time: {upload_data.get('upload_time', 'Unknown')}")
            context_parts.append(f"Status: {upload_data.get('status', 'Unknown')}")
        
        if quality_report and 'report' in quality_report:
            report = quality_report['report']
            context_parts.append(f"Data Quality Score: {report.get('quality_score', 0):.2f}")
            context_parts.append(f"Total rows: {report.get('total_rows', 0)}")
            context_parts.append(f"Total columns: {report.get('total_columns', 0)}")
            
            issues = report.get('issues', [])
            if issues:
                context_parts.append(f"Issues found: {len(issues)}")
                for issue in issues[:5]:  # Show first 5 issues
                    context_parts.append(f"- {issue.get('issue_type', 'Unknown')}: {issue.get('description', 'No description')}")
        
        if fix_record:
            fixes = fix_record.get('fixes_applied', [])
            if fixes:
                context_parts.append(f"Fixes applied: {len(fixes)}")
                for fix in fixes[:3]:  # Show first 3 fixes
                    context_parts.append(f"- {fix.get('fix_type', 'Unknown')}: {fix.get('description', 'No description')}")
        
        return "\n".join(context_parts) if context_parts else "No data context available"
    
    def _create_system_prompt(self, context: str) -> str:
        """Create system prompt for the AI assistant"""
        return f"""You are the Data Doctor AI Assistant, an expert in data quality, cleaning, and analysis. 
You help users understand their data issues, explain fixes that have been applied, and provide insights about data quality.

Current data context:
{context}

Guidelines for your responses:
1. Be conversational and helpful, like a data expert colleague
2. Explain technical concepts in simple terms
3. When discussing data issues, be specific about what was found and why it matters
4. For fixes applied, explain what was done and any uncertainties
5. Provide actionable insights and recommendations
6. If asked about specific issues, refer to the context provided
7. Always be honest about limitations and uncertainties in automated fixes
8. Suggest next steps for data quality improvement

Remember: You're helping users make better decisions with their data, so be clear, accurate, and supportive."""
    
    async def generate_data_insights(self, df_summary: Dict[str, Any]) -> List[str]:
        """Generate insights about the dataset"""
        insights = []
        
        # Basic insights
        if df_summary.get('total_rows', 0) > 10000:
            insights.append("Large dataset detected - consider sampling for initial analysis")
        
        if df_summary.get('missing_percentage', 0) > 20:
            insights.append("High missing data percentage - investigate data collection process")
        
        if df_summary.get('duplicate_percentage', 0) > 5:
            insights.append("Significant duplicate data - review data ingestion pipeline")
        
        # Column-specific insights
        numeric_columns = df_summary.get('numeric_columns', 0)
        categorical_columns = df_summary.get('categorical_columns', 0)
        
        if numeric_columns > categorical_columns:
            insights.append("Dataset is primarily numerical - suitable for statistical analysis")
        elif categorical_columns > numeric_columns:
            insights.append("Dataset is primarily categorical - consider encoding for ML applications")
        
        return insights
    
    async def explain_anomaly(self, column: str, value: Any, context: Dict[str, Any]) -> str:
        """Explain why a value might be an anomaly"""
        try:
            prompt = f"""Explain why this value might be an anomaly in the context of the dataset:

Column: {column}
Value: {value}
Context: {json.dumps(context, indent=2)}

Provide a brief, clear explanation of why this value stands out and what it might indicate."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analysis expert explaining statistical anomalies."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Unable to analyze this anomaly: {str(e)}"
    
    async def suggest_data_improvements(self, quality_report: Dict[str, Any]) -> List[str]:
        """Suggest improvements based on quality report"""
        suggestions = []
        
        issues = quality_report.get('issues', [])
        quality_score = quality_report.get('quality_score', 0)
        
        if quality_score < 0.7:
            suggestions.append("Consider implementing data validation rules at the source")
            suggestions.append("Review data collection processes for consistency")
        
        # Issue-specific suggestions
        issue_types = [issue.get('issue_type') for issue in issues]
        
        if 'missing_values' in issue_types:
            suggestions.append("Implement required field validation in data entry forms")
            suggestions.append("Consider data imputation strategies for missing values")
        
        if 'duplicates' in issue_types:
            suggestions.append("Add unique constraints to prevent duplicate entries")
            suggestions.append("Implement deduplication in data pipeline")
        
        if 'format_errors' in issue_types:
            suggestions.append("Standardize data entry formats with input validation")
            suggestions.append("Use dropdown menus for categorical data")
        
        if 'outliers' in issue_types:
            suggestions.append("Implement range validation for numerical fields")
            suggestions.append("Add data review process for extreme values")
        
        return suggestions
    
    async def generate_data_documentation(self, df_summary: Dict[str, Any]) -> str:
        """Generate documentation for the dataset"""
        try:
            prompt = f"""Generate a brief data documentation summary for this dataset:

{json.dumps(df_summary, indent=2)}

Include:
1. Dataset overview
2. Key columns and their purposes
3. Data quality summary
4. Recommendations for usage

Keep it concise and professional."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data documentation expert creating clear, concise dataset summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Unable to generate documentation: {str(e)}"
