#!/usr/bin/env python3
"""
SkillsHub Pro - 智能聚合爬虫
按技能名称聚合多平台数据
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from difflib import SequenceMatcher

OUTPUT_FILE = "/var/www/skillshub-pro/data/skills_aggregated.json"

# 技能名称相似度阈值
SIMILARITY_THRESHOLD = 0.85

def normalize_name(name):
    """标准化技能名称用于匹配"""
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r'[\s\-_]?skill[s]?$', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    return name

def similarity(a, b):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()

class SkillAggregator:
    def __init__(self):
        self.skills = {}  # 原始名称 -> 技能数据
        self.norm_names = {}  # 标准化名称 -> 原始名称
        
    def add_skill(self, platform, skill_data):
        """添加技能到聚合器"""
        name = skill_data.get("name", "")
        if not name:
            return
            
        norm_name = normalize_name(name)
        
        # 查找是否已存在相似技能
        matched_key = None
        for existing_norm, existing_orig in self.norm_names.items():
            if similarity(name, existing_orig) >= SIMILARITY_THRESHOLD:
                matched_key = existing_orig
                break
        
        if matched_key:
            # 合并到现有技能
            self.skills[matched_key]["platforms"][platform] = skill_data
            self._update_aggregated(matched_key)
        else:
            # 创建新技能
            self.skills[name] = {
                "name": name,
                "description": skill_data.get("description", ""),
                "tags": skill_data.get("tags", []),
                "platforms": {
                    platform: skill_data
                },
                "aggregated": {
                    "total_downloads": skill_data.get("downloads", 0),
                    "avg_rating": skill_data.get("rating", 0),
                    "platform_count": 1
                }
            }
            self.norm_names[norm_name] = name
    
    def _update_aggregated(self, skill_name):
        """更新聚合数据"""
        skill = self.skills[skill_name]
        platforms = skill["platforms"]
        
        total_downloads = 0
        ratings = []
        
        for p, data in platforms.items():
            total_downloads += data.get("downloads", 0)
            if data.get("rating", 0) > 0:
                ratings.append(data["rating"])
        
        skill["aggregated"] = {
            "total_downloads": total_downloads,
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "platform_count": len(platforms)
        }
    
    def to_list(self):
        """转换为列表并排序"""
        result = list(self.skills.values())
        result.sort(key=lambda x: (
            x["aggregated"]["platform_count"],
            x["aggregated"]["total_downloads"]
        ), reverse=True)
        return result


# ==================== 虾评Skill ====================
def scrape_xiaping_detailed(aggregator):
    """爬取 xiaping.coze.site 详细信息"""
    print("🕷️  爬取 xiaping.coze.site（详细信息）...")
    page = 1
    limit = 50
    count = 0
    
    while True:
        try:
            url = f"https://xiaping.coze.site/api/skills?page={page}&limit={limit}"
            resp = requests.get(url, timeout=30)
            data = resp.json()
            
            if "skills" not in data or len(data["skills"]) == 0:
                break
            
            for item in data["skills"]:
                skill_id = item.get("id", "")
                name = item.get("name", "")
                
                if not name:
                    continue
                
                # 获取详细信息
                detail = item
                try:
                    detail_url = f"https://xiaping.coze.site/api/skills/{skill_id}"
                    detail_resp = requests.get(detail_url, timeout=30)
                    detail = detail_resp.json()
                except:
                    pass
                
                skill_data = {
                    "name": name,  # 必须包含name
                    "id": skill_id,
                    "url": f"https://xiaping.coze.site/skill/{skill_id}",
                    "rating": round(item.get("avg_stars", 0) / 100, 2) if item.get("avg_stars") else 0,
                    "downloads": item.get("downloads", 0),
                    "description": detail.get("description", item.get("description", "")),
                    "tags": detail.get("tags", item.get("tags", [])),
                    "author": detail.get("owner_name", ""),
                    "version": detail.get("version", ""),
                    "updated_at": detail.get("updated_at", item.get("updated_at", "")),
                    "reviews_count": detail.get("comment_count", 0)
                }
                
                # 获取评论
                try:
                    comments_url = f"https://xiaping.coze.site/api/skills/{skill_id}/comments?limit=5"
                    comments_resp = requests.get(comments_url, timeout=30)
                    comments_data = comments_resp.json()
                    if "comments" in comments_data:
                        skill_data["reviews"] = [
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
                
                aggregator.add_skill("xiaping.coze.site", skill_data)
                count += 1
            
            print(f"  第{page}页: {len(data['skills'])} 个技能")
            page += 1
            time.sleep(0.2)
            
            if page > 100 or count >= 500:
                break
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            break
    
    print(f"  ✅ 总计: {count} 个技能")


# ==================== 其他平台爬虫 ====================
def scrape_clawhub_detailed(aggregator):
    print("🕷️  爬取 clawhub.ai...")
    # 暂时跳过，API不可用
    print("  ⏭️ API暂不可用，跳过")

def scrape_skills_sh_detailed(aggregator):
    print("🕷️  爬取 skills.sh...")
    # 暂时跳过，需要特殊处理
    print("  ⏭️ 需要特殊处理，跳过")

def scrape_tencent_detailed(aggregator):
    print("🕷️  爬取 skillhub.tencent.com...")
    # 暂时跳过，API不可用
    print("  ⏭️ API暂不可用，跳过")


# ==================== 主程序 ====================
def main():
    print("=" * 60)
    print("SkillsHub Pro - 智能聚合爬虫")
    print("=" * 60)
    
    aggregator = SkillAggregator()
    
    # 爬取各平台
    scrape_xiaping_detailed(aggregator)
    scrape_clawhub_detailed(aggregator)
    scrape_skills_sh_detailed(aggregator)
    scrape_tencent_detailed(aggregator)
    
    # 获取结果
    skills = aggregator.to_list()
    
    # 统计
    multi_platform = [s for s in skills if s["aggregated"]["platform_count"] > 1]
    
    # 保存结果
    output = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_skills": len(skills),
            "multi_platform_skills": len(multi_platform),
            "platforms": {
                "xiaping.coze.site": sum(1 for s in skills if "xiaping.coze.site" in s["platforms"]),
                "clawhub.ai": sum(1 for s in skills if "clawhub.ai" in s["platforms"]),
                "skills.sh": sum(1 for s in skills if "skills.sh" in s["platforms"]),
                "skillhub.tencent.com": sum(1 for s in skills if "skillhub.tencent.com" in s["platforms"])
            }
        },
        "skills": skills
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"📊 聚合完成！")
    print(f"  总技能数: {len(skills)}")
    print(f"  多平台技能: {len(multi_platform)}")
    for p, c in output["metadata"]["platforms"].items():
        print(f"    {p}: {c}")
    print(f"  输出: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
