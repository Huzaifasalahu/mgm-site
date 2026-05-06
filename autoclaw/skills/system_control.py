"""
AutoClaw - Autonomous AI Agent Platform
System Control Skill

Handles system operations: launch apps, execute commands, screenshots, etc.
"""

import subprocess
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

SKILL_METADATA = {
    "name": "system_control",
    "version": "1.0.0",
    "description": "System control: launch apps, execute commands, take screenshots",
    "author": "AutoClaw Team",
    "capabilities": [
        "launch_app",
        "execute_command",
        "take_screenshot",
        "get_system_info",
        "list_processes"
    ]
}


class SystemControl:
    """
    System control operations.
    
    Features:
    - Launch applications
    - Execute system commands
    - Take screenshots
    - Monitor system resources
    - List running processes
    """
    
    def __init__(self):
        self.os_type = platform.system()
        self.executed_commands = []
    
    async def launch_app(self, app_name: str, arguments: Optional[List[str]] = None) -> Dict:
        """
        Launch an application.
        
        Args:
            app_name: Application name or path
            arguments: Optional command-line arguments
            
        Returns:
            Launch result
        """
        try:
            cmd = [app_name]
            if arguments:
                cmd.extend(arguments)
            
            # Start the application
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.executed_commands.append({
                "type": "launch_app",
                "app": app_name,
                "timestamp": datetime.now().isoformat(),
                "pid": process.pid
            })
            
            return {
                "success": True,
                "app": app_name,
                "pid": process.pid,
                "message": f"Launched {app_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "app": app_name
            }
    
    async def execute_command(self, command: str, shell: bool = True, 
                             timeout: int = 30) -> Dict:
        """
        Execute a system command.
        
        Args:
            command: Command to execute
            shell: Whether to run in shell
            timeout: Execution timeout in seconds
            
        Returns:
            Command output
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            self.executed_commands.append({
                "type": "execute_command",
                "command": command,
                "timestamp": datetime.now().isoformat(),
                "return_code": result.returncode
            })
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": result.elapsed.total_seconds() if hasattr(result, 'elapsed') else 0
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    async def take_screenshot(self, filename: Optional[str] = None) -> Dict:
        """
        Take a screenshot of the current screen.
        
        Args:
            filename: Optional filename for the screenshot
            
        Returns:
            Screenshot result with path
        """
        try:
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_dir = Path.home() / "autoclaw_screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / filename
            
            # Take screenshot based on OS
            if self.os_type == "Darwin":  # macOS
                subprocess.run([
                    "screencapture",
                    "-x",
                    str(screenshot_path)
                ], check=True)
            elif self.os_type == "Windows":
                # Use PowerShell for Windows
                ps_script = f"""
                Add-Type -AssemblyName System.Windows.Forms
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen
                $bitmap = New-Object System.Drawing.Bitmap $screen.Bounds.Width, $screen.Bounds.Height
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphics.CopyFromScreen($screen.Bounds.X, $screen.Bounds.Y, 0, 0, $bitmap.Size)
                $bitmap.Save('{screenshot_path}')
                $graphics.Dispose()
                $bitmap.Dispose()
                """
                subprocess.run(["powershell", "-Command", ps_script], check=True)
            else:  # Linux
                try:
                    subprocess.run(["gnome-screenshot", "-f", str(screenshot_path)], check=True)
                except FileNotFoundError:
                    subprocess.run(["scrot", str(screenshot_path)], check=True)
            
            return {
                "success": True,
                "path": str(screenshot_path),
                "message": f"Screenshot saved to {screenshot_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_info(self) -> Dict:
        """
        Get system information.
        
        Returns:
            System information dictionary
        """
        try:
            info = {
                "os": self.os_type,
                "os_version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
                "username": os.getenv("USER") or os.getenv("USERNAME") or "unknown"
            }
            
            # Get CPU count
            import multiprocessing
            info["cpu_count"] = multiprocessing.cpu_count()
            
            # Get memory info (platform-specific)
            if self.os_type == "Linux":
                try:
                    with open("/proc/meminfo", "r") as f:
                        meminfo = {}
                        for line in f:
                            parts = line.split(":")
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip().split()[0]
                                meminfo[key] = value
                        info["memory_total_kb"] = meminfo.get("MemTotal", "unknown")
                        info["memory_available_kb"] = meminfo.get("MemAvailable", "unknown")
                except:
                    pass
            elif self.os_type == "Darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    info["memory_total_bytes"] = result.stdout.strip()
            
            return {
                "success": True,
                "system_info": info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_processes(self, filter_name: Optional[str] = None) -> Dict:
        """
        List running processes.
        
        Args:
            filter_name: Optional filter by process name
            
        Returns:
            List of processes
        """
        try:
            if self.os_type == "Windows":
                result = subprocess.run(
                    ["tasklist", "/FO", "CSV"],
                    capture_output=True,
                    text=True
                )
                processes = self._parse_windows_processes(result.stdout, filter_name)
            else:
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True
                )
                processes = self._parse_unix_processes(result.stdout, filter_name)
            
            return {
                "success": True,
                "processes": processes,
                "count": len(processes)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_windows_processes(self, csv_output: str, filter_name: Optional[str]) -> List[Dict]:
        """Parse Windows tasklist CSV output."""
        processes = []
        lines = csv_output.strip().split("\n")[1:]  # Skip header
        
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 5:
                name = parts[0].strip('"')
                pid = parts[1].strip('"')
                
                if filter_name and filter_name.lower() not in name.lower():
                    continue
                
                processes.append({
                    "name": name,
                    "pid": pid,
                    "os": "windows"
                })
        
        return processes
    
    def _parse_unix_processes(self, ps_output: str, filter_name: Optional[str]) -> List[Dict]:
        """Parse Unix ps aux output."""
        processes = []
        lines = ps_output.strip().split("\n")[1:]  # Skip header
        
        for line in lines:
            parts = line.split(None, 10)
            if len(parts) >= 11:
                pid = parts[1]
                cpu = parts[2]
                mem = parts[3]
                name = parts[10]
                
                if filter_name and filter_name.lower() not in name.lower():
                    continue
                
                processes.append({
                    "name": name,
                    "pid": pid,
                    "cpu": cpu,
                    "memory": mem,
                    "os": "unix"
                })
        
        return processes
    
    async def execute(self, action: str, **kwargs) -> Dict:
        """Generic execute method for tool manager compatibility."""
        if action == "launch_app":
            return await self.launch_app(
                kwargs.get("app_name", ""),
                kwargs.get("arguments")
            )
        elif action == "execute_command":
            return await self.execute_command(
                kwargs.get("command", ""),
                kwargs.get("shell", True),
                kwargs.get("timeout", 30)
            )
        elif action == "take_screenshot":
            return await self.take_screenshot(kwargs.get("filename"))
        elif action == "get_system_info":
            return await self.get_system_info()
        elif action == "list_processes":
            return await self.list_processes(kwargs.get("filter_name"))
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
