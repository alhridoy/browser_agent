import os
import platform
import subprocess
import shutil
from typing import Dict, Any, List, Optional, Tuple
import logging
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("platform_adapter")

class PlatformAdapter:
    """
    Adapter for platform-specific operations to ensure cross-platform compatibility.
    """
    
    def __init__(self):
        """
        Initialize the platform adapter.
        """
        self.system = platform.system()
        self.release = platform.release()
        self.version = platform.version()
        self.machine = platform.machine()
        
        logger.info(f"Initialized platform adapter for {self.system} {self.release} ({self.machine})")
    
    def get_browser_command(self, browser_name: str, args: List[str] = None) -> str:
        """
        Get the command to launch a browser on the current platform.
        
        Args:
            browser_name: The name of the browser (chrome, firefox, edge, safari).
            args: Additional command-line arguments.
            
        Returns:
            The command to launch the browser.
        """
        if args is None:
            args = []
        
        args_str = " ".join(args)
        
        if self.system == "Darwin":  # macOS
            if browser_name.lower() == "chrome":
                return f"open -a 'Google Chrome' --args {args_str}"
            elif browser_name.lower() == "firefox":
                return f"open -a Firefox --args {args_str}"
            elif browser_name.lower() == "safari":
                return f"open -a Safari --args {args_str}"
            elif browser_name.lower() == "edge":
                return f"open -a 'Microsoft Edge' --args {args_str}"
        elif self.system == "Windows":
            if browser_name.lower() == "chrome":
                return f"start chrome {args_str}"
            elif browser_name.lower() == "firefox":
                return f"start firefox {args_str}"
            elif browser_name.lower() == "edge":
                return f"start msedge {args_str}"
            elif browser_name.lower() == "ie":
                return f"start iexplore {args_str}"
        elif self.system == "Linux":
            if browser_name.lower() == "chrome":
                # Try different Chrome executable names
                chrome_executables = ["google-chrome", "chrome", "chromium", "chromium-browser"]
                for executable in chrome_executables:
                    if shutil.which(executable):
                        return f"{executable} {args_str}"
            elif browser_name.lower() == "firefox":
                return f"firefox {args_str}"
            elif browser_name.lower() == "edge":
                return f"microsoft-edge {args_str}"
        
        # Default fallback
        return f"{browser_name} {args_str}"
    
    def get_keyboard_shortcut(self, action: str) -> Tuple[str, str]:
        """
        Get the keyboard shortcut for a specific action on the current platform.
        
        Args:
            action: The action (e.g., "address_bar", "new_tab", "close_tab").
            
        Returns:
            A tuple of (modifier_key, key) for the shortcut.
        """
        if self.system == "Darwin":  # macOS
            shortcuts = {
                "address_bar": ("command", "l"),
                "new_tab": ("command", "t"),
                "close_tab": ("command", "w"),
                "refresh": ("command", "r"),
                "select_all": ("command", "a"),
                "copy": ("command", "c"),
                "paste": ("command", "v"),
                "cut": ("command", "x"),
                "save": ("command", "s"),
                "find": ("command", "f"),
                "print": ("command", "p"),
                "zoom_in": ("command", "+"),
                "zoom_out": ("command", "-"),
                "zoom_reset": ("command", "0"),
                "back": ("command", "["),
                "forward": ("command", "]"),
                "home": ("command", "home"),
                "end": ("command", "end"),
                "select_to_start": ("command+shift", "home"),
                "select_to_end": ("command+shift", "end"),
            }
        else:  # Windows/Linux
            shortcuts = {
                "address_bar": ("ctrl", "l"),
                "new_tab": ("ctrl", "t"),
                "close_tab": ("ctrl", "w"),
                "refresh": ("ctrl", "r"),
                "select_all": ("ctrl", "a"),
                "copy": ("ctrl", "c"),
                "paste": ("ctrl", "v"),
                "cut": ("ctrl", "x"),
                "save": ("ctrl", "s"),
                "find": ("ctrl", "f"),
                "print": ("ctrl", "p"),
                "zoom_in": ("ctrl", "+"),
                "zoom_out": ("ctrl", "-"),
                "zoom_reset": ("ctrl", "0"),
                "back": ("alt", "left"),
                "forward": ("alt", "right"),
                "home": ("home", ""),
                "end": ("end", ""),
                "select_to_start": ("shift", "home"),
                "select_to_end": ("shift", "end"),
            }
        
        return shortcuts.get(action, ("", ""))
    
    def get_config_directory(self, app_name: str) -> str:
        """
        Get the platform-specific configuration directory.
        
        Args:
            app_name: The name of the application.
            
        Returns:
            The path to the configuration directory.
        """
        if self.system == "Darwin":  # macOS
            config_dir = os.path.expanduser(f"~/Library/Application Support/{app_name}")
        elif self.system == "Windows":
            config_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), app_name)
        else:  # Linux
            config_dir = os.path.expanduser(f"~/.config/{app_name}")
        
        # Create the directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        return config_dir
    
    def get_data_directory(self, app_name: str) -> str:
        """
        Get the platform-specific data directory.
        
        Args:
            app_name: The name of the application.
            
        Returns:
            The path to the data directory.
        """
        if self.system == "Darwin":  # macOS
            data_dir = os.path.expanduser(f"~/Library/Application Support/{app_name}/Data")
        elif self.system == "Windows":
            data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), app_name, "Data")
        else:  # Linux
            data_dir = os.path.expanduser(f"~/.local/share/{app_name}")
        
        # Create the directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        return data_dir
    
    def get_temp_directory(self, app_name: str) -> str:
        """
        Get the platform-specific temporary directory.
        
        Args:
            app_name: The name of the application.
            
        Returns:
            The path to the temporary directory.
        """
        temp_dir = os.path.join(os.path.abspath(os.sep), "tmp" if self.system != "Windows" else os.environ.get("TEMP", "C:\\Temp"), app_name)
        
        # Create the directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
        
        return temp_dir
    
    def get_browser_data_directory(self, browser_name: str) -> str:
        """
        Get the platform-specific browser data directory.
        
        Args:
            browser_name: The name of the browser.
            
        Returns:
            The path to the browser data directory.
        """
        if self.system == "Darwin":  # macOS
            if browser_name.lower() == "chrome":
                return os.path.expanduser("~/Library/Application Support/Google/Chrome")
            elif browser_name.lower() == "firefox":
                return os.path.expanduser("~/Library/Application Support/Firefox")
            elif browser_name.lower() == "safari":
                return os.path.expanduser("~/Library/Safari")
            elif browser_name.lower() == "edge":
                return os.path.expanduser("~/Library/Application Support/Microsoft Edge")
        elif self.system == "Windows":
            if browser_name.lower() == "chrome":
                return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data")
            elif browser_name.lower() == "firefox":
                return os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles")
            elif browser_name.lower() == "edge":
                return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data")
            elif browser_name.lower() == "ie":
                return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Internet Explorer")
        elif self.system == "Linux":
            if browser_name.lower() == "chrome":
                return os.path.expanduser("~/.config/google-chrome")
            elif browser_name.lower() == "firefox":
                return os.path.expanduser("~/.mozilla/firefox")
            elif browser_name.lower() == "edge":
                return os.path.expanduser("~/.config/microsoft-edge")
        
        # Default fallback
        return os.path.expanduser(f"~/.{browser_name}")
    
    def is_process_running(self, process_name: str) -> bool:
        """
        Check if a process is running.
        
        Args:
            process_name: The name of the process.
            
        Returns:
            True if the process is running, False otherwise.
        """
        try:
            if self.system == "Windows":
                output = subprocess.check_output(f"tasklist /FI \"IMAGENAME eq {process_name}*\"", shell=True).decode()
                return process_name.lower() in output.lower()
            else:  # macOS/Linux
                output = subprocess.check_output(f"ps -A | grep -i {process_name}", shell=True).decode()
                return process_name.lower() in output.lower()
        except subprocess.CalledProcessError:
            return False
    
    def kill_process(self, process_name: str) -> bool:
        """
        Kill a process.
        
        Args:
            process_name: The name of the process.
            
        Returns:
            True if the process was killed successfully, False otherwise.
        """
        try:
            if self.system == "Windows":
                subprocess.check_output(f"taskkill /F /IM {process_name}*", shell=True)
            else:  # macOS/Linux
                subprocess.check_output(f"pkill -f {process_name}", shell=True)
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_screen_resolution(self) -> Tuple[int, int]:
        """
        Get the screen resolution.
        
        Returns:
            A tuple of (width, height) for the screen resolution.
        """
        try:
            import pyautogui
            return pyautogui.size()
        except ImportError:
            # Fallback if pyautogui is not available
            if self.system == "Windows":
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
                except:
                    return 1920, 1080  # Default fallback
            elif self.system == "Darwin":  # macOS
                try:
                    output = subprocess.check_output("system_profiler SPDisplaysDataType | grep Resolution", shell=True).decode()
                    resolution = output.split("Resolution:")[1].strip().split(" x ")
                    return int(resolution[0]), int(resolution[1])
                except:
                    return 1920, 1080  # Default fallback
            else:  # Linux
                try:
                    output = subprocess.check_output("xrandr | grep '*'", shell=True).decode()
                    resolution = output.split("*")[0].strip().split(" ")
                    return int(resolution[0]), int(resolution[1])
                except:
                    return 1920, 1080  # Default fallback
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            A dictionary containing system information.
        """
        info = {
            "system": self.system,
            "release": self.release,
            "version": self.version,
            "machine": self.machine,
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "node": platform.node(),
        }
        
        # Add screen resolution
        try:
            width, height = self.get_screen_resolution()
            info["screen_width"] = width
            info["screen_height"] = height
        except:
            pass
        
        # Add memory information
        try:
            import psutil
            memory = psutil.virtual_memory()
            info["total_memory"] = memory.total
            info["available_memory"] = memory.available
            info["memory_percent"] = memory.percent
        except ImportError:
            pass
        
        return info
