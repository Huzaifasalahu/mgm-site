# AutoClaw Architecture

## Overview

AutoClaw is an autonomous AI agent platform that implements the Observe-Plan-Act-Learn loop for executing complex tasks.

## Core Components

### 1. Main Application (`main.py`)
Entry point that orchestrates:
- GUI initialization (PyQt5)
- Agent creation
- Skill loading
- Configuration management

### 2. AI Agent (`agent.py`)
Implements the core autonomous loop:

```
┌─────────────┐
│   OBSERVE   │ ← Understand goal, gather context
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    PLAN     │ ← Break goal into steps
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    ACT      │ ← Execute tools/skills
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   LEARN     │ ← Store experience in memory
└─────────────┘
```

### 3. Tool Manager (`tools.py`)
Central registry for all tools:
- Browser Automation
- File Management
- Content Creation
- System Control
- Data Analysis
- Messaging
- Web Search

### 4. Skills (`skills/`)
Modular capabilities:
- `browser_automation.py` - Chromium CDP control
- `file_manager.py` - File I/O operations
- `content_creator.py` - Content generation
- `system_control.py` - OS-level operations
- `data_analyzer.py` - Data processing
- `messenger.py` - IM integration
- `search.py` - Web search
- `memory.py` - Persistent RAG memory
- `schedule.py` - Task scheduling

### 5. User Interface (`ui/`)
PyQt5-based GUI with tabs:
- Chat - Natural language interaction
- Skills - Skill management
- Scheduler - Task scheduling
- Memory - Memory viewer
- Settings - Configuration

## Data Flow

```
User Input → Agent → Tool Selection → Tool Execution → Result → Memory Storage
                 ↑                                           │
                 └──────────── Feedback Loop ────────────────┘
```

## Memory System

### Short-term Memory
- Current session context
- Active task state
- Temporary observations

### Long-term Memory
- Persisted task outcomes
- User feedback
- Skill adaptations
- TF-IDF based retrieval

## Security Considerations

1. **API Keys**: Stored locally in config.json (not encrypted by default)
2. **File Access**: Limited to user directories by default
3. **Browser**: Uses isolated profiles for automation
4. **System Commands**: Executed with user permissions only

## Extensibility

### Adding New Skills
1. Create new file in `skills/` directory
2. Define `SKILL_METADATA` dictionary
3. Implement async methods for actions
4. Register in `tools.py`

### Custom LLM Providers
1. Add provider configuration in `agent.py`
2. Implement API client in `LLMClient` class
3. Update UI dropdown in `main_window.py`

## Performance

- Async I/O for all external operations
- Background threading for scheduler
- Memory-limited to prevent unbounded growth
- Token usage tracking for cost management
