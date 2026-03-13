import streamlit as st
import feedparser
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="中吉中国新闻监控站", page_icon="🇨🇳", layout="wide")
st.title("🇰🇬 中吉中国新闻实时监控站")
st.caption("AKIPRESS • 24.kg • Kaktus.media • Sputnik.kg | 仅显示与中国相关的最新新闻")

# ================== 配置四个网站的 Google News RSS ==================
rss_sources = {
    "AKIPRESS": "https://news.google.com/rss/search?q=site:akipress.org+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "24.kg": "https://news.google.com/rss/search?q=site:24.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "Kaktus.media": "https://news.google.com/rss/search?q=site:kaktus.media+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
    "Sputnik.kg": "https://news.google.com/rss/search?q=site:sputnik.kg+(Китай+OR+КНР+OR+China+OR+Кытай)&hl=ru&gl=KG&ceid=KG:ru",
}

@st.cache_data(ttl=300)  # 每5分钟自动刷新一次
def fetch_news():
    all_news = []
    for source, url in rss_sources.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:  # 每个站点最多取15条
            all_news.append({
                "来源": source,
                "标题": entry.title,
                "摘要": entry.get("summary", "")[:200] + "...",
                "链接": entry.link,
                "发布时间": entry.get("published", "未知"),
                "原始时间": entry.get("published_parsed", None)
            })
    # 排序（最新在前）
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
    st.warning("暂无与中国相关的新闻（可能 Google 还未索引最新内容）")
else:
    # 分站点展示（更清晰）
    tabs = st.tabs(list(rss_sources.keys()) + ["全部新闻"])
    
    for i, source in enumerate(rss_sources.keys()):
        with tabs[i]:
            source_df = df[df["来源"] == source]
            if source_df.empty:
                st.info(f"暂无 {source} 的中国相关新闻")
            else:
                for _, row in source_df.iterrows():
                    with st.expander(f"📰 {row['标题'][:80]}...", expanded=False):
                        st.write(f"**发布时间**：{row['发布时间']}")
                        st.write(row["摘要"])
                        st.markdown(f"[阅读全文 →]({row['链接']})")
    
    # 全部新闻 Tab（时间线）
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

# 侧边栏说明
st.sidebar.header("使用说明")
st.sidebar.info("""
• 程序自动监控 4 个吉尔吉斯主流媒体  
• 关键词：Китай、КНР、China、Кытай  
• 每 5 分钟自动刷新（缓存）  
• 点击“实时刷新”立即更新  
• 免费部署成永久网站（见下方）
""")
st.sidebar.success("适合外交、商务、研究人员使用")

# 部署提示
st.sidebar.markdown("---")
st.sidebar.subheader("如何变成永久专用网站？")
st.sidebar.markdown("""
1. 注册 https://streamlit.io/cloud （免费）
2. 新建 App → 连接 GitHub（把本文件上传）
3. 部署后得到永久链接（如 https://你的名字-china-kg-news.streamlit.app）
4. 可分享给团队使用
""")
