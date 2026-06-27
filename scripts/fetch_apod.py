import requests
import re
import os
import html
from datetime import datetime, timezone

DEFAULT_IMAGE = "https://apod.nasa.gov/apod/image/2401/NGC6357_Cormier_3914.jpg"
APOD_SECTION_START = "<!-- APOD_SECTION_START -->"
APOD_SECTION_END = "<!-- APOD_SECTION_END -->"

def fetch_nasa_apod():
    """获取NASA每日天文图片"""
    url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": "DEMO_KEY",
        "thumbs": True
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        raw_explanation = data.get("explanation", "") or ""
        title = data.get("title", "Astronomy Picture of the Day")
        date = data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        media_type = data.get("media_type", "image")
        url_value = data.get("url", "") or DEFAULT_IMAGE
        hdurl = data.get("hdurl", url_value) or url_value
        
        if len(raw_explanation) > 300:
            explanation = raw_explanation[:300].rstrip() + "..."
        else:
            explanation = raw_explanation
        
        if media_type == "video":
            thumbnail = data.get("thumbnail_url", "") or url_value or DEFAULT_IMAGE
        else:
            thumbnail = url_value or DEFAULT_IMAGE
            
        return {
            "title": title,
            "date": date,
            "explanation": explanation,
            "url": url_value,
            "hdurl": hdurl,
            "thumbnail": thumbnail,
            "media_type": media_type
        }
    except Exception as e:
        print(f"获取NASA APOD失败: {e}")
        return {
            "title": "Astronomy Picture of the Day",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "explanation": "今日图片加载中，GitHub Actions运行后将自动更新...",
            "url": DEFAULT_IMAGE,
            "hdurl": "https://apod.nasa.gov/apod/astropix.html",
            "thumbnail": DEFAULT_IMAGE,
            "media_type": "image"
        }

def update_readme(apod_data):
    """更新README.md中的APOD部分"""
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        print(f"README文件不存在: {readme_path}")
        return False
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    safe_hdurl = html.escape(apod_data['hdurl'], quote=True)
    safe_thumbnail = html.escape(apod_data['thumbnail'], quote=True)
    safe_title = html.escape(apod_data['title'])
    safe_date = html.escape(apod_data['date'])
    safe_explanation = html.escape(apod_data['explanation'])
    
    apod_section = f'''{APOD_SECTION_START}
### 🛰️ NASA Astronomy Picture of the Day | 每日天文图片

<div align="center">
  <a href="{safe_hdurl}" target="_blank">
    <img src="{safe_thumbnail}" alt="{safe_title}" width="700">
  </a>
  <br>
  <h4>{safe_title} ({safe_date})</h4>
  <p>{safe_explanation}</p>
  <sub>🔗 图片来源: <a href="https://apod.nasa.gov/apod/astropix.html" target="_blank">NASA APOD</a> | 每日UTC 01:00（北京时间09:00）自动更新</sub>
</div>

---
{APOD_SECTION_END}'''
    
    pattern = re.escape(APOD_SECTION_START) + r'.*?' + re.escape(APOD_SECTION_END)
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, apod_section, content, flags=re.DOTALL)
    else:
        insertion_point = content.find('### ⭐ My Constellation')
        if insertion_point != -1:
            content = content[:insertion_point] + apod_section + '\n\n' + content[insertion_point:]
        else:
            content += '\n\n' + apod_section
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"NASA APOD已更新: {apod_data['title']}")
    return True

if __name__ == "__main__":
    apod_data = fetch_nasa_apod()
    update_readme(apod_data)
