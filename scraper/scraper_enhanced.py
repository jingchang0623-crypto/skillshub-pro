#!/usr/bin/env python3
"""
SkillsHub Pro - 增强版聚合爬虫
聚合 xiaping.coze.site + GitHub 技能仓库
"""

import requests
import json
import time
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 配置
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "skills_aggregated.json"

def get_github_token():
    """获取GitHub token"""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

import subprocess

# GitHub官方技能仓库列表
GITHUB_OFFICIAL_REPOS = [
    # AI 模型与平台
    ("anthropics", "skills"),
    ("openai", "skills"),
    ("google-gemini", "gemini-skills"),
    ("huggingface", "skills"),
    ("replicate", "skills"),
    ("elevenlabs", "skills"),
    ("black-forest-labs", "skills"),
    # 云服务
    ("cloudflare", "skills"),
    ("hashicorp", "agent-skills"),
    ("databricks", "databricks-agent-skills"),
    ("ClickHouse", "agent-skills"),
    ("supabase", "agent-skills"),
    ("stripe", "ai"),
    ("launchdarkly", "agent-skills"),
    ("getsentry", "skills"),
    # 开发框架
    ("vercel-labs", "agent-skills"),
    ("microsoft", "agent-skills"),
    ("expo", "skills"),
    ("better-auth", "skills"),
    ("posit-dev", "skills"),
    ("remotion-dev", "skills"),
    ("slidevjs", "slidev"),
    ("vercel-labs", "agent-browser"),
    ("browser-use", "browser-use"),
    ("firecrawl", "cli"),
    ("greensock", "gsap-skills"),
    # 内容协作
    ("makenotion", "skills"),
    ("kepano", "obsidian-skills"),
    ("WordPress", "agent-skills"),
    ("langgenius", "dify"),
    ("sanity-io", "agent-toolkit"),
]

# GitHub社区技能仓库
GITHUB_COMMUNITY_REPOS = [
    ("obra", "superpowers"),
    ("nextlevelbuilder", "ui-ux-pro-max-skill"),
    ("JimLiu", "baoyu-skills"),
    ("op7418", ""),  # 需要特殊处理
    ("cclank", "news-aggregator-skill"),
    ("huangserva", "skill-prompt-generator"),
    ("geekjourneyx", "md2wechat-skill"),
    ("wpsnote", "wpsnote-skills"),
    ("teng-lin", "notebooklm-py"),
    ("czlonkowski", "n8n-skills"),
    ("cloudai-x", "threejs-skills"),
    ("coreyhaines31", "marketingskills"),
    ("K-Dense-AI", "claude-scientific-skills"),
    ("libukai", "awesome-agent-skills"),
]

HEADERS = {
    "User-Agent": "SkillsHub-Pro/1.0 (https://skillsagent.org)",
    "Accept": "application/json",
}

def fetch_xiaping_skills():
    """从 xiaping.coze.site 获取技能列表"""
    print("🕷️  爬取 xiaping.coze.site...")
    skills = {}
    page = 1
    limit = 50
    
    while True:
        url = f"https://xiaping.coze.site/api/skills?page={page}&limit={limit}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            data = resp.json()
            items = data.get("skills", data.get("items", []))
            
            if not items:
                break
            
            for item in items:
                name = item.get("name", "")
                if not name:
                    continue
                
                if name not in skills:
                    skills[name] = {
                        "name": name,
                        "description": item.get("description", ""),
                        "tags": item.get("tags", []),
                        "platforms": {},
                        "aggregated": {
                            "total_downloads": 0,
                            "avg_rating": 0,
                            "platform_count": 0
                        }
                    }
                
                skills[name]["platforms"]["xiaping.coze.site"] = {
                    "id": item.get("id"),
                    "url": f"https://xiaping.coze.site/skill/{item.get('id')}",
                    "rating": item.get("rating", 0),
                    "downloads": item.get("downloads", 0),
                    "author": item.get("author", ""),
                    "updated_at": item.get("updated_at", ""),
                }
                
                # 更新聚合数据
                skills[name]["aggregated"]["total_downloads"] += item.get("downloads", 0)
                skills[name]["aggregated"]["platform_count"] += 1
            
            print(f"  第{page}页: {len(items)} 个技能")
            page += 1
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            break
    
    print(f"  ✅ 总计: {len(skills)} 个技能")
    return skills

def fetch_github_repo_skills(owner, repo, token=None):
    """从GitHub仓库获取技能信息"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "name": repo,
                "full_name": f"{owner}/{repo}",
                "description": data.get("description", ""),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "watchers": data.get("watchers_count", 0),
                "url": data.get("html_url", ""),
                "updated_at": data.get("updated_at", ""),
                "language": data.get("language", ""),
                "topics": data.get("topics", []),
            }
        elif resp.status_code == 403:
            print(f"    ⚠️ Rate limited")
        elif resp.status_code == 404:
            print(f"    ⚠️ Not found: {owner}/{repo}")
    except Exception as e:
        print(f"    ⚠️ {owner}/{repo}: {e}")
    return None

def fetch_github_skills():
    """从GitHub获取技能仓库信息"""
    print("🕷️  爬取 GitHub 技能仓库...")
    skills = {}
    
    # 获取token
    token = get_github_token()
    if token:
        print(f"  ✓ 使用GitHub认证")
    
    # 官方仓库
    print("  官方仓库...")
    for owner, repo in GITHUB_OFFICIAL_REPOS:
        skill = fetch_github_repo_skills(owner, repo, token)
        if skill:
            skill_name = skill["name"]
            if skill_name not in skills:
                skills[skill_name] = {
                    "name": skill_name,
                    "description": skill["description"],
                    "tags": skill["topics"],
                    "platforms": {},
                    "aggregated": {
                        "total_downloads": 0,
                        "avg_rating": 0,
                        "platform_count": 0
                    }
                }
            
            skills[skill_name]["platforms"]["github.com"] = {
                "full_name": skill["full_name"],
                "url": skill["url"],
                "stars": skill["stars"],
                "forks": skill["forks"],
                "watchers": skill["watchers"],
                "language": skill["language"],
                "updated_at": skill["updated_at"],
            }
            
            # GitHub的stars作为下载量的近似
            skills[skill_name]["aggregated"]["total_downloads"] += skill["stars"]
            skills[skill_name]["aggregated"]["platform_count"] += 1
            
            print(f"    ✅ {skill['full_name']}: ⭐{skill['stars']}")
        time.sleep(0.1)
    
    # 社区仓库
    print("  社区仓库...")
    for owner, repo in GITHUB_COMMUNITY_REPOS:
        if not repo:
            continue
        skill = fetch_github_repo_skills(owner, repo, token)
        if skill:
            skill_name = skill["name"]
            if skill_name not in skills:
                skills[skill_name] = {
                    "name": skill_name,
                    "description": skill["description"],
                    "tags": skill["topics"],
                    "platforms": {},
                    "aggregated": {
                        "total_downloads": 0,
                        "avg_rating": 0,
                        "platform_count": 0
                    }
                }
            
            skills[skill_name]["platforms"]["github.com"] = {
                "full_name": skill["full_name"],
                "url": skill["url"],
                "stars": skill["stars"],
                "forks": skill["forks"],
                "watchers": skill["watchers"],
                "language": skill["language"],
                "updated_at": skill["updated_at"],
            }
            
            skills[skill_name]["aggregated"]["total_downloads"] += skill["stars"]
            skills[skill_name]["aggregated"]["platform_count"] += 1
            
            print(f"    ✅ {skill['full_name']}: ⭐{skill['stars']}")
        time.sleep(0.1)
    
    print(f"  ✅ 总计: {len(skills)} 个技能仓库")
    return skills

def merge_skills(xiaping_skills, github_skills):
    """合并两个数据源的技能"""
    merged = {}
    
    # 先添加 xiaping 技能
    for name, skill in xiaping_skills.items():
        merged[name] = skill.copy()
    
    # 合并 GitHub 技能
    for name, skill in github_skills.items():
        if name in merged:
            # 已存在，合并平台数据
            merged[name]["platforms"].update(skill["platforms"])
            merged[name]["aggregated"]["total_downloads"] += skill["aggregated"]["total_downloads"]
            merged[name]["aggregated"]["platform_count"] += skill["aggregated"]["platform_count"]
        else:
            # 新技能
            merged[name] = skill
    
    return merged

def calculate_aggregated_stats(skills):
    """计算聚合统计"""
    for name, skill in skills.items():
        ratings = []
        for platform, data in skill["platforms"].items():
            if "rating" in data and data["rating"] > 0:
                ratings.append(data["rating"])
        
        if ratings:
            skill["aggregated"]["avg_rating"] = round(sum(ratings) / len(ratings), 2)
    
    return skills

def main():
    print("=" * 60)
    print("SkillsHub Pro - 增强版聚合爬虫")
    print("=" * 60)
    
    # 获取数据
    xiaping_skills = fetch_xiaping_skills()
    github_skills = fetch_github_skills()
    
    # 合并数据
    print("\n📊 合并数据...")
    skills = merge_skills(xiaping_skills, github_skills)
    skills = calculate_aggregated_stats(skills)
    
    # 统计多平台技能
    multi_platform = sum(1 for s in skills.values() if s["aggregated"]["platform_count"] > 1)
    
    # 保存结果
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_skills": len(skills),
            "multi_platform_skills": multi_platform,
            "platforms": {
                "xiaping.coze.site": len(xiaping_skills),
                "github.com": len(github_skills),
            }
        },
        "skills": list(skills.values())
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 聚合完成！")
    print(f"  总技能数: {len(skills)}")
    print(f"  多平台技能: {multi_platform}")
    print(f"    xiaping.coze.site: {len(xiaping_skills)}")
    print(f"    github.com: {len(github_skills)}")
    print(f"  输出: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
