#!/usr/bin/env python3
"""
新闻数据保存脚本
由小龙虾AI助手调用，保存生成的中文新闻数据
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

# 使用北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

def save_news_data(news_items):
    """
    保存新闻数据到JSON文件
    
    参数:
        news_items: 新闻列表，每条新闻包含:
            - title: 中文标题
            - title_en: 英文原标题（可选）
            - url: 原文链接
            - source: 来源名称
            - source_en: 来源英文名（可选）
            - summary: 中文摘要
            - summary_en: 英文原摘要（可选）
            - importance: 重要程度 (high/medium/low)
            - analysis: 中文分析
            - tags: 标签列表
    """
    today = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 添加日期和ID
    for i, item in enumerate(news_items, 1):
        item["id"] = i
        item["date"] = today
    
    # 按重要程度排序
    importance_order = {"high": 0, "medium": 1, "low": 2}
    news_items.sort(key=lambda x: importance_order.get(x.get("importance", "low"), 2))
    
    # 重新编号
    for i, item in enumerate(news_items, 1):
        item["id"] = i
    
    # 保存新闻文件
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
    
    return news_file

if __name__ == "__main__":
    # 示例：从命令行参数读取JSON数据
    if len(sys.argv) > 1:
        news_data = json.loads(sys.argv[1])
        save_news_data(news_data)
    else:
        print("用法: python save_news.py '<json_data>'")
        print("示例: python save_news.py '[{\"title\":\"测试新闻\",\"source\":\"测试源\"}]'")
