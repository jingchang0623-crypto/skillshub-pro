export interface Skill {
  id: string;
  name: string;
  description: string;
  tags: string[];
  platform: Platform;
  author: string;
  url: string;
  stars: number;
  createdAt: string;
}

export type Platform = 'skills.sh' | 'clawhub.ai' | 'xiaping.coze.site' | 'skillhub.tencent.com';

export interface SkillsData {
  skills: Skill[];
  metadata: {
    lastUpdated: string;
    totalSkills: number;
    platforms: Record<Platform, number>;
  };
}

export const PLATFORM_DISPLAY_NAMES: Record<Platform, string> = {
  'skills.sh': 'Skills.sh',
  'clawhub.ai': 'ClawHub',
  'xiaping.coze.site': 'Coze',
  'skillhub.tencent.com': 'Tencent SkillHub',
};

export const PLATFORM_COLORS: Record<Platform, string> = {
  'skills.sh': 'from-blue-500 to-blue-600',
  'clawhub.ai': 'from-purple-500 to-purple-600',
  'xiaping.coze.site': 'from-green-500 to-green-600',
  'skillhub.tencent.com': 'from-orange-500 to-orange-600',
};
