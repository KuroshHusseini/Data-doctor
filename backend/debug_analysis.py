#!/usr/bin/env python3
"""
Debug script to test the analyze endpoint directly
"""
import os
import sys
import asyncio
import pandas as pd
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from data_processor import DataProcessor
from ai_service import AIService


async def test_analysis():
    """Test the data analysis functionality"""
    print("🔧 Testing Data Doctor Analysis...")

    # Initialize services
    data_processor = DataProcessor()
    ai_service = AIService()

    print("✅ Services initialized successfully")

    # Test with demo data
    demo_file = backend_dir.parent / "demo_data.csv"

    if demo_file.exists():
        print(f"📊 Loading demo data from: {demo_file}")
        try:
            df = data_processor.load_data(str(demo_file))
            print(
                f"✅ Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns"
            )

            print("🔍 Analyzing data quality...")
            quality_report = data_processor.analyze_quality(df)
            print(
                f"✅ Quality analysis complete. Score: {quality_report.quality_score}"
            )
            print(f"📋 Issues found: {len(quality_report.issues)}")

            for i, issue in enumerate(quality_report.issues[:3]):  # Show first 3 issues
                print(f"   {i+1}. {issue.description}")

        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            import traceback

            traceback.print_exc()
    else:
        print(f"❌ Demo data file not found: {demo_file}")

        # Create simple test data
        print("📝 Creating test data...")
        test_data = pd.DataFrame(
            {
                "name": [
                    "Alice",
                    "Bob",
                    "",
                    "Diana",
                    "Alice",
                ],  # Missing value + duplicate
                "age": [25, 30, 22, -5, 25],  # Negative value
                "email": [
                    "alice@test.com",
                    "invalid-email",
                    "charlie@test.com",
                    "diana@test.com",
                    "alice@test.com",
                ],
                "date": [
                    "2023-01-01",
                    "2023-02-30",
                    "2023-03-15",
                    "2023-04-01",
                    "2023-05-01",
                ],  # Invalid date
            }
        )

        print(
            f"✅ Test data created: {test_data.shape[0]} rows, {test_data.shape[1]} columns"
        )

        try:
            print("🔍 Analyzing test data quality...")
            quality_report = data_processor.analyze_quality(test_data)
            print(
                f"✅ Quality analysis complete. Score: {quality_report.quality_score}"
            )
            print(f"📋 Issues found: {len(quality_report.issues)}")

            for i, issue in enumerate(quality_report.issues[:5]):
                print(f"   {i+1}. {issue.description}")

        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_analysis())
