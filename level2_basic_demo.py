import os
import time
import subprocess
import platform

def launch_browser():
    """
    Launch a browser using OS-level commands.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        cmd = "open -a 'Google Chrome' --args --start-maximized"
    elif system == "Windows":
        cmd = "start chrome --start-maximized"
    elif system == "Linux":
        cmd = "google-chrome --start-maximized"
    else:
        print(f"Unsupported platform: {system}")
        return False
    
    try:
        print(f"Launching browser with command: {cmd}")
        process = subprocess.Popen(cmd, shell=True)
        
        # Wait for the browser to start
        time.sleep(2)
        
        print(f"Browser launched successfully with PID: {process.pid}")
        
        # Wait a bit before closing
        print("Browser will close in 10 seconds...")
        time.sleep(10)
        
        # Close the browser
        process.terminate()
        process.wait()
        
        print("Browser closed successfully")
        return True
    except Exception as e:
        print(f"Error launching browser: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n=== Level 2 Basic Demo: OS-level Browser Control ===")
    
    success = launch_browser()
    
    if success:
        print("\n=== Demo completed successfully ===")
    else:
        print("\n=== Demo failed ===")
