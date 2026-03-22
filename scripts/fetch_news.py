#!/usr/bin/env python3
"""
每日财经新闻抓取脚本
从多个新闻源抓取财经新闻，并生成结构化数据
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

# OpenAI API配置
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# 新闻源配置（RSS feeds）
NEWS_SOURCES = {
    "Reuters": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/bloomberg-markets.xml",
    "CNBC": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
}

# 国内新闻源
CN_SOURCES = {
    "新浪财经": "https://feedx.net/rss/sina/finance.xml",
    "东方财富": "https://feedx.net/rss/eastmoney.xml",
}

def translate_to_chinese(text, context="news"):
    """使用OpenAI API翻译英文到中文"""
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY not set, skipping translation")
        return text
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"请将以下英文{'新闻标题' if context == 'title' else '新闻摘要'}翻译成简洁流畅的中文，保持专业性和准确性：\n\n{text}"
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "你是一个专业的财经新闻翻译，擅长将英文财经新闻翻译成通俗易懂的中文。"},
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
        print(f"Translation error: {e}")
        return text

def fetch_rss_news(url, source_name, max_items=5):
    """从RSS源获取新闻"""
    news_items = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_items]:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))[:300]
            
            # 判断是否需要翻译（英文新闻源）
            needs_translation = source_name in ["Reuters", "Bloomberg", "CNBC"]
            
            item = {
                "title": title,
                "title_cn": translate_to_chinese(title, "title") if needs_translation else title,
                "url": entry.get("link", ""),
                "source": source_name,
                "summary": summary,
                "summary_cn": translate_to_chinese(summary, "summary") if needs_translation else summary,
                "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
            }
            news_items.append(item)
    except Exception as e:
        print(f"Error fetching from {source_name}: {e}")
    return news_items

def classify_importance(title, summary):
    """根据标题和摘要判断新闻重要程度"""
    high_keywords = ["央行", "利率", "降息", "加息", "美联储", "ECB", "fed", "Fed",
                     "利率决议", "货币政策", "降准", "战争", "制裁", "OPEC", "通胀"]
    medium_keywords = ["股市", "油价", "金价", "汇率", "通胀", "GDP", 
                       "就业", "贸易", "关税", "经济数据", "股票", "石油", "就业"]
    
    text = (title + " " + summary).lower()
    
    for keyword in high_keywords:
        if keyword.lower() in text:
            return "high"
    
    for keyword in medium_keywords:
        if keyword.lower() in text:
            return "medium"
    
    return "low"

def generate_analysis(title, summary, title_cn=None):
    """生成新闻分析（中文）"""
    # 使用中文标题（如果有）进行分析
    text = title_cn if title_cn else title
    
    if "央行" in text or "利率" in text or "降息" in text or "加息" in text or "美联储" in text or "Fed" in text:
        return "货币政策变动对全球金融市场有重要影响，投资者应密切关注后续政策走向和相关经济数据。"
    elif "油价" in text or "能源" in text or "石油" in text:
        return "能源价格波动影响通胀预期和相关行业成本，需关注OPEC+产量政策及地缘政治因素。"
    elif "股市" in text or "市场" in text or "股票" in text:
        return "市场情绪受多重因素影响，建议投资者保持理性，关注基本面和长期趋势。"
    elif "通胀" in text or "CPI" in text:
        return "通胀数据是央行货币政策的重要参考指标，将直接影响利率决策和市场预期。"
    elif "就业" in text or "非农" in text or "失业" in text:
        return "就业数据反映经济健康状况，将影响美联储政策立场和市场风险偏好。"
    else:
        return "该新闻值得关注，建议持续跟踪相关动态以评估对投资组合的潜在影响。"

def main():
    """主函数"""
    all_news = []
    news_id = 1
    
    # 获取国际新闻
    for source_name, url in NEWS_SOURCES.items():
        print(f"Fetching from {source_name}...")
        items = fetch_rss_news(url, source_name)
        for item in items:
            item["id"] = news_id
            item["importance"] = classify_importance(item["title_cn"], item["summary_cn"])
            item["analysis"] = generate_analysis(item["title"], item["summary"], item.get("title_cn"))
            all_news.append(item)
            news_id += 1
    
    # 获取国内新闻
    for source_name, url in CN_SOURCES.items():
        print(f"Fetching from {source_name}...")
        items = fetch_rss_news(url, source_name)
        for item in items:
            item["id"] = news_id
            item["importance"] = classify_importance(item["title"], item["summary"])
            item["analysis"] = generate_analysis(item["title"], item["summary"])
            all_news.append(item)
            news_id += 1
    
    # 按重要程度排序
    importance_order = {"high": 0, "medium": 1, "low": 2}
    all_news.sort(key=lambda x: importance_order.get(x["importance"], 2))
    
    # 保存数据
    today = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 保存今日新闻
    news_file = data_dir / f"{today}.json"
    with open(news_file, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_news)} news items to {news_file}")
    
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
    print(f"Updated index file")

if __name__ == "__main__":
    main()
