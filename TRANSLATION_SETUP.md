# 新闻自动翻译功能配置说明

## 🌟 功能说明

系统现在支持自动翻译英文新闻为中文：
- ✅ 国际新闻源（CNBC、华尔街日报等）会自动翻译为中文
- ✅ 国内新闻源保持原中文内容
- ✅ 同时保留英文原文供参考

## 🔧 配置OpenAI API Key

### 方法1：GitHub Actions自动运行（推荐）

1. **访问GitHub仓库Secrets设置**：
   https://github.com/glenman/daily-finance-news/settings/secrets/actions

2. **添加OpenAI API Key**：
   - 点击 "New repository secret"
   - **Name**: `OPENAI_API_KEY`
   - **Value**: 你的OpenAI API Key（格式：`sk-xxxx...`）
   - 点击 "Add secret" 保存

3. **完成后，每天早上6点自动运行时会自动翻译英文新闻**

### 方法2：本地运行

在终端设置环境变量：

```bash
# 临时设置（仅当前会话有效）
export OPENAI_API_KEY="sk-xxxx..."

# 永久设置（添加到 ~/.zshrc 或 ~/.bash_profile）
echo 'export OPENAI_API_KEY="sk-xxxx..."' >> ~/.zshrc
source ~/.zshrc

# 运行脚本
cd /Users/glenman/.openclaw/workspace/daily-finance-news
bash scripts/update_news.sh
```

## 📊 当前新闻源配置

### 国际新闻源（自动翻译）
1. **CNBC** - 美国消费者新闻与商业频道 ✅
2. **华尔街日报** ✅
3. **市场观察** ✅
4. **雅虎财经** ✅

### 国内新闻源（中文原文）
1. **雪球** ✅
2. **IT之家** ✅
3. **少数派** ✅
4. **知乎日报** ✅

## 🚫 不使用翻译功能

如果不想使用翻译功能，可以：
1. 不设置 `OPENAI_API_KEY` 环境变量
2. 英文新闻会保留原文显示

## 💰 成本说明

使用OpenAI API翻译：
- **模型**: GPT-3.5-turbo
- **每条新闻**: 约0.001-0.002美元
- **每天20条新闻**: 约0.02-0.04美元
- **每月成本**: 约0.6-1.2美元

非常便宜！比一杯咖啡还便宜 ☕

## 📝 新闻格式示例

```json
{
  "title": "美联储官员暗示今年可能降息",
  "title_en": "Fed Governor Waller urges caution...",
  "summary": "美联储理事沃勒表示...",
  "summary_en": "Waller said in a CNBC interview...",
  "analysis": "货币政策变动对全球金融市场有重要影响...",
  "tags": ["美联储", "利率"]
}
```

## 🔍 测试翻译功能

```bash
# 设置API Key
export OPENAI_API_KEY="sk-xxxx..."

# 运行脚本
cd /Users/glenman/.openclaw/workspace/daily-finance-news
python3 scripts/generate_chinese_news.py

# 查看结果
cat data/$(date +%Y-%m-%d).json | jq '.[0]'
```

## ⚠️ 注意事项

1. **API Key安全**：不要将API Key提交到Git仓库
2. **速率限制**：OpenAI有API调用速率限制，脚本已做优化
3. **翻译质量**：GPT-3.5-turbo翻译质量很高，但偶尔可能需要人工润色
4. **超时设置**：翻译超时时间为30秒，避免长时间等待

## 🆘 常见问题

**Q: 翻译失败怎么办？**
A: 脚本会自动降级为保留原文，不会影响新闻抓取

**Q: 可以使用其他翻译服务吗？**
A: 可以修改 `translate_text()` 函数，接入其他翻译API

**Q: 翻译速度慢怎么办？**
A: 可以减少新闻源数量或使用更快的API服务
