#!/usr/bin/env python3
"""
SkillsHub Pro - 简化版聚合爬虫
"""

import json
import requests
from datetime import datetime
import time

OUTPUT_FILE = "/var/www/skillshub-pro/data/skills_aggregated.json"

def main():
    print("=" * 60)
    print("SkillsHub Pro - 聚合爬虫")
    print("=" * 60)
    
    skills = []
    page = 1
    limit = 50
    
    print("🕷️  爬取 xiaping.coze.site...")
    while True:
        try:
            url = f"https://xiaping.coze.site/api/skills?page={page}&limit={limit}"
            resp = requests.get(url, timeout=30)
            data = resp.json()
            
            if "skills" not in data or len(data["skills"]) == 0:
                break
            
            for item in data["skills"]:
                # 获取详细信息
                skill_id = item.get("id", "")
                name = item.get("name", "")
                
                if not name:
                    continue
                
                # 尝试获取评论
                reviews = []
                try:
                    comments_url = f"https://xiaping.coze.site/api/skills/{skill_id}/comments?limit=5"
                    comments_resp = requests.get(comments_url, timeout=10)
                    comments_data = comments_resp.json()
                    if "comments" in comments_data:
                        reviews = [
                            {
                                "user": c.get("user_name", ""),
                                "rating": round(c.get("stars", 0) / 100, 2) if c.get("stars") else 0,
                                "content": c.get("content", "")[:200],
                                "date": c.get("created_at", "")
                            }
                            for c in comments_data["comments"][:5]
                        ]
                except:
                    pass
                
                skill = {
                    "name": name,
                    "description": item.get("description", ""),
                    "tags": item.get("tags", []),
                    "platforms": {
                        "xiaping.coze.site": {
                            "id": skill_id,
                            "url": f"https://xiaping.coze.site/skill/{skill_id}",
                            "rating": round(item.get("avg_stars", 0) / 100, 2) if item.get("avg_stars") else 0,
                            "downloads": item.get("downloads", 0),
                            "author": item.get("owner_name", ""),
                            "updated_at": item.get("updated_at", ""),
                            "reviews": reviews,
                            "reviews_count": len(reviews)
                        }
                    },
                    "aggregated": {
                        "total_downloads": item.get("downloads", 0),
                        "avg_rating": round(item.get("avg_stars", 0) / 100, 2) if item.get("avg_stars") else 0,
                        "platform_count": 1
                    }
                }
                skills.append(skill)
            
            print(f"  第{page}页: {len(data['skills'])} 个技能")
            page += 1
            time.sleep(0.3)
            
            if page > 20:
                break
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            break
    
    # 按下载量排序
    skills.sort(key=lambda x: x["aggregated"]["total_downloads"], reverse=True)
    
    # 保存结果
    output = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_skills": len(skills),
            "platforms": {
                "xiaping.coze.site": len(skills)
            }
        },
        "skills": skills
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"📊 聚合完成！")
    print(f"  总技能数: {len(skills)}")
    print(f"  输出: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
