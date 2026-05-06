"""
AutoClaw - Autonomous AI Agent Platform
Scheduler Skill

Task scheduling for timed and repeating tasks.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import asyncio
import threading

SKILL_METADATA = {
    "name": "scheduler",
    "version": "1.0.0",
    "description": "Schedule tasks: one-time, recurring, interval-based",
    "author": "AutoClaw Team",
    "capabilities": [
        "schedule_task",
        "cancel_task",
        "list_tasks",
        "run_now"
    ]
}


class TaskScheduler:
    """
    Task scheduling system.
    
    Features:
    - One-time scheduled tasks
    - Recurring tasks (daily, weekly, monthly)
    - Interval-based tasks
    - Task cancellation
    - Run task immediately
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks_file = self.data_dir / "scheduled_tasks.json"
        
        # In-memory task storage
        self.tasks = {}
        self.running = False
        self._task_thread = None
        
        # Load existing tasks
        self._load_tasks()
        
        # Start scheduler thread
        self.start()
    
    def _load_tasks(self):
        """Load tasks from disk."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = {}
    
    def _save_tasks(self):
        """Save tasks to disk."""
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)
    
    def start(self):
        """Start the scheduler background thread."""
        if self.running:
            return
        
        self.running = True
        self._task_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._task_thread.start()
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
    
    def _run_scheduler(self):
        """Background scheduler loop."""
        while self.running:
            now = datetime.now()
            
            for task_id, task in list(self.tasks.items()):
                if not task.get("enabled", True):
                    continue
                
                next_run = task.get("next_run")
                if not next_run:
                    continue
                
                next_run_dt = datetime.fromisoformat(next_run)
                
                if now >= next_run_dt:
                    # Task is due
                    self._execute_task(task_id, task)
                    
                    # Calculate next run time
                    self._update_next_run(task)
            
            # Check every 30 seconds
            asyncio.run(asyncio.sleep(30))
    
    def _execute_task(self, task_id: str, task: Dict):
        """Execute a scheduled task."""
        try:
            # Log execution
            execution = {
                "task_id": task_id,
                "executed_at": datetime.now().isoformat(),
                "goal": task.get("goal", "")
            }
            
            # Update execution history
            if "execution_history" not in task:
                task["execution_history"] = []
            task["execution_history"].append(execution)
            
            # Keep last 50 executions
            task["execution_history"] = task["execution_history"][-50:]
            
            task["last_executed"] = datetime.now().isoformat()
            task["execution_count"] = task.get("execution_count", 0) + 1
            
            self._save_tasks()
            
        except Exception as e:
            print(f"Error executing task {task_id}: {e}")
    
    def _update_next_run(self, task: Dict):
        """Update the next run time for a task."""
        schedule_type = task.get("schedule_type", "once")
        
        if schedule_type == "once":
            task["next_run"] = None
            task["enabled"] = False
        elif schedule_type == "interval":
            interval_minutes = task.get("interval_minutes", 60)
            next_run = datetime.now() + timedelta(minutes=interval_minutes)
            task["next_run"] = next_run.isoformat()
        elif schedule_type == "daily":
            hour = task.get("hour", 9)
            minute = task.get("minute", 0)
            next_run = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= datetime.now():
                next_run += timedelta(days=1)
            task["next_run"] = next_run.isoformat()
        elif schedule_type == "weekly":
            weekday = task.get("weekday", 0)
            hour = task.get("hour", 9)
            minute = task.get("minute", 0)
            next_run = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            days_ahead = weekday - next_run.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
            if next_run <= datetime.now():
                next_run += timedelta(weeks=1)
            task["next_run"] = next_run.isoformat()
        
        self._save_tasks()
    
    async def schedule_task(self, goal: str, schedule_type: str = "once",
                           run_at: Optional[str] = None,
                           interval_minutes: Optional[int] = None,
                           daily_time: Optional[str] = None,
                           weekly_day: Optional[int] = None,
                           enabled: bool = True) -> Dict:
        """
        Schedule a new task.
        
        Args:
            goal: Task goal/description
            schedule_type: Type (once, interval, daily, weekly)
            run_at: ISO format datetime for one-time tasks
            interval_minutes: Minutes between runs for interval tasks
            daily_time: "HH:MM" for daily tasks
            weekly_day: 0-6 (Monday-Sunday) for weekly tasks
            enabled: Whether task is enabled
            
        Returns:
            Scheduling result
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.tasks)}"
        
        task = {
            "id": task_id,
            "goal": goal,
            "schedule_type": schedule_type,
            "enabled": enabled,
            "created_at": datetime.now().isoformat(),
            "execution_count": 0,
            "execution_history": []
        }
        
        # Calculate first run time
        if schedule_type == "once":
            if run_at:
                task["next_run"] = run_at
            else:
                task["next_run"] = datetime.now().isoformat()
        elif schedule_type == "interval":
            task["interval_minutes"] = interval_minutes or 60
            task["next_run"] = (datetime.now() + timedelta(minutes=task["interval_minutes"])).isoformat()
        elif schedule_type == "daily":
            if daily_time:
                hour, minute = map(int, daily_time.split(":"))
            else:
                hour, minute = 9, 0
            task["hour"] = hour
            task["minute"] = minute
            next_run = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= datetime.now():
                next_run += timedelta(days=1)
            task["next_run"] = next_run.isoformat()
        elif schedule_type == "weekly":
            task["weekday"] = weekly_day or 0
            task["hour"] = 9
            task["minute"] = 0
            next_run = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            days_ahead = task["weekday"] - next_run.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
            task["next_run"] = next_run.isoformat()
        
        self.tasks[task_id] = task
        self._save_tasks()
        
        return {
            "success": True,
            "task_id": task_id,
            "next_run": task["next_run"],
            "message": f"Task scheduled: {goal[:50]}..."
        }
    
    async def cancel_task(self, task_id: str) -> Dict:
        """Cancel a scheduled task."""
        if task_id not in self.tasks:
            return {"success": False, "error": f"Task not found: {task_id}"}
        
        del self.tasks[task_id]
        self._save_tasks()
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task cancelled"
        }
    
    async def list_tasks(self, include_history: bool = False) -> Dict:
        """List all scheduled tasks."""
        tasks_list = []
        for task_id, task in self.tasks.items():
            task_info = {
                "id": task_id,
                "goal": task.get("goal", ""),
                "schedule_type": task.get("schedule_type", ""),
                "next_run": task.get("next_run"),
                "enabled": task.get("enabled", True),
                "execution_count": task.get("execution_count", 0),
                "last_executed": task.get("last_executed")
            }
            
            if include_history:
                task_info["execution_history"] = task.get("execution_history", [])[-5:]
            
            tasks_list.append(task_info)
        
        return {
            "success": True,
            "tasks": tasks_list,
            "count": len(tasks_list)
        }
    
    async def run_now(self, task_id: str) -> Dict:
        """Run a task immediately."""
        if task_id not in self.tasks:
            return {"success": False, "error": f"Task not found: {task_id}"}
        
        task = self.tasks[task_id]
        self._execute_task(task_id, task)
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task executed immediately"
        }
    
    async def enable_task(self, task_id: str, enabled: bool = True) -> Dict:
        """Enable or disable a task."""
        if task_id not in self.tasks:
            return {"success": False, "error": f"Task not found: {task_id}"}
        
        self.tasks[task_id]["enabled"] = enabled
        self._save_tasks()
        
        return {
            "success": True,
            "task_id": task_id,
            "enabled": enabled
        }
    
    async def execute(self, action: str, **kwargs) -> Dict:
        """Generic execute method."""
        if action == "schedule_task":
            return await self.schedule_task(
                kwargs.get("goal", ""),
                kwargs.get("schedule_type", "once"),
                kwargs.get("run_at"),
                kwargs.get("interval_minutes"),
                kwargs.get("daily_time"),
                kwargs.get("weekly_day"),
                kwargs.get("enabled", True)
            )
        elif action == "cancel_task":
            return await self.cancel_task(kwargs.get("task_id", ""))
        elif action == "list_tasks":
            return await self.list_tasks(kwargs.get("include_history", False))
        elif action == "run_now":
            return await self.run_now(kwargs.get("task_id", ""))
        elif action == "enable_task":
            return await self.enable_task(
                kwargs.get("task_id", ""),
                kwargs.get("enabled", True)
            )
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
