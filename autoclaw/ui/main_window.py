"""
AutoClaw - Autonomous AI Agent Platform
Main Window GUI (PyQt5)

Provides a graphical interface for all AutoClaw interactions.
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                             QLabel, QTabWidget, QComboBox, QGroupBox, 
                             QFormLayout, QSpinBox, QFileDialog, QMessageBox,
                             QProgressBar, QListWidget, QListWidgetItem, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon

class MessageSignal(QObject):
    """Signal for thread-safe message updates."""
    new_message = pyqtSignal(str)
    task_complete = pyqtSignal(str)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, agent, config, app_instance):
        super().__init__()
        
        self.agent = agent
        self.config = config
        self.app_instance = app_instance
        
        self.message_signal = MessageSignal()
        self.message_signal.new_message.connect(self._append_chat)
        self.message_signal.task_complete.connect(self._task_complete)
        
        self.setWindowTitle("🦞 AutoClaw - Autonomous AI Agent")
        self.setMinimumSize(1200, 800)
        
        self._init_ui()
        self._load_config_to_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self._create_chat_tab()
        self._create_skills_tab()
        self._create_scheduler_tab()
        self._create_memory_tab()
        self._create_settings_tab()
    
    def _create_chat_tab(self):
        """Create the chat/task execution tab."""
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 10))
        self.chat_display.append("👋 Welcome to AutoClaw! Enter a goal below to get started.")
        layout.addWidget(self.chat_display)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("Enter your goal (e.g., 'Search for Python tutorials and save them')...")
        self.goal_input.returnPressed.connect(self._execute_goal)
        input_layout.addWidget(self.goal_input)
        
        send_btn = QPushButton("🚀 Execute")
        send_btn.clicked.connect(self._execute_goal)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        self.tabs.addTab(chat_widget, "💬 Chat")
    
    def _create_skills_tab(self):
        """Create the skills management tab."""
        skills_widget = QWidget()
        layout = QVBoxLayout(skills_widget)
        
        # Skills list
        skills_group = QGroupBox("Available Skills")
        skills_layout = QVBoxLayout(skills_group)
        
        self.skills_list = QListWidget()
        skills_layout.addWidget(self.skills_list)
        
        # Load skills
        from skills import SkillLoader
        loader = SkillLoader(self.app_instance.skills_dir)
        skills = loader.load_skills()
        
        for skill in skills:
            item = QListWidgetItem(f"📦 {skill.get('name', 'Unknown')}")
            item.setToolTip(skill.get('description', ''))
            self.skills_list.addItem(item)
        
        layout.addWidget(skills_group)
        
        # Skill store button
        store_btn = QPushButton("🌐 Browse Skill Store")
        store_btn.clicked.connect(self._open_skill_store)
        layout.addWidget(store_btn)
        
        self.tabs.addTab(skills_widget, "🛠️ Skills")
    
    def _create_scheduler_tab(self):
        """Create the task scheduler tab."""
        scheduler_widget = QWidget()
        layout = QVBoxLayout(scheduler_widget)
        
        # Schedule form
        form_group = QGroupBox("Schedule New Task")
        form_layout = QFormLayout(form_group)
        
        self.schedule_goal = QLineEdit()
        form_layout.addRow("Goal:", self.schedule_goal)
        
        self.schedule_type = QComboBox()
        self.schedule_type.addItems(["Once", "Interval", "Daily", "Weekly"])
        form_layout.addRow("Type:", self.schedule_type)
        
        self.schedule_time = QLineEdit("09:00")
        form_layout.addRow("Time (HH:MM):", self.schedule_time)
        
        schedule_btn = QPushButton("📅 Schedule Task")
        schedule_btn.clicked.connect(self._schedule_task)
        layout.addWidget(form_group)
        layout.addWidget(schedule_btn)
        
        # Scheduled tasks list
        tasks_group = QGroupBox("Scheduled Tasks")
        tasks_layout = QVBoxLayout(tasks_group)
        
        self.scheduled_tasks_list = QListWidget()
        tasks_layout.addWidget(self.scheduled_tasks_list)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_scheduled_tasks)
        tasks_layout.addWidget(refresh_btn)
        
        layout.addWidget(tasks_group)
        
        self.tabs.addTab(scheduler_widget, "📅 Scheduler")
    
    def _create_memory_tab(self):
        """Create the memory viewer tab."""
        memory_widget = QWidget()
        layout = QVBoxLayout(memory_widget)
        
        # Memory search
        search_layout = QHBoxLayout()
        
        self.memory_search = QLineEdit()
        self.memory_search.setPlaceholderText("Search memories...")
        search_layout.addWidget(self.memory_search)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self._search_memories)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Memory display
        self.memory_display = QTextEdit()
        self.memory_display.setReadOnly(True)
        layout.addWidget(self.memory_display)
        
        # Stats
        self.memory_stats = QLabel("Memories: 0 | Feedback entries: 0")
        layout.addWidget(self.memory_stats)
        
        self._update_memory_stats()
        
        self.tabs.addTab(memory_widget, "🧠 Memory")
    
    def _create_settings_tab(self):
        """Create the settings/configuration tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # LLM Settings
        llm_group = QGroupBox("LLM Configuration")
        llm_layout = QFormLayout(llm_group)
        
        self.llm_provider = QComboBox()
        self.llm_provider.addItems(["openai", "anthropic", "google", "deepseek", "ollama", "custom"])
        llm_layout.addRow("Provider:", self.llm_provider)
        
        self.llm_model = QLineEdit("gpt-4o")
        llm_layout.addRow("Model:", self.llm_model)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        llm_layout.addRow("API Key:", self.api_key_input)
        
        self.api_base_input = QLineEdit()
        llm_layout.addRow("API Base (optional):", self.api_base_input)
        
        layout.addWidget(llm_group)
        
        # Messaging Settings
        msg_group = QGroupBox("Messaging Integration")
        msg_layout = QFormLayout(msg_group)
        
        self.feishu_webhook = QLineEdit()
        msg_layout.addRow("Feishu Webhook:", self.feishu_webhook)
        
        self.slack_webhook = QLineEdit()
        msg_layout.addRow("Slack Webhook:", self.slack_webhook)
        
        self.telegram_token = QLineEdit()
        self.telegram_token.setEchoMode(QLineEdit.Password)
        msg_layout.addRow("Telegram Token:", self.telegram_token)
        
        layout.addWidget(msg_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Configuration")
        save_btn.clicked.connect(self._save_configuration)
        layout.addWidget(save_btn)
        
        # Token usage
        self.token_usage_label = QLabel("Token Usage: N/A")
        layout.addWidget(self.token_usage_label)
        
        self.tabs.addTab(settings_widget, "⚙️ Settings")
    
    def _load_config_to_ui(self):
        """Load configuration into UI elements."""
        self.llm_provider.setCurrentText(self.config.get("llm_provider", "openai"))
        self.llm_model.setText(self.config.get("llm_model", "gpt-4o"))
        self.api_key_input.setText(self.config.get("api_key", ""))
        self.api_base_input.setText(self.config.get("api_base", "") or "")
        
        msg_config = self.config.get("messaging", {})
        self.feishu_webhook.setText(msg_config.get("feishu_webhook", ""))
        self.slack_webhook.setText(msg_config.get("slack_webhook", ""))
        self.telegram_token.setText(msg_config.get("telegram_bot_token", ""))
    
    def _save_configuration(self):
        """Save configuration from UI."""
        self.config["llm_provider"] = self.llm_provider.currentText()
        self.config["llm_model"] = self.llm_model.text()
        self.config["api_key"] = self.api_key_input.text()
        self.config["api_base"] = self.api_base_input.text() or None
        
        self.config["messaging"] = {
            "feishu_webhook": self.feishu_webhook.text(),
            "slack_webhook": self.slack_webhook.text(),
            "telegram_bot_token": self.telegram_token.text()
        }
        
        self.app_instance.save_config()
        
        # Update agent config
        if self.agent:
            self.agent.update_config(self.config)
        
        QMessageBox.information(self, "Configuration Saved", 
                               "Settings have been saved successfully!")
    
    def _execute_goal(self):
        """Execute the goal entered in chat."""
        goal = self.goal_input.text().strip()
        if not goal:
            return
        
        self._append_chat(f"\n👤 You: {goal}")
        self.goal_input.clear()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Execute asynchronously
        import asyncio
        asyncio.run_coroutine_threadsafe(
            self._run_goal(goal),
            asyncio.get_event_loop()
        )
    
    async def _run_goal(self, goal: str):
        """Run goal execution in background."""
        try:
            result = await self.agent.execute_goal(goal)
            self.message_signal.task_complete.emit(result)
        except Exception as e:
            self.message_signal.task_complete.emit(f"❌ Error: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def _task_complete(self, result: str):
        """Handle task completion."""
        self._append_chat(f"\n🤖 AutoClaw: {result}")
        self._update_memory_stats()
    
    def _append_chat(self, text: str):
        """Append text to chat display."""
        self.chat_display.append(text)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def _schedule_task(self):
        """Schedule a new task."""
        goal = self.schedule_goal.text().strip()
        if not goal:
            QMessageBox.warning(self, "Warning", "Please enter a goal")
            return
        
        schedule_type = self.schedule_type.currentText().lower()
        time_str = self.schedule_time.text().strip()
        
        import asyncio
        from datetime import datetime
        
        # Simple scheduling logic
        if schedule_type == "once":
            run_at = f"{datetime.now().strftime('%Y-%m-%d')} {time_str}:00"
        else:
            run_at = None
        
        asyncio.run_coroutine_threadsafe(
            self.agent.tool_manager.execute_tool("scheduler", {
                "action": "schedule_task",
                "goal": goal,
                "schedule_type": schedule_type,
                "daily_time": time_str if schedule_type == "daily" else None
            }),
            asyncio.get_event_loop()
        )
        
        QMessageBox.information(self, "Task Scheduled", f"Task '{goal}' has been scheduled!")
        self._refresh_scheduled_tasks()
    
    def _refresh_scheduled_tasks(self):
        """Refresh the scheduled tasks list."""
        self.scheduled_tasks_list.clear()
        self.scheduled_tasks_list.addItem("Loading tasks...")
        # Would fetch actual tasks here
    
    def _search_memories(self):
        """Search memories."""
        query = self.memory_search.text().strip()
        if not query:
            return
        
        self.memory_display.append(f"🔍 Searching for: {query}\n")
        # Would perform actual search here
    
    def _update_memory_stats(self):
        """Update memory statistics display."""
        # Would fetch actual stats here
        self.memory_stats.setText("Memories: Loading... | Feedback: Loading...")
    
    def _open_skill_store(self):
        """Open the skill store browser."""
        QMessageBox.information(self, "Skill Store", 
                               "Skill Store feature coming soon!\n\n"
                               "Browse and install community-contributed skills.")


def run_gui(agent, config, app_instance):
    """Run the GUI application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow(agent, config, app_instance)
    window.show()
    
    sys.exit(app.exec_())
