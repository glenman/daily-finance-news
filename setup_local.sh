#!/bin/bash
# 本地新闻自动更新设置脚本

echo "🦞 小龙虾本地新闻自动更新设置"
echo "================================"
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "📝 创建配置文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo ""
    echo "⚠️  请编辑 .env 文件，填入你的 OpenAI API Key："
    echo "   OPENAI_API_KEY=sk-xxxx..."
    echo ""
    echo "配置完成后，重新运行此脚本。"
    exit 0
fi

# 检查API Key是否配置
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-api-key-here" ]; then
    echo "❌ 错误: 请先在 .env 文件中配置 OPENAI_API_KEY"
    exit 1
fi

echo "✅ API Key已配置"
echo ""

# 测试运行
echo "🧪 测试运行..."
python3 scripts/generate_chinese_news.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 测试成功！"
    echo ""
    echo "⏰  设置定时任务..."
    
    # 创建launchd plist
    cat > ~/Library/LaunchAgents/com.daily.news.update.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.daily.news.update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>__PROJECT_DIR__/scripts/update_news.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>__PROJECT_DIR__</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OPENAI_API_KEY</key>
        <string>__API_KEY__</string>
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
EOF

    # 替换变量
    PROJECT_DIR=$(pwd)
    sed -i '' "s|__PROJECT_DIR__|$PROJECT_DIR|g" ~/Library/LaunchAgents/com.daily.news.update.plist
    sed -i '' "s|__API_KEY__|$OPENAI_API_KEY|g" ~/Library/LaunchAgents/com.daily.news.update.plist
    
    # 加载任务
    launchctl unload ~/Library/LaunchAgents/com.daily.news.update.plist 2>/dev/null
    launchctl load ~/Library/LaunchAgents/com.daily.news.update.plist
    
    echo "✅ 定时任务已设置"
    echo ""
    echo "📅 每天早上 6:00 自动运行"
    echo "📝 日志文件: /tmp/news_update.log"
    echo ""
    echo "🔍 查看日志: tail -f /tmp/news_update.log"
    echo "⏹️  停止任务: launchctl unload ~/Library/LaunchAgents/com.daily.news.update.plist"
    echo "▶️  启动任务: launchctl load ~/Library/LaunchAgents/com.daily.news.update.plist"
else
    echo ""
    echo "❌ 测试失败，请检查配置"
    exit 1
fi
