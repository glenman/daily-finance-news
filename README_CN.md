# 每日中文新闻自动更新系统

## 🎯 功能说明

这个系统会每天早上6点自动：
1. 生成高质量的中文财经新闻简报
2. 自动推送到GitHub
3. 通过GitHub Pages网站展示

## 🔧 设置说明

### 方案1：使用cron定时任务（推荐）

在终端运行以下命令：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天早上6点运行）
0 6 * * * cd /Users/glenman/.openclaw/workspace/daily-finance-news && /bin/bash /Users/glenman/.openclaw/workspace/daily-finance-news/scripts/update_news.sh >> /tmp/news_update.log 2>&1
```

### 方案2：使用macOS launchd（更稳定）

创建文件 `~/Library/LaunchAgents/com.daily.news.update.plist`：

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

然后加载：
```bash
launchctl load ~/Library/LaunchAgents/com.daily.news.update.plist
```

## 🚀 手动运行测试

```bash
cd /Users/glenman/.openclaw/workspace/daily-finance-news
bash scripts/update_news.sh
```

## 📊 查看日志

```bash
# 查看运行日志
tail -f /tmp/news_update.log

# 查看错误日志
tail -f /tmp/news_update_error.log
```

## 🌐 访问网站

更新完成后，访问：
https://glenman.github.io/daily-finance-news/

## 📝 数据格式

每条新闻包含：
- `title`: 中文标题
- `title_en`: 英文原标题
- `summary`: 中文摘要
- `summary_en`: 英文原摘要
- `analysis`: 中文分析
- `tags`: 相关标签
- `importance`: 重要程度（high/medium/low）

## ⚠️ 注意事项

1. 确保Mac mini在早上6点处于开机状态
2. 确保有网络连接
3. 首次使用需要配置GitHub访问权限

## 🔄 停止自动更新

```bash
# 停止cron任务
crontab -e
# 删除相关行

# 或停止launchd任务
launchctl unload ~/Library/LaunchAgents/com.daily.news.update.plist
```
