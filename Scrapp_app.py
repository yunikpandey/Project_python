import streamlit as st
import requests
from bs4 import BeautifulSoup
from processor import *
from datetime import datetime
import pandas as pd
import json

# Initialize session state for storing multiple articles
if 'articles' not in st.session_state:
    st.session_state.articles = []

def url_process(url, response):
    papers = ['onlinekhabar', 'setopati', 'ratopati', 'annapurnapost', 'nagariknews', 'ekantipur']
    
    try:
        domain_parts = url.split('//')[-1].split('/')[0].split('.')
        site_name = domain_parts[-2] if len(domain_parts) >= 2 else domain_parts[-1]
        
        if site_name not in papers:
            return None, f"Unsupported website: {site_name}", None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        st.info(f"Processing {site_name} article...")
        
        processor_name = f"process_{site_name}"
        processor = globals().get(processor_name)
        
        if not processor:
            return None, f"Processor function missing: {processor_name}", None
            
        content = processor(soup)
        if not content.strip():
            return None, f"No content could be extracted from {site_name}", None
            
        return content, None, site_name
        
    except Exception as e:
        return None, f"Processing error: {str(e)}", None


# ─── Main UI ───────────────────────────────────────────────────────────────
st.title("Nepali News Article Extractor")

url = st.text_input(
    "Paste article URL here:",
    placeholder="https://www.setopati.com/politics/..."
)

col1, col2 = st.columns([3, 1])
with col1:
    extract_btn = st.button("Extract & Save", type="primary")
with col2:
    if st.button("Clear All", type="secondary"):
        st.session_state.articles = []
        st.rerun()

if extract_btn:
    if not url.strip():
        st.warning("Please enter a URL")
    else:
        with st.spinner("Fetching & processing article..."):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'
                }
                response = requests.get(url, headers=headers, timeout=12)
                
                if response.status_code != 200:
                    st.error(f"Page returned status code {response.status_code}")
                else:
                    content, error, site_name = url_process(url, response)
                    
                    if error:
                        st.error(error)
                    else:
                        # Save to history
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        article_data = {
                            "url": url,
                            "site": site_name,
                            "extracted_at": timestamp,
                            "content_length": len(content),
                            "content": content
                        }
                        
                        st.session_state.articles.append(article_data)
                        
                        st.success(f"Article saved! Total articles: {len(st.session_state.articles)}")
                        
                        # Show current article
                        with st.expander("Latest Extracted Content", expanded=True):
                            st.markdown(content)
                        
            except requests.exceptions.RequestException as e:
                st.error(f"Connection problem: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")


# ─── History & Bulk Export ─────────────────────────────────────────────────
if st.session_state.articles:
    st.subheader(f"Collected Articles ({len(st.session_state.articles)})")
    
    # Create preview dataframe (without full content)
    preview_df = pd.DataFrame([
        {
            "URL": a["url"],
            "Site": a["site"],
            "Date": a["extracted_at"],
            "Length": a["content_length"]
        }
        for a in st.session_state.articles
    ])
    
    st.dataframe(preview_df, use_container_width=True)
    
    # Export buttons
    col_csv, col_json = st.columns(2)
    
    with col_csv:
        csv_data = pd.DataFrame(st.session_state.articles).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download ALL as CSV",
            data=csv_data,
            file_name=f"nepali_news_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    with col_json:
        json_data = json.dumps(st.session_state.articles, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download ALL as JSON",
            data=json_data,
            file_name=f"nepali_news_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

st.caption("Supported sites: onlinekhabar • setopati • ratopati • annapurnapost • nagariknews • ekantipur")
