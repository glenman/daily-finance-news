# 每日财经新闻概览

📰 每日自动更新的国际财经新闻聚合网站

## 功能特点

- ✅ 每日 6:00 (北京时间) 自动更新
- ✅ 支持按日期筛选
- ✅ 支持关键词搜索
- ✅ 支持按重要程度筛选
- ✅ 移动端友好设计
- ✅ 包含新闻综述分析

## 访问地址

🔗 [https://glenman.github.io/daily-finance-news](https://glenman.github.io/daily-finance-news)

## 新闻来源

### 国际
- Reuters
- Bloomberg
- CNBC

### 国内
- 新浪财经
- 东方财富

## 本地开发

```bash
# 克隆仓库
git clone https://github.com/glenman/daily-finance-news.git
cd daily-finance-news

# 本地运行（可以用任意静态服务器）
python -m http.server 8000
# 然后访问 http://localhost:8000
```

## 自动更新

项目使用 GitHub Actions 实现每日自动抓取新闻：
- 运行时间：每天北京时间 6:00
- 配置文件：`.github/workflows/daily-news.yml`

## 技术栈

- 前端：纯 HTML/CSS/JavaScript
- 数据存储：JSON 文件
- 自动化：GitHub Actions + Python
- 部署：GitHub Pages
