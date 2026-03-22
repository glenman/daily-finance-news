#!/bin/bash
# 每日新闻更新脚本
# 由小龙虾AI助手生成中文新闻并推送到GitHub

set -e

# 切换到项目目录
cd "$(dirname "$0")/.."

echo "🦞 小龙虾开始每日新闻更新..."
echo "📅 当前时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 运行Python脚本生成新闻
echo "📝 生成中文新闻..."
python3 scripts/generate_chinese_news.py

# 检查是否有变化
if git diff --quiet data/; then
    echo "ℹ️  没有新的新闻内容，跳过提交"
    exit 0
fi

# 提交并推送
echo "📦 提交更改..."
git add data/
git commit -m "📰 更新中文新闻简报 - $(date '+%Y-%m-%d')" --no-verify

echo "🚀 推送到GitHub..."
git push origin main

echo "✅ 完成！新闻已更新并推送到GitHub"
