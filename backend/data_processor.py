import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

from models import DataIssue, DataFix, IssueType, FixType, DataQualityReport


class DataProcessor:
    def __init__(self):
        self.date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
        ]

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from various file formats"""
        try:
            if file_path.endswith(".csv"):
                return pd.read_csv(file_path)
            elif file_path.endswith((".xlsx", ".xls")):
                return pd.read_excel(file_path)
            elif file_path.endswith(".json"):
                return pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def analyze_quality(self, df: pd.DataFrame) -> DataQualityReport:
        """Comprehensive data quality analysis"""
        issues = []
        recommendations = []

        # Basic statistics
        total_rows, total_columns = df.shape

        # 1. Missing values analysis
        missing_issues = self._detect_missing_values(df)
        issues.extend(missing_issues)

        # 2. Duplicate detection
        duplicate_issues = self._detect_duplicates(df)
        issues.extend(duplicate_issues)

        # 3. Format inconsistencies
        format_issues = self._detect_format_issues(df)
        issues.extend(format_issues)

        # 4. Data type mismatches
        type_issues = self._detect_type_mismatches(df)
        issues.extend(type_issues)

        # 5. Outlier detection
        outlier_issues = self._detect_outliers(df)
        issues.extend(outlier_issues)

        # 6. Generate recommendations
        recommendations = self._generate_recommendations(issues, df)

        # Calculate quality score
        quality_score = self._calculate_quality_score(issues, total_rows, total_columns)

        return DataQualityReport(
            upload_id="",  # Will be set by the calling function
            quality_score=quality_score,
            total_rows=total_rows,
            total_columns=total_columns,
            issues=issues,
            recommendations=recommendations,
        )

    def _detect_missing_values(self, df: pd.DataFrame) -> List[DataIssue]:
        """Detect missing values in the dataset"""
        issues = []

        for column in df.columns:
            missing_count = df[column].isnull().sum()
            if missing_count > 0:
                missing_percentage = (missing_count / len(df)) * 100

                # Determine severity based on percentage
                if missing_percentage > 50:
                    severity = "critical"
                elif missing_percentage > 20:
                    severity = "high"
                elif missing_percentage > 5:
                    severity = "medium"
                else:
                    severity = "low"

                affected_rows = df[df[column].isnull()].index.tolist()

                # Suggest fix based on data type
                suggested_fix = self._suggest_missing_value_fix(df, column)

                issues.append(
                    DataIssue(
                        issue_type=IssueType.MISSING_VALUES,
                        column=column,
                        description=f"{missing_count} missing values ({missing_percentage:.1f}%)",
                        affected_rows=affected_rows,
                        severity=severity,
                        suggested_fix=suggested_fix,
                        confidence=0.95,
                    )
                )

        return issues

    def _detect_duplicates(self, df: pd.DataFrame) -> List[DataIssue]:
        """Detect duplicate rows"""
        issues = []

        # Check for exact duplicates
        duplicates = df.duplicated()
        duplicate_count = duplicates.sum()

        if duplicate_count > 0:
            affected_rows = df[duplicates].index.tolist()

            severity = "high" if duplicate_count > len(df) * 0.1 else "medium"

            issues.append(
                DataIssue(
                    issue_type=IssueType.DUPLICATES,
                    column="all_columns",
                    description=f"{duplicate_count} duplicate rows found",
                    affected_rows=affected_rows,
                    severity=severity,
                    suggested_fix="Remove duplicate rows, keeping first occurrence",
                    confidence=0.99,
                )
            )

        return issues

    def _detect_format_issues(self, df: pd.DataFrame) -> List[DataIssue]:
        """Detect format inconsistencies"""
        issues = []

        for column in df.columns:
            if df[column].dtype == "object":  # String columns
                # Check for date format inconsistencies
                date_issues = self._check_date_formats(df, column)
                issues.extend(date_issues)

                # Check for case inconsistencies
                case_issues = self._check_case_consistency(df, column)
                issues.extend(case_issues)

                # Check for whitespace issues
                whitespace_issues = self._check_whitespace_issues(df, column)
                issues.extend(whitespace_issues)

        return issues

    def _check_date_formats(self, df: pd.DataFrame, column: str) -> List[DataIssue]:
        """Check for date format inconsistencies"""
        issues = []

        # Try to identify if column contains dates
        sample_values = df[column].dropna().head(100)
        date_like_count = 0

        for value in sample_values:
            if isinstance(value, str):
                for fmt in self.date_formats:
                    try:
                        datetime.strptime(value, fmt)
                        date_like_count += 1
                        break
                    except ValueError:
                        continue

        # If more than 50% of values look like dates, check for format consistency
        if date_like_count > len(sample_values) * 0.5:
            format_counts = {}
            for value in sample_values:
                if isinstance(value, str):
                    for fmt in self.date_formats:
                        try:
                            datetime.strptime(value, fmt)
                            format_counts[fmt] = format_counts.get(fmt, 0) + 1
                            break
                        except ValueError:
                            continue

            if len(format_counts) > 1:
                issues.append(
                    DataIssue(
                        issue_type=IssueType.FORMAT_ERRORS,
                        column=column,
                        description=f"Multiple date formats detected: {list(format_counts.keys())}",
                        affected_rows=[],
                        severity="medium",
                        suggested_fix="Standardize to YYYY-MM-DD format",
                        confidence=0.85,
                    )
                )

        return issues

    def _check_case_consistency(self, df: pd.DataFrame, column: str) -> List[DataIssue]:
        """Check for case inconsistencies in text data"""
        issues = []

        # Get unique values (case-sensitive)
        unique_values = df[column].dropna().unique()

        # Check if there are case variations of the same value
        lower_values = [str(v).lower() for v in unique_values if isinstance(v, str)]
        case_variations = len(lower_values) != len(set(lower_values))

        if case_variations:
            issues.append(
                DataIssue(
                    issue_type=IssueType.INCONSISTENCIES,
                    column=column,
                    description="Case inconsistencies detected in text data",
                    affected_rows=[],
                    severity="low",
                    suggested_fix="Standardize case (e.g., title case or lowercase)",
                    confidence=0.8,
                )
            )

        return issues

    def _check_whitespace_issues(
        self, df: pd.DataFrame, column: str
    ) -> List[DataIssue]:
        """Check for leading/trailing whitespace"""
        issues = []

        # Check for leading/trailing whitespace
        has_whitespace = (
            df[column].astype(str).str.strip().ne(df[column].astype(str)).any()
        )

        if has_whitespace:
            affected_rows = df[
                df[column].astype(str).str.strip().ne(df[column].astype(str))
            ].index.tolist()

            issues.append(
                DataIssue(
                    issue_type=IssueType.FORMAT_ERRORS,
                    column=column,
                    description="Leading or trailing whitespace detected",
                    affected_rows=affected_rows,
                    severity="low",
                    suggested_fix="Trim whitespace from text values",
                    confidence=0.9,
                )
            )

        return issues

    def _detect_type_mismatches(self, df: pd.DataFrame) -> List[DataIssue]:
        """Detect data type mismatches"""
        issues = []

        for column in df.columns:
            if df[column].dtype == "object":
                # Check if numeric values are stored as strings
                numeric_count = 0
                total_count = 0

                for value in df[column].dropna():
                    total_count += 1
                    if isinstance(value, str):
                        try:
                            float(value.replace(",", "").replace("$", ""))
                            numeric_count += 1
                        except ValueError:
                            pass

                if total_count > 0 and numeric_count / total_count > 0.8:
                    issues.append(
                        DataIssue(
                            issue_type=IssueType.DATA_TYPE_MISMATCH,
                            column=column,
                            description="Numeric values stored as text",
                            affected_rows=[],
                            severity="medium",
                            suggested_fix="Convert to numeric data type",
                            confidence=0.85,
                        )
                    )

        return issues

    def _detect_outliers(self, df: pd.DataFrame) -> List[DataIssue]:
        """Detect statistical outliers"""
        issues = []

        for column in df.select_dtypes(include=[np.number]).columns:
            if (
                len(df[column].dropna()) > 10
            ):  # Need sufficient data for outlier detection
                outliers = self._find_outliers(df[column])

                if len(outliers) > 0:
                    severity = "medium" if len(outliers) < len(df) * 0.05 else "high"

                    issues.append(
                        DataIssue(
                            issue_type=IssueType.OUTLIERS,
                            column=column,
                            description=f"{len(outliers)} statistical outliers detected",
                            affected_rows=outliers,
                            severity=severity,
                            suggested_fix="Review outliers for data entry errors",
                            confidence=0.7,
                        )
                    )

        return issues

    def _find_outliers(self, series: pd.Series) -> List[int]:
        """Find outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return outliers.index.tolist()

    def _suggest_missing_value_fix(self, df: pd.DataFrame, column: str) -> str:
        """Suggest appropriate fix for missing values"""
        if df[column].dtype in ["int64", "float64"]:
            return "Fill with median value"
        elif df[column].dtype == "object":
            return "Fill with most frequent value"
        else:
            return "Fill with appropriate default value"

    def _generate_recommendations(
        self, issues: List[DataIssue], df: pd.DataFrame
    ) -> List[str]:
        """Generate recommendations based on detected issues"""
        recommendations = []

        # Count issues by type
        issue_counts = {}
        for issue in issues:
            issue_counts[issue.issue_type] = issue_counts.get(issue.issue_type, 0) + 1

        # Generate specific recommendations
        if IssueType.MISSING_VALUES in issue_counts:
            recommendations.append(
                f"Address {issue_counts[IssueType.MISSING_VALUES]} columns with missing values"
            )

        if IssueType.DUPLICATES in issue_counts:
            recommendations.append("Remove duplicate rows to ensure data uniqueness")

        if IssueType.FORMAT_ERRORS in issue_counts:
            recommendations.append("Standardize date and text formats across columns")

        if IssueType.OUTLIERS in issue_counts:
            recommendations.append("Review and validate outlier values for accuracy")

        # General recommendations
        recommendations.append(
            "Consider implementing data validation rules for future uploads"
        )
        recommendations.append("Document data quality standards and expected formats")

        return recommendations

    def _calculate_quality_score(
        self, issues: List[DataIssue], total_rows: int, total_columns: int
    ) -> float:
        """Calculate overall data quality score"""
        if not issues:
            return 1.0

        # Weight issues by severity
        severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}

        total_penalty = 0
        for issue in issues:
            penalty = severity_weights.get(issue.severity, 0.3)
            # Adjust penalty based on affected rows percentage
            if issue.affected_rows:
                affected_percentage = len(issue.affected_rows) / total_rows
                penalty *= affected_percentage
            total_penalty += penalty

        # Normalize penalty (max penalty is 1.0)
        max_possible_penalty = len(issues) * 1.0
        normalized_penalty = min(total_penalty / max_possible_penalty, 1.0)

        return max(0.0, 1.0 - normalized_penalty)

    def apply_fixes(
        self, df: pd.DataFrame, issues: List[Dict[str, Any]]
    ) -> Tuple[pd.DataFrame, List[DataFix]]:
        """Apply automated fixes to data issues"""
        df_fixed = df.copy()
        fixes_applied = []

        for issue_data in issues:
            issue_type = issue_data["issue_type"]
            column = issue_data["column"]

            if issue_type == IssueType.MISSING_VALUES:
                fix = self._fix_missing_values(df_fixed, column, issue_data)
                if fix:
                    fixes_applied.append(fix)

            elif issue_type == IssueType.DUPLICATES:
                fix = self._fix_duplicates(df_fixed, issue_data)
                if fix:
                    fixes_applied.append(fix)

            elif issue_type == IssueType.FORMAT_ERRORS:
                fix = self._fix_format_errors(df_fixed, column, issue_data)
                if fix:
                    fixes_applied.append(fix)

            elif issue_type == IssueType.OUTLIERS:
                fix = self._fix_outliers(df_fixed, column, issue_data)
                if fix:
                    fixes_applied.append(fix)

        return df_fixed, fixes_applied

    def _fix_missing_values(
        self, df: pd.DataFrame, column: str, issue_data: Dict[str, Any]
    ) -> Optional[DataFix]:
        """Fix missing values in a column"""
        if df[column].dtype in ["int64", "float64"]:
            # Fill with median for numeric columns
            median_value = df[column].median()
            old_values = df[column].isnull()
            df[column].fillna(median_value, inplace=True)

            return DataFix(
                fix_type=FixType.FILL_MISSING,
                column=column,
                description=f"Filled {old_values.sum()} missing values with median: {median_value}",
                rows_affected=df[old_values].index.tolist(),
                old_values=[None] * old_values.sum(),
                new_values=[median_value] * old_values.sum(),
                confidence=0.8,
            )

        elif df[column].dtype == "object":
            # Fill with most frequent value for categorical columns
            most_frequent = (
                df[column].mode().iloc[0] if not df[column].mode().empty else "Unknown"
            )
            old_values = df[column].isnull()
            df[column].fillna(most_frequent, inplace=True)

            return DataFix(
                fix_type=FixType.FILL_MISSING,
                column=column,
                description=f"Filled {old_values.sum()} missing values with most frequent: {most_frequent}",
                rows_affected=df[old_values].index.tolist(),
                old_values=[None] * old_values.sum(),
                new_values=[most_frequent] * old_values.sum(),
                confidence=0.7,
            )

        return None

    def _fix_duplicates(
        self, df: pd.DataFrame, issue_data: Dict[str, Any]
    ) -> Optional[DataFix]:
        """Remove duplicate rows"""
        initial_rows = len(df)
        df.drop_duplicates(inplace=True, keep="first")
        removed_rows = initial_rows - len(df)

        if removed_rows > 0:
            return DataFix(
                fix_type=FixType.REMOVE_DUPLICATES,
                column="all_columns",
                description=f"Removed {removed_rows} duplicate rows",
                rows_affected=[],
                old_values=[],
                new_values=[],
                confidence=0.99,
            )

        return None

    def _fix_format_errors(
        self, df: pd.DataFrame, column: str, issue_data: Dict[str, Any]
    ) -> Optional[DataFix]:
        """Fix format errors in a column"""
        if df[column].dtype == "object":
            # Trim whitespace
            old_values = df[column].copy()
            df[column] = df[column].astype(str).str.strip()

            # Check if any changes were made
            changes_made = not old_values.equals(df[column])

            if changes_made:
                return DataFix(
                    fix_type=FixType.STANDARDIZE_FORMAT,
                    column=column,
                    description="Trimmed leading and trailing whitespace",
                    rows_affected=[],
                    old_values=old_values.tolist(),
                    new_values=df[column].tolist(),
                    confidence=0.9,
                )

        return None

    def _fix_outliers(
        self, df: pd.DataFrame, column: str, issue_data: Dict[str, Any]
    ) -> Optional[DataFix]:
        """Fix outliers by capping them to reasonable values"""
        if df[column].dtype in ["int64", "float64"]:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Cap outliers
            old_values = df[column].copy()
            df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)

            # Check if any changes were made
            changes_made = not old_values.equals(df[column])

            if changes_made:
                affected_rows = df[old_values != df[column]].index.tolist()

                return DataFix(
                    fix_type=FixType.CORRECT_OUTLIER,
                    column=column,
                    description=f"Capped outliers to range [{lower_bound:.2f}, {upper_bound:.2f}]",
                    rows_affected=affected_rows,
                    old_values=old_values[affected_rows].tolist(),
                    new_values=df[column][affected_rows].tolist(),
                    confidence=0.6,
                    uncertainty_reason="Statistical capping may not reflect true data values",
                )

        return None

    def generate_comparison(
        self, df_original: pd.DataFrame, df_fixed: pd.DataFrame
    ) -> Dict[str, Any]:
        """Generate before/after comparison"""
        return {
            "original_shape": df_original.shape,
            "fixed_shape": df_fixed.shape,
            "rows_removed": df_original.shape[0] - df_fixed.shape[0],
            "columns_changed": list(df_original.columns),
            "summary": {
                "original_missing_values": df_original.isnull().sum().sum(),
                "fixed_missing_values": df_fixed.isnull().sum().sum(),
                "original_duplicates": df_original.duplicated().sum(),
                "fixed_duplicates": df_fixed.duplicated().sum(),
            },
        }
