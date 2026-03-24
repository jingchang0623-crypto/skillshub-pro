export interface PlatformData {
  id: string;
  url: string;
  rating: number;
  downloads: number;
  author: string;
  updated_at: string;
  reviews?: Review[];
  reviews_count: number;
}

export interface Review {
  user: string;
  rating: number;
  content: string;
  date: string;
}

export interface Skill {
  name: string;
  description: string;
  tags: string[];
  platforms: Record<string, PlatformData>;
  aggregated: {
    total_downloads: number;
    avg_rating: number;
    platform_count: number;
  };
}

export type Platform = 'xiaping.coze.site' | 'clawhub.ai' | 'skills.sh' | 'skillhub.tencent.com';

export interface SkillsData {
  metadata: {
    last_updated: string;
    total_skills: number;
    platforms: Record<string, number>;
  };
  skills: Skill[];
}

export const PLATFORM_DISPLAY_NAMES: Record<string, string> = {
  'xiaping.coze.site': '虾评Skill',
  'clawhub.ai': 'ClawHub',
  'skills.sh': 'Skills.sh',
  'skillhub.tencent.com': '腾讯SkillHub',
};

export const PLATFORM_COLORS: Record<string, string> = {
  'xiaping.coze.site': 'from-green-500 to-green-600',
  'clawhub.ai': 'from-purple-500 to-purple-600',
  'skills.sh': 'from-blue-500 to-blue-600',
  'skillhub.tencent.com': 'from-orange-500 to-orange-600',
};
