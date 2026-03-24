#!/usr/bin/env python3
"""
SkillsHub Pro Scraper
抓取多个技能平台的技能数据
"""

import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup


class Skill:
    """技能数据模型"""
    def __init__(self, id: str, name: str, description: str, source: str, 
                 url: str, tags: List[str] = None, stars: int = 0, 
                 downloads: int = 0, updated_at: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.source = source
        self.url = url
        self.tags = tags or []
        self.stars = stars
        self.downloads = downloads
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source': self.source,
            'url': self.url,
            'tags': self.tags,
            'stars': self.stars,
            'downloads': self.downloads,
            'updated_at': self.updated_at
        }


class SkillsShScraper:
    """skills.sh 平台爬虫 - API方式"""
    
    def __init__(self):
        self.base_url = "https://skills.sh"
        self.api_url = f"{self.base_url}/api"
    
    def scrape(self) -> List[Skill]:
        """抓取技能数据"""
        skills = []
        try:
            # 尝试获取技能列表API
            response = requests.get(f"{self.api_url}/skills", timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('skills', data if isinstance(data, list) else []):
                    skill_id = item.get('id') or self._generate_id(item.get('name', ''))
                    skill = Skill(
                        id=f"skillssh-{skill_id}",
                        name=item.get('name', 'Unknown'),
                        description=item.get('description', item.get('summary', '')),
                        source='skills.sh',
                        url=item.get('url', f"{self.base_url}/skill/{skill_id}"),
                        tags=item.get('tags', []),
                        stars=item.get('stars', item.get('likes', 0)),
                        downloads=item.get('downloads', item.get('installs', 0)),
                        updated_at=item.get('updated_at', item.get('updatedAt'))
                    )
                    skills.append(skill)
            else:
                # 如果API不可用，尝试网页爬取
                print(f"skills.sh API returned {response.status_code}, falling back to web scraping")
                skills = self._scrape_web()
        except Exception as e:
            print(f"skills.sh API error: {e}, falling back to web scraping")
            skills = self._scrape_web()
        
        return skills
    
    def _scrape_web(self) -> List[Skill]:
        """网页爬取备用方案"""
        skills = []
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 根据实际网页结构调整选择器
                skill_cards = soup.find_all(['div', 'article'], class_=lambda x: x and 'skill' in x.lower() if x else False)
                
                for card in skill_cards[:20]:  # 限制前20个
                    name_elem = card.find(['h2', 'h3', 'h4', 'a'])
                    desc_elem = card.find('p')
                    
                    if name_elem:
                        name = name_elem.get_text(strip=True)
                        desc = desc_elem.get_text(strip=True) if desc_elem else ''
                        skill_id = self._generate_id(name)
                        
                        skill = Skill(
                            id=f"skillssh-{skill_id}",
                            name=name,
                            description=desc,
                            source='skills.sh',
                            url=f"{self.base_url}/skill/{skill_id}",
                            tags=[]
                        )
                        skills.append(skill)
        except Exception as e:
            print(f"skills.sh web scraping error: {e}")
        
        return skills
    
    def _generate_id(self, name: str) -> str:
        return hashlib.md5(name.encode()).hexdigest()[:8]


class ClawhubScraper:
    """clawhub.ai 平台爬虫"""
    
    def __init__(self):
        self.base_url = "https://clawhub.ai"
    
    def scrape(self) -> List[Skill]:
        """抓取技能数据"""
        skills = []
        try:
            # 尝试API端点
            response = requests.get(f"{self.base_url}/api/skills", timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('skills', data if isinstance(data, list) else []):
                    skill_id = item.get('id') or self._generate_id(item.get('name', ''))
                    skill = Skill(
                        id=f"clawhub-{skill_id}",
                        name=item.get('name', 'Unknown'),
                        description=item.get('description', ''),
                        source='clawhub.ai',
                        url=item.get('url', f"{self.base_url}/skill/{skill_id}"),
                        tags=item.get('tags', []),
                        stars=item.get('stars', 0),
                        downloads=item.get('downloads', 0),
                        updated_at=item.get('updated_at')
                    )
                    skills.append(skill)
            else:
                # 网页爬取
                skills = self._scrape_web()
        except Exception as e:
            print(f"clawhub.ai API error: {e}, falling back to web scraping")
            skills = self._scrape_web()
        
        return skills
    
    def _scrape_web(self) -> List[Skill]:
        """网页爬取"""
        skills = []
        try:
            # 尝试技能列表页面
            for page_path in ['/skills', '/explore', '/']:
                try:
                    url = f"{self.base_url}{page_path}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # 查找技能卡片
                        cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(kw in x.lower() for kw in ['skill', 'card', 'item']) if x else False)
                        
                        for card in cards[:20]:
                            name_elem = card.find(['h2', 'h3', 'h4', 'a', 'span'])
                            desc_elem = card.find('p')
                            
                            if name_elem:
                                name = name_elem.get_text(strip=True)
                                if not name or len(name) < 2:
                                    continue
                                
                                desc = desc_elem.get_text(strip=True) if desc_elem else ''
                                skill_id = self._generate_id(name)
                                
                                skill = Skill(
                                    id=f"clawhub-{skill_id}",
                                    name=name,
                                    description=desc,
                                    source='clawhub.ai',
                                    url=f"{self.base_url}/skill/{skill_id}",
                                    tags=[]
                                )
                                skills.append(skill)
                        
                        if skills:
                            break
                except:
                    continue
        except Exception as e:
            print(f"clawhub.ai web scraping error: {e}")
        
        return skills
    
    def _generate_id(self, name: str) -> str:
        return hashlib.md5(name.encode()).hexdigest()[:8]


class XiapingCozeScraper:
    """xiaping.coze.site 平台爬虫 - API方式"""
    
    def __init__(self):
        self.base_url = "https://xiaping.coze.site"
        self.api_url = f"{self.base_url}/api/skills"
    
    def scrape(self) -> List[Skill]:
        """抓取技能数据"""
        skills = []
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('skills', data if isinstance(data, list) else []):
                    skill_id = item.get('id') or self._generate_id(item.get('name', ''))
                    skill = Skill(
                        id=f"xiaping-{skill_id}",
                        name=item.get('name', 'Unknown'),
                        description=item.get('description', item.get('summary', '')),
                        source='xiaping.coze.site',
                        url=item.get('url', f"{self.base_url}/skill/{skill_id}"),
                        tags=item.get('tags', []),
                        stars=item.get('stars', 0),
                        downloads=item.get('downloads', 0),
                        updated_at=item.get('updated_at', item.get('updatedAt'))
                    )
                    skills.append(skill)
            else:
                print(f"xiaping.coze.site API returned {response.status_code}")
        except Exception as e:
            print(f"xiaping.coze.site API error: {e}")
        
        return skills
    
    def _generate_id(self, name: str) -> str:
        return hashlib.md5(name.encode()).hexdigest()[:8]


class TencentSkillhubScraper:
    """skillhub.tencent.com 平台爬虫"""
    
    def __init__(self):
        self.base_url = "https://skillhub.tencent.com"
    
    def scrape(self) -> List[Skill]:
        """抓取技能数据"""
        skills = []
        try:
            # 尝试API端点
            for api_path in ['/api/skills', '/api/v1/skills', '/gateway/api/skills']:
                try:
                    response = requests.get(f"{self.base_url}{api_path}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get('skills', data.get('data', data if isinstance(data, list) else [])):
                            skill_id = item.get('id') or self._generate_id(item.get('name', ''))
                            skill = Skill(
                                id=f"tencent-{skill_id}",
                                name=item.get('name', 'Unknown'),
                                description=item.get('description', item.get('desc', '')),
                                source='skillhub.tencent.com',
                                url=item.get('url', f"{self.base_url}/skill/{skill_id}"),
                                tags=item.get('tags', item.get('labels', [])),
                                stars=item.get('stars', item.get('starCount', 0)),
                                downloads=item.get('downloads', item.get('downloadCount', 0)),
                                updated_at=item.get('updated_at', item.get('updateTime'))
                            )
                            skills.append(skill)
                        if skills:
                            return skills
                except:
                    continue
            
            # 网页爬取备用
            skills = self._scrape_web()
        except Exception as e:
            print(f"skillhub.tencent.com error: {e}, falling back to web scraping")
            skills = self._scrape_web()
        
        return skills
    
    def _scrape_web(self) -> List[Skill]:
        """网页爬取"""
        skills = []
        try:
            for page_path in ['/', '/skills', '/explore']:
                try:
                    url = f"{self.base_url}{page_path}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # 查找技能列表
                        cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(kw in x.lower() for kw in ['skill', 'card', 'item', 'plugin']) if x else False)
                        
                        for card in cards[:20]:
                            name_elem = card.find(['h2', 'h3', 'h4', 'a'])
                            desc_elem = card.find('p')
                            
                            if name_elem:
                                name = name_elem.get_text(strip=True)
                                if not name or len(name) < 2:
                                    continue
                                
                                desc = desc_elem.get_text(strip=True) if desc_elem else ''
                                skill_id = self._generate_id(name)
                                
                                skill = Skill(
                                    id=f"tencent-{skill_id}",
                                    name=name,
                                    description=desc,
                                    source='skillhub.tencent.com',
                                    url=f"{self.base_url}/skill/{skill_id}",
                                    tags=[]
                                )
                                skills.append(skill)
                        
                        if skills:
                            break
                except:
                    continue
        except Exception as e:
            print(f"skillhub.tencent.com web scraping error: {e}")
        
        return skills
    
    def _generate_id(self, name: str) -> str:
        return hashlib.md5(name.encode()).hexdigest()[:8]


class SkillHubProScraper:
    """主爬虫管理器"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.scrapers = [
            SkillsShScraper(),
            ClawhubScraper(),
            XiapingCozeScraper(),
            TencentSkillhubScraper()
        ]
    
    def run(self) -> List[Dict]:
        """运行所有爬虫"""
        all_skills = []
        
        for scraper in self.scrapers:
            source_name = scraper.__class__.__name__.replace('Scraper', '')
            print(f"\n🔍 Scraping {source_name}...")
            
            try:
                skills = scraper.scrape()
                print(f"✅ Found {len(skills)} skills from {source_name}")
                all_skills.extend([skill.to_dict() for skill in skills])
            except Exception as e:
                print(f"❌ Error scraping {source_name}: {e}")
            
            # 礼貌延迟
            time.sleep(1)
        
        # 保存结果
        self._save(all_skills)
        
        print(f"\n{'='*50}")
        print(f"📊 Total skills scraped: {len(all_skills)}")
        print(f"💾 Saved to: {self.output_path}")
        
        return all_skills
    
    def _save(self, skills: List[Dict]):
        """保存到JSON文件"""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(skills, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    output_path = "/var/www/skillshub-pro/data/skills.json"
    scraper = SkillHubProScraper(output_path)
    scraper.run()
