import { SkillsData } from '@/types/skill';
import fs from 'fs';
import path from 'path';

const DATA_PATH = path.join(process.cwd(), 'data', 'skills_aggregated.json');

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
    metadata: {
      last_updated: new Date().toISOString(),
      total_skills: 0,
      platforms: {},
    },
    skills: [],
  };
}
