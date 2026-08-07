import subprocess
import os
import sys
import time
import shutil

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    
    backend_dir = os.path.join(root_dir, 'backend')
    frontend_dir = os.path.join(root_dir, 'frontend')

    backend_process = None
    frontend_process = None

    try:
        # 1. Start Backend
        print("=== Starting Backend ===")
        venv_dir = os.path.join(backend_dir, '.venv')
        if not os.path.exists(venv_dir):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=backend_dir, check=True)
            
        print("Installing backend dependencies...")
        pip_exe = os.path.join(venv_dir, 'Scripts', 'pip.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'pip')
        subprocess.run([pip_exe, "install", "-r", "requirements.txt"], cwd=backend_dir, check=True)
        
        print("Running backend server on http://localhost:8000...")
        python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'python')
        backend_process = subprocess.Popen([python_exe, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd=backend_dir)
        
        # 2. Start Frontend
        print("\n=== Starting Frontend ===")
        npm_path = shutil.which("npm")
        if not npm_path:
            npm_path = "npm.cmd" if os.name == 'nt' else "npm"
            
        print(f"Using npm at: {npm_path}")
        
        print("Installing frontend dependencies...")
        subprocess.run([npm_path, "install"], cwd=frontend_dir, check=True)
        
        print("Building frontend...")
        subprocess.run([npm_path, "run", "build"], cwd=frontend_dir, check=True)
        
        print("Running frontend server on http://localhost:3000...")
        frontend_process = subprocess.Popen([npm_path, "start"], cwd=frontend_dir)
        
        print("\n=== Both servers are starting up! ===")
        print("Frontend: http://localhost:3000 (Production Build)")
        print("Backend:  http://localhost:8000")
        print("Press Ctrl+C to stop both servers.\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Stopping servers...")
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()

if __name__ == "__main__":
    main()
