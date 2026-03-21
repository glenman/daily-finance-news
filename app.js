let allNews = [];

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 设置默认日期为今天
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('dateFilter').value = today;
    
    loadNews();
});

// 加载新闻数据
async function loadNews() {
    const loading = document.getElementById('loading');
    const container = document.getElementById('newsContainer');
    
    try {
        // 尝试加载今天的新闻
        const today = new Date().toISOString().split('T')[0];
        const response = await fetch(`data/${today}.json`);
        
        if (response.ok) {
            allNews = await response.json();
        } else {
            // 如果今天没有，尝试加载最近的数据
            const indexResponse = await fetch('data/index.json');
            if (indexResponse.ok) {
                const index = await indexResponse.json();
                if (index.latestDate) {
                    const latestResponse = await fetch(`data/${index.latestDate}.json`);
                    if (latestResponse.ok) {
                        allNews = await latestResponse.json();
                        document.getElementById('dateFilter').value = index.latestDate;
                    }
                }
            }
        }
        
        displayNews(allNews);
    } catch (error) {
        console.log('加载新闻数据:', error);
        // 显示示例数据
        loadSampleData();
    }
    
    loading.style.display = 'none';
}

// 加载示例数据
function loadSampleData() {
    allNews = [
        {
            id: 1,
            title: "美联储维持利率不变，暗示年内可能降息",
            date: new Date().toISOString().split('T')[0],
            source: "Reuters",
            url: "https://example.com/news1",
            summary: "美联储在最新政策会议上决定维持基准利率不变，但暗示如果通胀持续降温，年内可能会开始降息。",
            importance: "high",
            analysis: "这一决定符合市场预期。维持利率不变为经济提供了稳定性，而降息预期则支撑了股市情绪。投资者应关注后续通胀数据和美联储官员讲话。"
        },
        {
            id: 2,
            title: "中国央行降准0.5个百分点，释放长期资金约1万亿元",
            date: new Date().toISOString().split('T')[0],
            source: "新华社",
            url: "https://example.com/news2",
            summary: "中国人民银行宣布下调金融机构存款准备金率0.5个百分点，预计将释放长期资金约1万亿元人民币。",
            importance: "high",
            analysis: "此次降准显示了央行稳增长的决心，有助于降低银行资金成本，支持实体经济发展。对A股市场形成利好。"
        },
        {
            id: 3,
            title: "欧洲央行维持三大关键利率不变",
            date: new Date().toISOString().split('T')[0],
            source: "Bloomberg",
            url: "https://example.com/news3",
            summary: "欧洲央行在最新会议上决定维持主要再融资利率、边际借贷利率和存款机制利率不变。",
            importance: "medium",
            analysis: "欧洲央行继续保持观望态度，等待更多通胀数据。市场预期首次降息可能在6月份。"
        }
    ];
    
    displayNews(allNews);
}

// 显示新闻
function displayNews(news) {
    const container = document.getElementById('newsContainer');
    const noResults = document.getElementById('noResults');
    const stats = document.getElementById('stats');
    
    if (news.length === 0) {
        container.innerHTML = '';
        noResults.style.display = 'block';
        stats.innerHTML = '';
        return;
    }
    
    noResults.style.display = 'none';
    
    // 统计信息
    const highCount = news.filter(n => n.importance === 'high').length;
    const mediumCount = news.filter(n => n.importance === 'medium').length;
    const lowCount = news.filter(n => n.importance === 'low').length;
    stats.innerHTML = `共 <strong>${news.length}</strong> 条新闻 | 🔴 高 ${highCount} | 🟡 中 ${mediumCount} | 🟢 低 ${lowCount}`;
    
    // 按重要程度排序
    const sortedNews = [...news].sort((a, b) => {
        const order = { high: 0, medium: 1, low: 2 };
        return order[a.importance] - order[b.importance];
    });
    
    container.innerHTML = sortedNews.map(item => `
        <article class="news-card">
            <div class="news-header">
                <span class="importance ${item.importance}">${
                    item.importance === 'high' ? '🔴 高重要性' :
                    item.importance === 'medium' ? '🟡 中等' : '🟢 一般'
                }</span>
                <span class="news-date">${formatDate(item.date)}</span>
            </div>
            <h2 class="news-title">${escapeHtml(item.title)}</h2>
            <div class="news-source">来源: <a href="${item.url}" target="_blank" rel="noopener">${escapeHtml(item.source)}</a></div>
            <div class="news-summary">${escapeHtml(item.summary)}</div>
            <div class="news-analysis">
                <div class="analysis-label">📊 综述分析</div>
                ${escapeHtml(item.analysis)}
            </div>
        </article>
    `).join('');
}

// 筛选新闻
async function filterNews() {
    const dateValue = document.getElementById('dateFilter').value;
    const keyword = document.getElementById('keywordSearch').value.trim().toLowerCase();
    const importance = document.getElementById('importanceFilter').value;
    
    // 如果选择了日期，尝试加载该日期的数据
    if (dateValue) {
        try {
            const response = await fetch(`data/${dateValue}.json`);
            if (response.ok) {
                allNews = await response.json();
            }
        } catch (e) {
            console.log('加载指定日期数据失败');
        }
    }
    
    let filtered = allNews;
    
    // 关键词筛选
    if (keyword) {
        filtered = filtered.filter(item => 
            item.title.toLowerCase().includes(keyword) ||
            item.summary.toLowerCase().includes(keyword) ||
            item.analysis.toLowerCase().includes(keyword) ||
            item.source.toLowerCase().includes(keyword)
        );
    }
    
    // 重要程度筛选
    if (importance) {
        filtered = filtered.filter(item => item.importance === importance);
    }
    
    displayNews(filtered);
}

// 重置筛选
function resetFilters() {
    document.getElementById('dateFilter').value = new Date().toISOString().split('T')[0];
    document.getElementById('keywordSearch').value = '';
    document.getElementById('importanceFilter').value = '';
    loadNews();
}

// 格式化日期
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
