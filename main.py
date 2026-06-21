import subprocess
import time
import webbrowser
import sys
import os
import signal

backend_process = None
frontend_process = None

def cleanup():
    print("\n[Synapse Launcher] Shutting down services...", flush=True)
    if backend_process:
        print(f"[Synapse Launcher] Terminating backend process (PID {backend_process.pid}) tree...", flush=True)
        try:
            # On Windows, taskkill /F /T kills the process and all its children (essential for uvicorn and python subprocesses)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(backend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            backend_process.terminate()
    if frontend_process:
        print(f"[Synapse Launcher] Terminating frontend process (PID {frontend_process.pid}) tree...", flush=True)
        try:
            # taskkill is also essential for npm run dev which spawns shell and node child processes
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(frontend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            frontend_process.terminate()
    print("[Synapse Launcher] All services stopped.", flush=True)

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

def main():
    global backend_process, frontend_process

    # Register signal handlers for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("[Synapse Launcher] Starting Synapse Engine...", flush=True)
    print("[Synapse Launcher] Starting FastAPI backend on http://127.0.0.1:8000 ...", flush=True)
    
    # Check and free port 8000 if it's already in use
    try:
        if sys.platform.startswith("win"):
            # Check if port 8000 is bound
            netstat_output = subprocess.run(
                ["netstat", "-ano", "-p", "tcp"],
                capture_output=True,
                text=True,
                check=True
            ).stdout
            # Search for a line matching port 8000
            for line in netstat_output.splitlines():
                if ":8000 " in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"[Synapse Launcher] Port 8000 is already in use by PID {pid}. Cleaning up...", flush=True)
                        subprocess.run(["taskkill", "/F", "/T", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(1) # wait for the port to release
                        break
    except Exception as e:
        print(f"[Synapse Launcher] Warning: Could not auto-clear port 8000: {e}", flush=True)

    # Start backend
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Start frontend
    print("[Synapse Launcher] Starting React frontend dev server on http://localhost:5173 ...", flush=True)
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(os.getcwd(), "frontend"),
        shell=True # Required on Windows to resolve npm command
    )

    # Wait a few seconds for servers to initialize
    print("[Synapse Launcher] Initializing servers (waiting 4 seconds)...", flush=True)
    time.sleep(4)

    # Check if backend or frontend died immediately
    if backend_process.poll() is not None:
        print("[Synapse Launcher] ERROR: Backend failed to start. Standard error:")
        _, err = backend_process.communicate()
        print(err, flush=True)
        cleanup()
        sys.exit(1)
        
    if frontend_process.poll() is not None:
        print("[Synapse Launcher] ERROR: Frontend failed to start.", flush=True)
        cleanup()
        sys.exit(1)

    print("[Synapse Launcher] Launching dashboard in default browser...", flush=True)
    webbrowser.open("http://localhost:5173")

    print("[Synapse Launcher] Synapse running successfully! Press Ctrl+C to stop all services.", flush=True)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    main()
