import { SkillsData, Platform } from '@/types/skill';
import fs from 'fs';
import path from 'path';

// 在构建时数据路径为相对于项目根目录
const DATA_PATH = path.join(process.cwd(), 'data', 'skills.json');

export async function getSkillsData(): Promise<SkillsData> {
  try {
    if (!fs.existsSync(DATA_PATH)) {
      console.warn('Skills data file not found at:', DATA_PATH);
      return getDefaultData();
    }
    
    const fileContents = fs.readFileSync(DATA_PATH, 'utf8');
    const data = JSON.parse(fileContents);
    
    if (!data.skills || !Array.isArray(data.skills)) {
      console.warn('Invalid skills data structure');
      return getDefaultData();
    }
    
    return data;
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
      } as Record<Platform, number>,
    },
  };
}
