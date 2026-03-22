# 本地新闻自动更新设置指南

## 🎯 方案说明

完全在本地处理，然后推送到GitHub：
1. ✅ 在你的Mac mini上运行脚本
2. ✅ 抓取新闻 -> AI翻译 -> 生成中文内容
3. ✅ 自动推送到GitHub
4. ✅ 无需GitHub Action参与翻译

## 📦 快速开始

### 第一步：配置OpenAI API Key

```bash
cd /Users/glenman/.openclaw/workspace/daily-finance-news

# 复制配置文件模板
cp .env.example .env

# 编辑配置文件
nano .env
```

在 `.env` 文件中填入你的API Key：
```
OPENAI_API_KEY=sk-xxxx你的密钥xxxx
```

保存并退出（Ctrl+O, Enter, Ctrl+X）

### 第二步：运行设置脚本

```bash
# 给脚本添加执行权限
chmod +x setup_local.sh

# 运行设置脚本
./setup_local.sh
```

设置脚本会：
- ✅ 检查配置
- ✅ 测试运行
- ✅ 设置定时任务（每天早上6点）

### 第三步：验证

```bash
# 手动测试一次
bash scripts/update_news.sh

# 查看日志
tail -f /tmp/news_update.log
```

## ⏰ 定时任务管理

### 查看任务状态
```bash
launchctl list | grep news
```

### 查看日志
```bash
# 实时查看日志
tail -f /tmp/news_update.log

# 查看错误日志
tail -f /tmp/news_update_error.log
```

### 停止定时任务
```bash
launchctl unload ~/Library/LaunchAgents/com.daily.news.update.plist
```

### 启动定时任务
```bash
launchctl load ~/Library/LaunchAgents/com.daily.news.update.plist
```

### 立即运行一次
```bash
cd /Users/glenman/.openclaw/workspace/daily-finance-news
bash scripts/update_news.sh
```

## 🔧 手动设置（如果自动设置失败）

### 1. 创建launchd配置文件

```bash
nano ~/Library/LaunchAgents/com.daily.news.update.plist
```

粘贴以下内容（记得替换路径和API Key）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.daily.news.update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/glenman/.openclaw/workspace/daily-finance-news/scripts/update_news.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/glenman/.openclaw/workspace/daily-finance-news</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OPENAI_API_KEY</key>
        <string>你的API密钥</string>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/news_update.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/news_update_error.log</string>
</dict>
</plist>
```

### 2. 加载任务

```bash
launchctl load ~/Library/LaunchAgents/com.daily.news.update.plist
```

## 🌐 访问网站

更新完成后，访问：
https://glenman.github.io/daily-finance-news/

## 💰 成本说明

使用OpenAI API翻译：
- 模型: GPT-3.5-turbo
- 每条新闻: 约0.001-0.002美元
- 每天24条: 约0.024-0.048美元
- 每月: 约0.72-1.44美元

## 🔒 安全说明

- ✅ `.env` 文件已添加到 `.gitignore`，不会提交到Git
- ✅ API Key仅存储在本地
- ✅ launchd配置文件也在本地，不会上传到GitHub

## 📊 新闻源配置

### 国际新闻源（自动翻译）
1. CNBC - 美国消费者新闻与商业频道
2. 华尔街日报
3. 市场观察
4. 雅虎财经

### 国内新闻源（中文原文）
1. 雪球
2. IT之家
3. 少数派
4. 知乎日报

## 🆘 常见问题

**Q: 定时任务没有运行？**
A: 检查Mac mini是否在早上6点开机，查看日志 `/tmp/news_update_error.log`

**Q: 翻译失败？**
A: 检查 `.env` 文件中的API Key是否正确，检查OpenAI账户余额

**Q: 推送到GitHub失败？**
A: 检查网络连接，确保有push权限

**Q: 想要立即更新新闻？**
A: 运行 `bash scripts/update_news.sh`

## 🔄 GitHub Action说明

GitHub Action仍然配置为每天早上6点运行，但：
- ⚠️ 不会进行翻译（没有API Key）
- ⚠️ 仅作为备用方案
- ✅ 主要依赖本地定时任务

建议保持GitHub Action配置，作为本地任务的备份。
