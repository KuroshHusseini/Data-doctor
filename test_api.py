#!/usr/bin/env python3
"""
Test script to reproduce the 500 error by calling the API directly
"""
import requests
import json


def test_api():
    """Test the upload and analyze endpoints"""
    base_url = "http://localhost:8000"

    print("🧪 Testing Data Doctor API...")

    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return

    # Test upload with demo data
    demo_file = "/Users/kurosh.husseini/Desktop/Junction two/demo_data.csv"

    try:
        print("📤 Testing upload endpoint...")
        with open(demo_file, "rb") as f:
            files = {"file": ("demo_data.csv", f, "text/csv")}
            response = requests.post(f"{base_url}/upload", files=files)

        if response.status_code == 200:
            upload_data = response.json()
            print(f"✅ Upload successful: {upload_data['upload_id']}")
            upload_id = upload_data["upload_id"]

            # Test analyze endpoint
            print("🔍 Testing analyze endpoint...")
            response = requests.post(f"{base_url}/analyze/{upload_id}")

            if response.status_code == 200:
                analysis_data = response.json()
                print(
                    f"✅ Analysis successful: Quality score {analysis_data['quality_score']}"
                )
                print(f"📋 Issues found: {len(analysis_data['issues_found'])}")
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                print(f"Error: {response.text}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_api()
