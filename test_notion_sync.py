import sys
import os

# Add root folder to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from storage.notion_sync import NotionSyncManager

def test_sync():
    print("Initializing NotionSyncManager...")
    sync_manager = NotionSyncManager(interval_sec=5)
    
    # Check credentials
    if not sync_manager.notion_token:
        print("ERROR: NOTION_TOKEN is not set in environment or .env file.")
        return
    if not sync_manager.database_id:
        print("ERROR: DATABASE_ID is not set in environment or .env file.")
        return
        
    print(f"NOTION_TOKEN found (prefix: {sync_manager.notion_token[:8]}...)")
    print(f"DATABASE_ID found: {sync_manager.database_id}")
    
    if not sync_manager.client:
        print("ERROR: notion-client is not installed or initialization failed.")
        return
        
    print("\nRunning a manual sync run...")
    try:
        # Check if report exists
        report_path = os.path.join("reports", "latest_report.json")
        if not os.path.exists(report_path):
            print(f"WARNING: {report_path} not found. Creating a mock report first.")
            os.makedirs("reports", exist_ok=True)
            mock_data = {
                "timestamp": "2026-06-21T11:50:25.063840",
                "stress": {"score": 25.5, "level": "Relaxed"},
                "metrics": {
                    "cv": {
                        "cv_metrics": {
                            "fatigue_index": 12,
                            "attention_score": 95
                        }
                    }
                },
                "contributors": {
                    "typing": 0.8,
                    "mouse_activity": 0.4
                },
                "alert": {"severity": "LOW"}
            }
            import json
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(mock_data, f, indent=2)
            print(f"Mock report created at {report_path}")

        # Run the sync logic
        sync_manager._run_sync()
        print("\nSUCCESS! Successfully synced latest_report.json to Notion.")
        print("Please check your Notion Employee Analytics database to verify the new row is added.")
    except Exception as e:
        print(f"\nERROR: Failed to sync: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sync()
