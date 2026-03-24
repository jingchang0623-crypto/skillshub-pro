#!/usr/bin/env python3
"""
SkillsHub Pro - 终极版爬虫
尝试所有可能的方式获取数据
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
    """爬取 xiaping.coze.site - 全部数据"""
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
            time.sleep(0.3)
            
            if page > 100:
                break
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            break
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

# ==================== ClawHub ====================
def scrape_clawhub():
    """爬取 clawhub.ai - 多种方式尝试"""
    print("🕷️  爬取 clawhub.ai...")
    skills = []
    
    # 方式1: 尝试搜索API
    try:
        url = "https://clawhub.ai/api/skills?nonSuspicious=true"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  发现API数据: {type(data)}")
    except Exception as e:
        print(f"  API方式失败: {e}")
    
    # 方式2: 网页爬取
    try:
        url = "https://clawhub.ai/skills?nonSuspicious=true"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 查找所有可能的技能元素
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'skills' in script.string:
                # 尝试从JavaScript中提取数据
                match = re.search(r'"skills":\s*(\[.*?\])', script.string, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        for item in data:
                            skills.append(normalize_skill({
                                "id": f"clawhub-{item.get('id', len(skills))}",
                                "name": item.get("name", ""),
                                "description": item.get("description", ""),
                                "url": f"https://clawhub.ai/skill/{item.get('id', '')}",
                                "tags": item.get("tags", []),
                                "stars": 0,
                                "downloads": item.get("downloads", 0),
                                "updated_at": datetime.now().isoformat()
                            }, "clawhub.ai"))
                        print(f"  从JS中提取: {len(skills)} 个技能")
                        break
                    except:
                        pass
                        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

# ==================== Skills.sh ====================
def scrape_skills_sh():
    """爬取 skills.sh"""
    print("🕷️  爬取 skills.sh...")
    skills = []
    
    # 方式1: GitHub数据源
    try:
        # skills.sh的数据来自GitHub仓库
        repos = [
            "inferen-sh/skills",
            "microsoft/github-copilot-for-azure",
            "microsoft/azure-skills"
        ]
        
        for repo in repos:
            url = f"https://api.github.com/repos/{repo}/contents"
            resp = requests.get(url, timeout=30)
            
            if resp.status_code == 200:
                files = resp.json()
                if isinstance(files, list):
                    for f in files:
                        if f['type'] == 'dir' or f['name'].endswith('.md'):
                            skills.append(normalize_skill({
                                "id": f"skillssh-{f['name']}",
                                "name": f['name'].replace('.md', '').replace('-', ' ').title(),
                                "description": f"来自 {repo}",
                                "url": f['html_url'],
                                "tags": ["github"],
                                "stars": 0,
                                "downloads": 0,
                                "updated_at": datetime.now().isoformat()
                            }, "skills.sh"))
                    
                    print(f"  从 {repo}: {len(files)} 项")
    except Exception as e:
        print(f"  GitHub方式失败: {e}")
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

# ==================== Tencent SkillHub ====================
def scrape_tencent_skillhub():
    """爬取 skillhub.tencent.com"""
    print("🕷️  爬取 skillhub.tencent.com...")
    skills = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        # 尝试多个可能的API端点
        endpoints = [
            "https://skillhub.tencent.com/api/v1/skills",
            "https://skillhub.tencent.com/api/skills/list",
            "https://skillhub.tencent.com/api/skill/list",
        ]
        
        for url in endpoints:
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"  发现API: {url}")
                    break
            except:
                continue
                
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

# ==================== 主程序 ====================
def main():
    print("=" * 60)
    print("SkillsHub Pro - 终极版爬虫")
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
        key = f"{skill['source']}-{skill['name']}"
        if key not in seen:
            seen.add(key)
            unique_skills.append(skill)
    
    # 保存结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_skills, f, ensure_ascii=False, indent=2)
    
    # 统计
    stats = {}
    for skill in unique_skills:
        stats[skill['source']] = stats.get(skill['source'], 0) + 1
    
    print("\n" + "=" * 60)
    print(f"📊 爬取完成！")
    print(f"  总计: {len(unique_skills)} 个技能")
    for source, count in stats.items():
        print(f"    {source}: {count}")
    print(f"  输出: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
