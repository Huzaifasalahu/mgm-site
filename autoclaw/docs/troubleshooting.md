# AutoClaw Troubleshooting Guide

## Common Issues

### 1. Application Won't Start

**Symptoms**: Double-clicking does nothing, or immediate crash

**Solutions**:
- Check Python installation: `python --version`
- Verify dependencies: `pip install -r requirements.txt`
- Run from terminal to see errors: `python main.py`
- Check for PyQt5: `pip show PyQt5`

### 2. LLM API Errors

**Symptoms**: "API key not configured" or authentication failures

**Solutions**:
1. Go to Settings tab
2. Enter valid API key for your provider
3. Verify API key has sufficient credits
4. Check API endpoint URL if using custom provider

### 3. Browser Automation Fails

**Symptoms**: "Browser not found" or connection errors

**Solutions**:
```bash
# Install Playwright browsers
playwright install chromium

# Or install Pyppeteer browser
pyppeteer-install

# On Linux, install dependencies
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libcairo-1.0-0
```

### 4. Memory Issues

**Symptoms**: High RAM usage, slow performance

**Solutions**:
- Clear memory from Memory tab
- Reduce memory limit in settings
- Restart application periodically
- Check for memory leaks in logs

### 5. File Access Errors

**Symptoms**: Permission denied when reading/writing files

**Solutions**:
- Run as administrator (Windows) or with sudo (Linux/macOS)
- Check file permissions
- Ensure target directories exist
- Verify antivirus isn't blocking access

### 6. Scheduler Not Running

**Symptoms**: Scheduled tasks don't execute

**Solutions**:
- Keep application running (don't close)
- Check system tray for background process
- Verify task is enabled in Scheduler tab
- Review execution history for errors

### 7. Messaging Integration Fails

**Symptoms**: Messages not sent to Slack/Telegram/Feishu

**Solutions**:
1. Verify webhook URLs are correct
2. Check network connectivity
3. Test webhook manually with curl
4. Review firewall settings

## Log Files

AutoClaw logs are stored in:
- **Windows**: `%APPDATA%\AutoClaw\logs\`
- **macOS**: `~/Library/Logs/AutoClaw/`
- **Linux**: `~/.local/share/AutoClaw/logs/`

## Getting Help

1. Check documentation: `/docs/` folder
2. Review architecture: `architecture.md`
3. Search existing issues on GitHub
4. Create new issue with:
   - OS version
   - Python version
   - Error messages
   - Steps to reproduce

## Performance Tips

1. Use local LLM (Ollama) for faster response
2. Limit concurrent tasks
3. Regularly clear memory
4. Disable unused skills
5. Use SSD for storage
