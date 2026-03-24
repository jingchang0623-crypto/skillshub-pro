'use client';

import { Platform, PLATFORM_DISPLAY_NAMES, PLATFORM_COLORS } from '@/types/skill';

interface PlatformFilterProps {
  platforms: Record<Platform, number>;
  selected: Platform | 'all';
  onChange: (platform: Platform | 'all') => void;
}

export default function PlatformFilter({ platforms, selected, onChange }: PlatformFilterProps) {
  const total = Object.values(platforms).reduce((a, b) => a + b, 0);

  return (
    <div className="flex flex-wrap gap-3 justify-center">
      <button
        onClick={() => onChange('all')}
        className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
          selected === 'all'
            ? 'bg-white text-gray-900'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
        }`}
      >
        全部 ({total})
      </button>
      {(Object.keys(platforms) as Platform[]).map((platform) => {
        const count = platforms[platform];
        const displayName = PLATFORM_DISPLAY_NAMES[platform];
        const gradient = PLATFORM_COLORS[platform];
        
        return (
          <button
            key={platform}
            onClick={() => onChange(platform)}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              selected === platform
                ? `bg-gradient-to-r ${gradient} text-white shadow-lg`
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {displayName} ({count})
          </button>
        );
      })}
    </div>
  );
}
