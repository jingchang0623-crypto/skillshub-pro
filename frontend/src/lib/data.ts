import { Skill, Platform, SkillsData } from '@/types/skill';
import fs from 'fs';
import path from 'path';

const DATA_PATH = path.join(process.cwd(), 'data', 'skills.json');

interface RawSkill {
  id: string;
  name: string;
  description: string;
  source: string;
  url: string;
  tags: string[];
  stars: number;
  downloads: number;
  updated_at: string;
}

export async function getSkillsData(): Promise<SkillsData> {
  try {
    if (!fs.existsSync(DATA_PATH)) {
      console.warn('Skills data file not found at:', DATA_PATH);
      return getDefaultData();
    }
    
    const fileContents = fs.readFileSync(DATA_PATH, 'utf8');
    const rawData: RawSkill[] = JSON.parse(fileContents);
    
    if (!Array.isArray(rawData)) {
      console.warn('Invalid skills data structure');
      return getDefaultData();
    }
    
    // 转换数据格式
    const skills: Skill[] = rawData.map((item) => ({
      id: item.id,
      name: item.name,
      description: item.description || '',
      tags: item.tags || [],
      platform: item.source as Platform,
      author: '',
      url: item.url,
      stars: item.stars || 0,
      createdAt: item.updated_at || new Date().toISOString(),
    }));
    
    // 计算平台统计
    const platforms: Record<Platform, number> = {
      'skills.sh': 0,
      'clawhub.ai': 0,
      'xiaping.coze.site': 0,
      'skillhub.tencent.com': 0,
    };
    
    skills.forEach((skill) => {
      if (skill.platform in platforms) {
        platforms[skill.platform]++;
      }
    });
    
    return {
      skills,
      metadata: {
        lastUpdated: new Date().toISOString(),
        totalSkills: skills.length,
        platforms,
      },
    };
  } catch (error) {
    console.error('Error reading skills data:', error);
    return getDefaultData();
  }
}

function getDefaultData(): SkillsData {
  return {
    skills: [],
    metadata: {
      lastUpdated: new Date().toISOString(),
      totalSkills: 0,
      platforms: {
        'skills.sh': 0,
        'clawhub.ai': 0,
        'xiaping.coze.site': 0,
        'skillhub.tencent.com': 0,
      },
    },
  };
}
