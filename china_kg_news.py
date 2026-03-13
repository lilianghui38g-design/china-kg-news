import streamlit as st
import feedparser
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="中吉中国新闻监控站", page_icon="🇨🇳", layout="wide")
st.title("🇰🇬 中吉中国新闻实时监控站 v2.0")
st.caption("AKIPRESS • 24.kg • Kaktus • Sputnik • KABAR • KLOOP • VESTI • PRESIDENT • GOV | 仅显示与中国相关的最新新闻")

# ================== 全部RSS来源（已新增5个官方/主流媒体） ==================
rss_sources = {
    "AKIPRESS": "https://news.google.com/rss/search?q=site:akipress.org+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "24.kg": "https://news.google.com/rss/search?q=site:24.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "Kaktus.media": "https://news.google.com/rss/search?q=site:kaktus.media+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "Sputnik.kg": "https://news.google.com/rss/search?q=site:sputnik.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    
    # === 新增部分 ===
    "KABAR": "https://news.google.com/rss/search?q=site:kabar.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "KLOOP": "https://news.google.com/rss/search?q=site:kloop.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "VESTI": "https://news.google.com/rss/search?q=site:vesti.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "PRESIDENT.KG": "https://news.google.com/rss/search?q=site:president.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "GOV.KG": "https://news.google.com/rss/search?q=site:gov.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
}

@st.cache_data(ttl=300)  # 每5分钟自动刷新
def fetch_news():
    all_news = []
    for source, url in rss_sources.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:12]:  # 每个站点最多12条（防止过多）
            all_news.append({
                "来源": source,
                "标题": entry.title,
                "摘要": entry.get("summary", "")[:180] + "...",
                "链接": entry.link,
                "发布时间": entry.get("published", "未知"),
                "原始时间": entry.get("published_parsed", None)
            })
    df = pd.DataFrame(all_news)
    if not df.empty and "原始时间" in df.columns:
        df = df.sort_values(by="原始时间", ascending=False)
    return df

# ================== 界面 ==================
col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🔄 实时刷新新闻", type="primary"):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

df = fetch_news()

if df.empty:
    st.warning("暂无与中国相关的新闻")
else:
    tabs = st.tabs(list(rss_sources.keys()) + ["全部新闻"])
    
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
                        st.markdown(f"[阅读全文 →]({row['链接']})")
    
    with tabs[-1]:
        st.subheader("全部最新中国新闻（时间倒序）")
        for _, row in df.iterrows():
            st.markdown(f"""
            **{row['来源']}** | {row['发布时间']}  
            **{row['标题']}**  
            {row['摘要']}  
            [阅读全文]({row['链接']})  
            ---
            """)

# ================== 侧边栏（新增社交媒体说明） ==================
st.sidebar.header("已监控媒体")
st.sidebar.success("✅ 9大主流新闻网站（含官方）")
st.sidebar.info("""
• 新增：KABAR、KLOOP、VESTI、PRESIDENT.KG、GOV.KG  
• 每5分钟自动刷新  
• 点击按钮手动刷新
""")

st.sidebar.header("社交媒体（X / Facebook / Instagram）")
st.sidebar.warning("""
目前暂未纳入（平台限制）。  
推荐方案：
1. 打开 https://rss.app 
2. 输入吉尔吉斯媒体/自媒体账号链接
3. 生成RSS后复制链接
4. 发给我，我立刻帮你加进程序（永久有效）
""")
st.sidebar.markdown("---")
st.sidebar.caption("你的专用中吉中国新闻监控站 v2.0")
