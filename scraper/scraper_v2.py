#!/usr/bin/env python3
"""
SkillsHub Pro - 增强版爬虫
支持4个平台，自动分页获取全部技能
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

OUTPUT_FILE = "/var/www/skillshub-pro/data/skills.json"

def normalize_skill(data, source):
    """统一数据格式"""
    return {
        "id": data.get("id", ""),
        "name": data.get("name", "Unknown"),
        "description": data.get("description", "")[:500] if data.get("description") else "",
        "source": source,
        "url": data.get("url", ""),
        "tags": data.get("tags", []),
        "stars": data.get("stars", 0),
        "downloads": data.get("downloads", 0),
        "updated_at": data.get("updated_at", datetime.now().isoformat())
    }

# ==================== 虾评Skill ====================
def scrape_xiaping():
    """爬取 xiaping.coze.site - API支持分页"""
    print("🕷️  爬取 xiaping.coze.site...")
    skills = []
    page = 1
    limit = 50
    
    while True:
        try:
            url = f"https://xiaping.coze.site/api/skills?page={page}&limit={limit}"
            resp = requests.get(url, timeout=30)
            data = resp.json()
            
            if "skills" not in data or len(data["skills"]) == 0:
                break
                
            for item in data["skills"]:
                skills.append(normalize_skill({
                    "id": f"xiaping-{item['id']}",
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "url": f"https://xiaping.coze.site/skill/{item['id']}",
                    "tags": item.get("tags", []),
                    "stars": item.get("avg_stars", 0) / 100 if item.get("avg_stars") else 0,
                    "downloads": item.get("downloads", 0),
                    "updated_at": item.get("updated_at", "")
                }, "xiaping.coze.site"))
            
            print(f"  第{page}页: {len(data['skills'])} 个技能")
            page += 1
            time.sleep(0.5)
            
            # 安全限制
            if page > 100:
                break
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            break
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

# ==================== ClawHub ====================
def scrape_clawhub():
    """爬取 clawhub.ai"""
    print("🕷️  爬取 clawhub.ai...")
    skills = []
    
    try:
        # 尝试API
        url = "https://clawhub.ai/api/skills"
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                for item in data:
                    skills.append(normalize_skill({
                        "id": f"clawhub-{item.get('id', '')}",
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "url": f"https://clawhub.ai/skill/{item.get('id', '')}",
                        "tags": item.get("tags", []),
                        "stars": item.get("stars", 0),
                        "downloads": item.get("downloads", 0),
                        "updated_at": item.get("updatedAt", "")
                    }, "clawhub.ai"))
        else:
            # 网页爬取
            url = "https://clawhub.ai/skills"
            resp = requests.get(url, timeout=30)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 查找技能卡片
            cards = soup.find_all('div', class_='skill-card') or soup.find_all('article')
            for card in cards:
                name_elem = card.find('h3') or card.find('h2') or card.find('a')
                desc_elem = card.find('p')
                
                if name_elem:
                    skills.append(normalize_skill({
                        "id": f"clawhub-{len(skills)}",
                        "name": name_elem.get_text(strip=True),
                        "description": desc_elem.get_text(strip=True) if desc_elem else "",
                        "url": f"https://clawhub.ai/skill/{len(skills)}",
                        "tags": [],
                        "stars": 0,
                        "downloads": 0,
                        "updated_at": datetime.now().isoformat()
                    }, "clawhub.ai"))
                    
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

# ==================== Skills.sh ====================
def scrape_skills_sh():
    """爬取 skills.sh"""
    print("🕷️  爬取 skills.sh...")
    skills = []
    
    try:
        # 尝试API
        url = "https://api.skills.sh/v1/skills"
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                for item in data:
                    skills.append(normalize_skill({
                        "id": f"skillssh-{item.get('id', '')}",
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "url": f"https://skills.sh/skill/{item.get('id', '')}",
                        "tags": item.get("tags", []),
                        "stars": item.get("stars", 0),
                        "downloads": item.get("downloads", 0),
                        "updated_at": item.get("updatedAt", "")
                    }, "skills.sh"))
        else:
            # 网页爬取
            url = "https://skills.sh"
            resp = requests.get(url, timeout=30)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 查找技能列表
            items = soup.find_all('div', class_='skill') or soup.find_all('li', class_='skill-item')
            for item in items:
                name_elem = item.find('a') or item.find('h3')
                
                if name_elem:
                    skills.append(normalize_skill({
                        "id": f"skillssh-{len(skills)}",
                        "name": name_elem.get_text(strip=True),
                        "description": "",
                        "url": f"https://skills.sh",
                        "tags": [],
                        "stars": 0,
                        "downloads": 0,
                        "updated_at": datetime.now().isoformat()
                    }, "skills.sh"))
                    
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

# ==================== Tencent SkillHub ====================
def scrape_tencent_skillhub():
    """爬取 skillhub.tencent.com"""
    print("🕷️  爬取 skillhub.tencent.com...")
    skills = []
    
    try:
        # 尝试公开API
        url = "https://skillhub.tencent.com/api/skills"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                for item in data:
                    skills.append(normalize_skill({
                        "id": f"tencent-{item.get('id', '')}",
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "url": f"https://skillhub.tencent.com/skill/{item.get('id', '')}",
                        "tags": item.get("tags", []),
                        "stars": item.get("stars", 0),
                        "downloads": item.get("downloads", 0),
                        "updated_at": item.get("updatedAt", "")
                    }, "skillhub.tencent.com"))
        else:
            # 网页爬取
            url = "https://skillhub.tencent.com"
            resp = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 查找技能卡片
            cards = soup.find_all('div', class_='skill-card') or soup.find_all('div', class_='item')
            for card in cards:
                name_elem = card.find('h3') or card.find('h4') or card.find('a')
                
                if name_elem:
                    skills.append(normalize_skill({
                        "id": f"tencent-{len(skills)}",
                        "name": name_elem.get_text(strip=True),
                        "description": "",
                        "url": "https://skillhub.tencent.com",
                        "tags": [],
                        "stars": 0,
                        "downloads": 0,
                        "updated_at": datetime.now().isoformat()
                    }, "skillhub.tencent.com"))
                    
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

# ==================== 主程序 ====================
def main():
    print("=" * 60)
    print("SkillsHub Pro - 增强版爬虫")
    print("=" * 60)
    
    all_skills = []
    
    # 爬取各平台
    all_skills.extend(scrape_xiaping())
    all_skills.extend(scrape_clawhub())
    all_skills.extend(scrape_skills_sh())
    all_skills.extend(scrape_tencent_skillhub())
    
    # 去重
    seen = set()
    unique_skills = []
    for skill in all_skills:
        if skill["id"] not in seen:
            seen.add(skill["id"])
            unique_skills.append(skill)
    
    # 保存结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_skills, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"📊 爬取完成！")
    print(f"  总计: {len(unique_skills)} 个技能")
    print(f"  输出: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
