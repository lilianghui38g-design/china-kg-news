import streamlit as st
import feedparser
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="中吉中国新闻监控站", page_icon="🇨🇳", layout="wide")
st.title("🇰🇬 中吉中国新闻实时监控站 v3.0")
st.caption("9大新闻网站 + Facebook 前10大吉媒体 | 仅显示与中国相关的最新新闻")

# ================== 原有9大新闻网站 RSS ==================
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
}

# ================== Facebook 前10大账号（请替换RSS） ==================
facebook_sources = {
    "FB_Azattyk": "YOUR_RSS_HERE",          # Facebook页面：https://www.facebook.com/azattyk.org/
    "FB_Kloop": "YOUR_RSS_HERE",            # https://www.facebook.com/kloop.kg/
    "FB_AKIpress": "YOUR_RSS_HERE",         # https://www.facebook.com/akipress/
    "FB_BBC_Kyrgyz": "YOUR_RSS_HERE",       # https://www.facebook.com/bbcnewskyrgyz/
    "FB_Kaktus": "YOUR_RSS_HERE",           # https://www.facebook.com/kaktus.kyrgyzstan/
    "FB_KNews": "YOUR_RSS_HERE",            # https://www.facebook.com/knews.kg/
    "FB_Vesti": "YOUR_RSS_HERE",            # https://www.facebook.com/vestikg/
    "FB_SuperKG": "YOUR_RSS_HERE",          # https://www.facebook.com/Super.kg.Portaly/
    "FB_VBishkek": "YOUR_RSS_HERE",         # https://www.facebook.com/vb.kg.news/
    "FB_24kg": "YOUR_RSS_HERE",             # 24.kg页面请自行搜索确认后生成（粉丝约4.9万）
}

@st.cache_data(ttl=300)
def fetch_news():
    all_news = []
    # 原有新闻网站
    for source, url in rss_sources.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            all_news.append({"来源": source, "标题": entry.title, "摘要": entry.get("summary", "")[:180] + "...", "链接": entry.link, "发布时间": entry.get("published", "未知")})
    
    # Facebook账号
    for source, url in facebook_sources.items():
        if url != "YOUR_RSS_HERE":
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                all_news.append({"来源": source.replace("FB_", "Facebook - "), "标题": entry.title, "摘要": entry.get("summary", "")[:180] + "...", "链接": entry.link, "发布时间": entry.get("published", "未知")})
    
    df = pd.DataFrame(all_news)
    return df.sort_values(by="发布时间", ascending=False) if not df.empty else df

# ================== 界面 ==================
col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🔄 实时刷新新闻", type="primary"):
        st.cache_data.clear()
        st.rerun()
with col2:
    st.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

df = fetch_news()

tabs = st.tabs(list(rss_sources.keys()) + ["Facebook Top10", "全部新闻"])

# 原有新闻网站标签页
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

# Facebook Top10 标签页
with tabs[-2]:
    st.subheader("📘 Facebook 前10大吉尔吉斯媒体（涉华新闻）")
    fb_df = df[df["来源"].str.contains("Facebook - ")]
    if fb_df.empty:
        st.warning("请先生成RSS链接并替换代码中的 YOUR_RSS_HERE")
    else:
        for _, row in fb_df.iterrows():
            with st.expander(f"📰 {row['标题'][:75]}...", expanded=False):
                st.write(f"**发布时间**：{row['发布时间']}")
                st.write(row["摘要"])
                st.markdown(f"[阅读全文 →]({row['链接']})")

# 全部新闻
with tabs[-1]:
    st.subheader("全部最新中国新闻（时间倒序）")
    for _, row in df.iterrows():
        st.markdown(f"**{row['来源']}** | {row['发布时间']}  \n**{row['标题']}**  \n{row['摘要']}  \n[阅读全文]({row['链接']})  \n---")

# ================== 侧边栏（生成RSS教程） ==================
st.sidebar.header("✅ 已监控来源")
st.sidebar.success("9大新闻网站 + Facebook Top10")
st.sidebar.info("每5分钟自动刷新")

st.sidebar.header("📘 如何一键添加Facebook前10账号（只需做一次）")
st.sidebar.markdown("""
1. 打开 https://rss.app
2. 复制下方每个Facebook页面链接，粘贴进去
3. 点击 Generate RSS
4. 复制生成的链接（https://rss.app/feeds/xxxx.xml）
5. 把代码里对应的 **YOUR_RSS_HERE** 替换成你的链接
6. GitHub提交 → 网站自动更新
""")

st.sidebar.subheader("10个Facebook页面链接（直接复制）")
st.sidebar.markdown("""
- Azattyk：https://www.facebook.com/azattyk.org/
- Kloop：https://www.facebook.com/kloop.kg/
- AKIpress：https://www.facebook.com/akipress/
- BBC Kyrgyz：https://www.facebook.com/bbcnewskyrgyz/
- Kaktus：https://www.facebook.com/kaktus.kyrgyzstan/
- K-News：https://www.facebook.com/knews.kg/
- Vesti：https://www.facebook.com/vestikg/
- SuperKG：https://www.facebook.com/Super.kg.Portaly/
- Vecherniy Bishkek：https://www.facebook.com/vb.kg.news/
- 24.kg：请搜索“24.kg facebook”确认官方页后生成
""")

st.sidebar.caption("v3.0 已覆盖吉尔吉斯斯坦几乎所有主流渠道 🇨🇳🇰🇬")
