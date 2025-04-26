import os
import json
import platform
import shutil
from typing import Dict, Any, List, Optional
import logging
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("config")

class BrowserConfig:
    """
    Configuration for browser settings, proxies, and extensions.
    """
    
    def __init__(self, browser_name: str = "chrome"):
        """
        Initialize the browser configuration.
        
        Args:
            browser_name: The name of the browser to configure (chrome, firefox, safari).
        """
        self.browser_name = browser_name.lower()
        self.config_dir = os.path.join(os.path.dirname(__file__), "config", self.browser_name)
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load existing configuration if available
        self.config = self._load_config()
        
        logger.info(f"Initialized browser configuration for {browser_name}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the browser configuration from the config file.
        
        Returns:
            The browser configuration.
        """
        config_file = os.path.join(self.config_dir, "config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        # Return default configuration if no config file exists
        return {
            "proxy": {
                "enabled": False,
                "type": "http",
                "host": "",
                "port": 0,
                "username": "",
                "password": ""
            },
            "extensions": [],
            "user_agent": "",
            "window_size": {
                "width": 1280,
                "height": 800
            },
            "cookies": []
        }
    
    def _save_config(self) -> bool:
        """
        Save the browser configuration to the config file.
        
        Returns:
            True if the configuration was saved successfully, False otherwise.
        """
        config_file = os.path.join(self.config_dir, "config.json")
        
        try:
            with open(config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def set_proxy(self, proxy_type: str, host: str, port: int, username: str = "", password: str = "") -> Dict[str, Any]:
        """
        Set the proxy configuration.
        
        Args:
            proxy_type: The type of proxy (http, https, socks4, socks5).
            host: The proxy host.
            port: The proxy port.
            username: The proxy username (optional).
            password: The proxy password (optional).
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            self.config["proxy"] = {
                "enabled": True,
                "type": proxy_type,
                "host": host,
                "port": port,
                "username": username,
                "password": password
            }
            
            if self._save_config():
                return {
                    "success": True,
                    "message": f"Set proxy configuration: {proxy_type}://{host}:{port}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save proxy configuration"
                }
        except Exception as e:
            logger.error(f"Error setting proxy: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to set proxy: {str(e)}"
            }
    
    def disable_proxy(self) -> Dict[str, Any]:
        """
        Disable the proxy configuration.
        
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            self.config["proxy"]["enabled"] = False
            
            if self._save_config():
                return {
                    "success": True,
                    "message": "Disabled proxy configuration"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to disable proxy configuration"
                }
        except Exception as e:
            logger.error(f"Error disabling proxy: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to disable proxy: {str(e)}"
            }
    
    def get_proxy_config(self) -> Dict[str, Any]:
        """
        Get the current proxy configuration.
        
        Returns:
            The proxy configuration.
        """
        return self.config["proxy"]
    
    def get_proxy_args(self) -> List[str]:
        """
        Get the command-line arguments for the proxy configuration.
        
        Returns:
            A list of command-line arguments.
        """
        if not self.config["proxy"]["enabled"]:
            return []
        
        proxy_type = self.config["proxy"]["type"]
        host = self.config["proxy"]["host"]
        port = self.config["proxy"]["port"]
        username = self.config["proxy"]["username"]
        password = self.config["proxy"]["password"]
        
        proxy_url = f"{proxy_type}://"
        
        if username and password:
            proxy_url += f"{username}:{password}@"
        
        proxy_url += f"{host}:{port}"
        
        if self.browser_name == "chrome":
            return [f"--proxy-server={proxy_url}"]
        elif self.browser_name == "firefox":
            return ["-P", "proxy"]  # Use a profile with proxy settings
        
        return []
    
    def add_extension(self, extension_path: str) -> Dict[str, Any]:
        """
        Add a browser extension.
        
        Args:
            extension_path: The path to the extension file or directory.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            # Check if the extension exists
            if not os.path.exists(extension_path):
                return {
                    "success": False,
                    "message": f"Extension not found: {extension_path}"
                }
            
            # Copy the extension to the extensions directory
            extensions_dir = os.path.join(self.config_dir, "extensions")
            os.makedirs(extensions_dir, exist_ok=True)
            
            extension_name = os.path.basename(extension_path)
            extension_dest = os.path.join(extensions_dir, extension_name)
            
            if os.path.isdir(extension_path):
                if os.path.exists(extension_dest):
                    shutil.rmtree(extension_dest)
                shutil.copytree(extension_path, extension_dest)
            else:
                shutil.copy2(extension_path, extension_dest)
            
            # Add the extension to the configuration
            if extension_dest not in self.config["extensions"]:
                self.config["extensions"].append(extension_dest)
            
            if self._save_config():
                return {
                    "success": True,
                    "message": f"Added extension: {extension_name}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save extension configuration"
                }
        except Exception as e:
            logger.error(f"Error adding extension: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to add extension: {str(e)}"
            }
    
    def remove_extension(self, extension_name: str) -> Dict[str, Any]:
        """
        Remove a browser extension.
        
        Args:
            extension_name: The name of the extension to remove.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            extensions_dir = os.path.join(self.config_dir, "extensions")
            
            # Find the extension
            extension_path = None
            for ext in self.config["extensions"]:
                if os.path.basename(ext) == extension_name:
                    extension_path = ext
                    break
            
            if not extension_path:
                return {
                    "success": False,
                    "message": f"Extension not found: {extension_name}"
                }
            
            # Remove the extension from the configuration
            self.config["extensions"].remove(extension_path)
            
            # Remove the extension files
            if os.path.exists(extension_path):
                if os.path.isdir(extension_path):
                    shutil.rmtree(extension_path)
                else:
                    os.remove(extension_path)
            
            if self._save_config():
                return {
                    "success": True,
                    "message": f"Removed extension: {extension_name}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save extension configuration"
                }
        except Exception as e:
            logger.error(f"Error removing extension: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to remove extension: {str(e)}"
            }
    
    def list_extensions(self) -> List[str]:
        """
        List all installed extensions.
        
        Returns:
            A list of extension names.
        """
        return [os.path.basename(ext) for ext in self.config["extensions"]]
    
    def get_extension_args(self) -> List[str]:
        """
        Get the command-line arguments for the extensions.
        
        Returns:
            A list of command-line arguments.
        """
        if not self.config["extensions"]:
            return []
        
        if self.browser_name == "chrome":
            return [f"--load-extension={','.join(self.config['extensions'])}"]
        elif self.browser_name == "firefox":
            # Firefox extensions are loaded through profiles
            return []
        
        return []
    
    def set_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """
        Set the user agent.
        
        Args:
            user_agent: The user agent string.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            self.config["user_agent"] = user_agent
            
            if self._save_config():
                return {
                    "success": True,
                    "message": f"Set user agent: {user_agent}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save user agent configuration"
                }
        except Exception as e:
            logger.error(f"Error setting user agent: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to set user agent: {str(e)}"
            }
    
    def get_user_agent(self) -> str:
        """
        Get the current user agent.
        
        Returns:
            The user agent string.
        """
        return self.config["user_agent"]
    
    def get_user_agent_args(self) -> List[str]:
        """
        Get the command-line arguments for the user agent.
        
        Returns:
            A list of command-line arguments.
        """
        if not self.config["user_agent"]:
            return []
        
        if self.browser_name == "chrome":
            return [f"--user-agent={self.config['user_agent']}"]
        elif self.browser_name == "firefox":
            # Firefox user agent is set through profiles
            return []
        
        return []
    
    def set_window_size(self, width: int, height: int) -> Dict[str, Any]:
        """
        Set the window size.
        
        Args:
            width: The window width.
            height: The window height.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            self.config["window_size"] = {
                "width": width,
                "height": height
            }
            
            if self._save_config():
                return {
                    "success": True,
                    "message": f"Set window size: {width}x{height}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save window size configuration"
                }
        except Exception as e:
            logger.error(f"Error setting window size: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to set window size: {str(e)}"
            }
    
    def get_window_size(self) -> Dict[str, int]:
        """
        Get the current window size.
        
        Returns:
            A dictionary containing the window width and height.
        """
        return self.config["window_size"]
    
    def get_window_size_args(self) -> List[str]:
        """
        Get the command-line arguments for the window size.
        
        Returns:
            A list of command-line arguments.
        """
        width = self.config["window_size"]["width"]
        height = self.config["window_size"]["height"]
        
        if self.browser_name == "chrome":
            return [f"--window-size={width},{height}"]
        elif self.browser_name == "firefox":
            # Firefox window size is set through profiles
            return []
        
        return []
    
    def add_cookie(self, domain: str, name: str, value: str, path: str = "/", secure: bool = False, http_only: bool = False, expiry: Optional[int] = None) -> Dict[str, Any]:
        """
        Add a cookie.
        
        Args:
            domain: The cookie domain.
            name: The cookie name.
            value: The cookie value.
            path: The cookie path.
            secure: Whether the cookie is secure.
            http_only: Whether the cookie is HTTP only.
            expiry: The cookie expiry timestamp.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            cookie = {
                "domain": domain,
                "name": name,
                "value": value,
                "path": path,
                "secure": secure,
                "httpOnly": http_only
            }
            
            if expiry:
                cookie["expiry"] = expiry
            
            # Check if the cookie already exists
            for i, c in enumerate(self.config["cookies"]):
                if c["domain"] == domain and c["name"] == name:
                    # Update the existing cookie
                    self.config["cookies"][i] = cookie
                    break
            else:
                # Add a new cookie
                self.config["cookies"].append(cookie)
            
            if self._save_config():
                return {
                    "success": True,
                    "message": f"Added cookie: {name} for {domain}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save cookie configuration"
                }
        except Exception as e:
            logger.error(f"Error adding cookie: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to add cookie: {str(e)}"
            }
    
    def remove_cookie(self, domain: str, name: str) -> Dict[str, Any]:
        """
        Remove a cookie.
        
        Args:
            domain: The cookie domain.
            name: The cookie name.
            
        Returns:
            A dictionary indicating success or failure.
        """
        try:
            # Find the cookie
            for i, cookie in enumerate(self.config["cookies"]):
                if cookie["domain"] == domain and cookie["name"] == name:
                    # Remove the cookie
                    del self.config["cookies"][i]
                    break
            else:
                return {
                    "success": False,
                    "message": f"Cookie not found: {name} for {domain}"
                }
            
            if self._save_config():
                return {
                    "success": True,
                    "message": f"Removed cookie: {name} for {domain}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save cookie configuration"
                }
        except Exception as e:
            logger.error(f"Error removing cookie: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to remove cookie: {str(e)}"
            }
    
    def get_cookies(self) -> List[Dict[str, Any]]:
        """
        Get all cookies.
        
        Returns:
            A list of cookies.
        """
        return self.config["cookies"]
    
    def get_launch_args(self) -> List[str]:
        """
        Get all command-line arguments for launching the browser.
        
        Returns:
            A list of command-line arguments.
        """
        args = []
        
        args.extend(self.get_proxy_args())
        args.extend(self.get_extension_args())
        args.extend(self.get_user_agent_args())
        args.extend(self.get_window_size_args())
        
        return args
