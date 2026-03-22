#!/usr/bin/env python3
"""
生成中文财经新闻简报
从多个权威新闻源抓取并生成高质量中文新闻摘要
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import feedparser
import requests
from bs4 import BeautifulSoup

# 使用北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 加载.env配置文件
def load_env():
    """加载.env文件中的环境变量"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

# 加载环境变量
load_env()

# OpenAI API配置
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# 国际新闻源配置（RSS feeds）
INTERNATIONAL_SOURCES = {
    "CNBC": {
        "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "name_cn": "美国消费者新闻与商业频道",
        "priority": 1
    },
    "WSJ": {
        "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "name_cn": "华尔街日报",
        "priority": 2
    },
    "MarketWatch": {
        "url": "https://www.marketwatch.com/rss/topstories",
        "name_cn": "市场观察",
        "priority": 3
    },
    "YahooFinance": {
        "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL&region=US&lang=en-US",
        "name_cn": "雅虎财经",
        "priority": 4
    }
}

# 国内新闻源配置
CHINESE_SOURCES = {
    "雪球": {
        "url": "https://xueqiu.com/hots/topic/rss",
        "priority": 1
    },
    "IT之家": {
        "url": "https://www.ithome.com/rss/",
        "priority": 2
    },
    "少数派": {
        "url": "https://sspai.com/feed",
        "priority": 3
    },
    "知乎日报": {
        "url": "https://daily.zhihu.com/feed",
        "priority": 4
    }
}

def translate_text(text, context="news"):
    """使用OpenAI API翻译英文到中文"""
    if not OPENAI_API_KEY or not text:
        return text
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"请将以下英文{'新闻标题' if context == 'title' else '新闻摘要'}翻译成简洁流畅的中文，保持专业性和准确性，不要添加任何解释：\n\n{text}"
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "你是一个专业的财经新闻翻译，擅长将英文财经新闻翻译成通俗易懂的中文。只返回翻译结果，不要添加任何解释或标注。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500 if context == "summary" else 200
        }
        
        response = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        translation = result["choices"][0]["message"]["content"].strip()
        return translation
    except Exception as e:
        print(f"    ⚠️  翻译失败: {str(e)[:50]}")
        return text

def fetch_rss_news(url, source_name, source_name_cn, max_items=4, needs_translation=False):
    """从RSS源获取新闻"""
    news_items = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_items]:
            # 获取内容
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            link = entry.get("link", "")
            
            # 清理HTML标签
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                summary = soup.get_text()[:300]
            
            # 翻译英文内容
            title_cn = None
            summary_cn = None
            
            if needs_translation and OPENAI_API_KEY:
                print(f"    🔄 正在翻译: {title[:50]}...")
                title_cn = translate_text(title, "title")
                summary_cn = translate_text(summary, "summary")
            
            news_items.append({
                "title": title_cn if title_cn else title,
                "title_en": title if needs_translation else None,
                "url": link,
                "source": source_name_cn if source_name_cn else source_name,
                "source_en": source_name if needs_translation else None,
                "summary": summary_cn if summary_cn else summary,
                "summary_en": summary if needs_translation else None,
                "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
            })
            
        print(f"  ✅ {source_name_cn or source_name}: {len(news_items)} 条")
    except Exception as e:
        print(f"  ❌ {source_name_cn or source_name}: {str(e)}")
    
    return news_items

def classify_importance(title, summary):
    """根据标题和摘要判断新闻重要程度"""
    high_keywords = ["央行", "利率", "降息", "加息", "美联储", "Fed", "ECB", 
                     "利率决议", "货币政策", "降准", "战争", "制裁", "OPEC", 
                     "通胀", "GDP", "衰退", "危机"]
    medium_keywords = ["股市", "油价", "金价", "汇率", "通胀", "GDP", 
                       "就业", "贸易", "关税", "经济数据", "股票", "石油", 
                       "盈利", "财报", "并购", "IPO"]
    
    text = (title + " " + summary).lower()
    
    for keyword in high_keywords:
        if keyword.lower() in text:
            return "high"
    
    for keyword in medium_keywords:
        if keyword.lower() in text:
            return "medium"
    
    return "low"

def generate_analysis(title, summary):
    """生成新闻分析"""
    text = title + " " + summary
    
    if any(k in text for k in ["央行", "利率", "降息", "加息", "美联储", "Fed", "ECB"]):
        return "货币政策变动对全球金融市场有重要影响，投资者应密切关注后续政策走向和相关经济数据。"
    elif any(k in text for k in ["油价", "能源", "石油", "OPEC"]):
        return "能源价格波动影响通胀预期和相关行业成本，需关注OPEC+产量政策及地缘政治因素。"
    elif any(k in text for k in ["股市", "市场", "股票", "指数"]):
        return "市场情绪受多重因素影响，建议投资者保持理性，关注基本面和长期趋势。"
    elif any(k in text for k in ["通胀", "CPI", "物价"]):
        return "通胀数据是央行货币政策的重要参考指标，将直接影响利率决策和市场预期。"
    elif any(k in text for k in ["就业", "非农", "失业"]):
        return "就业数据反映经济健康状况，将影响美联储政策立场和市场风险偏好。"
    elif any(k in text for k in ["贸易", "关税", "进出口"]):
        return "贸易政策变化将影响相关行业和企业盈利，需关注对供应链和成本的影响。"
    elif any(k in text for k in ["科技", "AI", "人工智能"]):
        return "科技发展推动产业升级，相关领域投资机会值得关注，但需评估估值风险。"
    else:
        return "该新闻值得关注，建议持续跟踪相关动态以评估对投资组合的潜在影响。"

def extract_tags(title, summary):
    """从标题和摘要中提取标签"""
    text = title + " " + summary
    tags = []
    
    tag_keywords = {
        "美联储": ["美联储", "Fed", "联邦储备"],
        "利率": ["利率", "降息", "加息"],
        "通胀": ["通胀", "CPI", "物价"],
        "股市": ["股市", "股票", "指数", "A股", "美股"],
        "油价": ["油价", "原油", "石油", "OPEC"],
        "汇率": ["汇率", "人民币", "美元", "欧元"],
        "就业": ["就业", "非农", "失业率"],
        "贸易": ["贸易", "关税", "进出口"],
        "科技": ["科技", "AI", "人工智能", "芯片"],
        "加密货币": ["比特币", "加密货币", "区块链"],
        "房地产": ["房地产", "楼市", "房价"],
        "银行": ["银行", "信贷", "贷款"]
    }
    
    for tag, keywords in tag_keywords.items():
        if any(k in text for k in keywords):
            tags.append(tag)
    
    return tags[:3] if tags else ["财经"]

def generate_chinese_news():
    """
    生成中文新闻数据
    从多个RSS源抓取新闻
    """
    today = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    all_news = []
    news_id = 1
    
    print("📡 开始抓取国际新闻...")
    # 获取国际新闻
    for source_name, config in INTERNATIONAL_SOURCES.items():
        items = fetch_rss_news(
            config["url"], 
            source_name, 
            config["name_cn"],
            max_items=4,
            needs_translation=True  # 国际新闻需要翻译
        )
        for item in items:
            item["id"] = news_id
            item["importance"] = classify_importance(item["title"], item["summary"])
            item["analysis"] = generate_analysis(item["title"], item["summary"])
            item["tags"] = extract_tags(item["title"], item["summary"])
            all_news.append(item)
            news_id += 1
    
    print("\n📡 开始抓取国内新闻...")
    # 获取国内新闻
    for source_name, config in CHINESE_SOURCES.items():
        items = fetch_rss_news(
            config["url"], 
            source_name, 
            None,
            max_items=4,
            needs_translation=False  # 国内新闻不需要翻译
        )
        for item in items:
            item["id"] = news_id
            item["importance"] = classify_importance(item["title"], item["summary"])
            item["analysis"] = generate_analysis(item["title"], item["summary"])
            item["tags"] = extract_tags(item["title"], item["summary"])
            all_news.append(item)
            news_id += 1
    
    # 按重要程度排序
    importance_order = {"high": 0, "medium": 1, "low": 2}
    all_news.sort(key=lambda x: importance_order.get(x["importance"], 2))
    
    # 重新编号
    for i, item in enumerate(all_news, 1):
        item["id"] = i
    
    return all_news

def main():
    """主函数"""
    print("🦞 小龙虾开始生成中文新闻简报...")
    
    # 生成新闻数据
    news_items = generate_chinese_news()
    
    # 保存数据
    today = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 保存今日新闻
    news_file = data_dir / f"{today}.json"
    with open(news_file, "w", encoding="utf-8") as f:
        json.dump(news_items, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {len(news_items)} 条新闻到 {news_file}")
    
    # 更新索引
    index_file = data_dir / "index.json"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"availableDates": []}
    
    index["latestDate"] = today
    if today not in index["availableDates"]:
        index["availableDates"].append(today)
        index["availableDates"].sort(reverse=True)
    
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"✅ 已更新索引文件")

if __name__ == "__main__":
    main()
