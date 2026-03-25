import streamlit as st
import feedparser
from datetime import datetime
import pandas as pd
import time  # 用于异常等待（可选）

st.set_page_config(page_title="中吉中国新闻监控站", page_icon="🇨🇳", layout="wide")
st.title("🇰🇬 中吉中国新闻实时监控站 v2.1")
st.caption("AKIPRESS • 24.kg • Kaktus • Sputnik • KABAR • KLOOP • VESTI • PRESIDENT • GOV • Вечерний Бишкек • Экономист • BBC Кыргыз | 仅显示与中国相关的最新新闻")

# ================== 全部RSS来源（新增3个） ==================
rss_sources = {
    "AKIPRESS": "https://news.google.com/rss/search?q=site:akipress.org+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "24.kg": "https://news.google.com/rss/search?q=site:24.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "Kaktus.media": "https://news.google.com/rss/search?q=site:kaktus.media+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "Sputnik.kg": "https://news.google.com/rss/search?q=site:sputnik.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "KABAR": "https://news.google.com/rss/search?q=site:kabar.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "KLOOP": "https://news.google.com/rss/search?q=site:kloop.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "VESTI": "https://news.google.com/rss/search?q=site:vesti.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "PRESIDENT.KG": "https://news.google.com/rss/search?q=site:president.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "GOV.KG": "https://news.google.com/rss/search?q=site:gov.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    
    # === 新增3个监测对象 ===
    "Вечерний Бишкек": "https://news.google.com/rss/search?q=site:vb.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "Экономист": "https://news.google.com/rss/search?q=site:economist.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "BBC Кыргыз": "https://news.google.com/rss/search?q=site:bbc.com/kyrgyz+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
}

@st.cache_data(ttl=300)  # 每5分钟自动刷新
def fetch_news():
    all_news = []
    for source, url in rss_sources.items():
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
                
            for entry in feed.entries[:12]:  # 每个站点最多12条
                published_parsed = entry.get("published_parsed")
                all_news.append({
                    "来源": source,
                    "标题": entry.title,
                    "摘要": entry.get("summary", "")[:180] + "..." if entry.get("summary") else "无摘要",
                    "链接": entry.link,
                    "发布时间": entry.get("published", "未知"),
                    "原始时间": published_parsed,
                })
        except Exception as e:
            st.warning(f"⚠️ {source} 抓取失败: {str(e)[:80]}")
            continue  # 单个源失败不影响整体
    
    df = pd.DataFrame(all_news)
    
    # === 关键修复：处理 None 并排序 ===
    if not df.empty and "原始时间" in df.columns:
        df = df.dropna(subset=["原始时间"])  # 移除无效时间
        if not df.empty:
            df = df.sort_values(by="原始时间", ascending=False).reset_index(drop=True)
    
    return df

# ================== 界面 ==================
col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🔄 实时刷新新闻", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.write(f"**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

df = fetch_news()

if df.empty:
    st.warning("暂无与中国相关的新闻，请稍后刷新")
else:
    tabs = st.tabs(list(rss_sources.keys()) + ["全部新闻"])
    
    # 单个来源 Tab
    for i, source in enumerate(rss_sources.keys()):
        with tabs[i]:
            source_df = df[df["来源"] == source]
            if source_df.empty:
                st.info(f"暂无 {source} 的中国相关新闻")
            else:
                for _, row in source_df.iterrows():
                    with st.expander(f"📰 {row['标题'][:75]}...", expanded=False):
                        st.write(f"**发布时间**：{row['发布时间']}")
                        st.write(row["摘要"])
                        st.markdown(f"[📖 阅读全文 →]({row['链接']})")
    
    # 全部新闻 Tab（限制显示前50条，防止页面过长）
    with tabs[-1]:
        st.subheader(f"全部最新中国新闻（共 {len(df)} 条 • 时间倒序）")
        display_df = df.head(50)
        for _, row in display_df.iterrows():
            st.markdown(f"""
            **{row['来源']}** | {row['发布时间']}  
            **{row['标题']}**  
            {row['摘要']}  
            [📖 阅读全文]({row['链接']})
            ---
            """)

# ================== 侧边栏 ==================
st.sidebar.header("✅ 已监控媒体")
st.sidebar.success("12大主流新闻网站（含官方）")
st.sidebar.info("""
• 新增：Вечерний Бишкек（vb.kg）、Экономист（economist.kg）、BBC Кыргыз（bbc.com/kyrgyz）  
• 每5分钟自动刷新  
• 单个源失败不影响整体运行
""")

st.sidebar.header("📱 社交媒体（X / Facebook / Instagram）")
st.sidebar.warning("""
目前暂未纳入（平台限制）。  
推荐方案：  
1. 打开 https://rss.app  
2. 输入吉尔吉斯媒体/自媒体账号链接  
3. 生成RSS后复制链接  
4. 发给我，我立刻帮你加进程序（永久有效）
""")
st.sidebar.markdown("---")
st.sidebar.caption("你的专用中吉中国新闻监控站 v2.1 © 2026")
