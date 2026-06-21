import os

class RetentionManager:
    """Manages the retention policy for historical data (e.g. snapshots)."""
    
    @staticmethod
    def enforce_retention(directory: str, max_files: int = 500):
        """
        Scans a directory, orders files by modification time, and deletes 
        the oldest files if the total exceeds max_files.
        """
        if not os.path.exists(directory):
            return
            
        files = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and filename.endswith(".json"):
                files.append((filepath, os.path.getmtime(filepath)))
                
        if len(files) <= max_files:
            return
            
        # Sort by modification time (oldest first)
        files.sort(key=lambda x: x[1])
        
        files_to_delete = len(files) - max_files
        
        for i in range(files_to_delete):
            try:
                os.remove(files[i][0])
            except Exception as e:
                print(f"RetentionManager: Failed to delete {files[i][0]}: {e}", flush=True)
