'use client';

import { Skill, PLATFORM_DISPLAY_NAMES, PLATFORM_COLORS } from '@/types/skill';
import { useState } from 'react';

interface SkillCardProps {
  skill: Skill;
}

export default function SkillCard({ skill }: SkillCardProps) {
  const [expanded, setExpanded] = useState(false);
  
  const platformCount = skill.aggregated.platform_count;
  const totalDownloads = skill.aggregated.total_downloads;
  const avgRating = skill.aggregated.avg_rating;
  
  return (
    <div 
      className="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-gray-600 transition-all cursor-pointer"
      onClick={() => setExpanded(!expanded)}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-lg text-white line-clamp-1 flex-1">
          {skill.name}
        </h3>
        {avgRating > 0 && (
          <div className="flex items-center gap-1 text-yellow-400 text-sm">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            {avgRating.toFixed(1)}
          </div>
        )}
      </div>
      
      {/* Description */}
      <p className="text-gray-400 text-sm line-clamp-2 mb-3">
        {skill.description || '暂无描述'}
      </p>
      
      {/* Stats */}
      <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
        <div className="flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          {totalDownloads.toLocaleString()} 下载
        </div>
        <div className="flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          {platformCount} 平台
        </div>
      </div>
      
      {/* Tags */}
      <div className="flex flex-wrap gap-1 mb-3">
        {skill.tags.slice(0, 3).map((tag) => (
          <span key={tag} className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded text-xs">
            {tag}
          </span>
        ))}
        {skill.tags.length > 3 && (
          <span className="text-gray-500 text-xs">+{skill.tags.length - 3}</span>
        )}
      </div>
      
      {/* Platform indicators */}
      <div className="flex gap-2">
        {Object.entries(skill.platforms).map(([platform, data]) => (
          <a
            key={platform}
            href={data.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className={`px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${PLATFORM_COLORS[platform] || 'from-gray-500 to-gray-600'} text-white hover:opacity-80`}
          >
            {PLATFORM_DISPLAY_NAMES[platform] || platform}
            {data.rating > 0 && ` · ${data.rating.toFixed(1)}★`}
          </a>
        ))}
      </div>
      
      {/* Expanded details */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <h4 className="text-sm font-medium text-gray-300 mb-2">平台详情</h4>
          {Object.entries(skill.platforms).map(([platform, data]) => (
            <div key={platform} className="mb-3 p-3 bg-gray-900 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-white">
                  {PLATFORM_DISPLAY_NAMES[platform]}
                </span>
                <a
                  href={data.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 text-sm"
                >
                  访问 →
                </a>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                <div>评分: <span className="text-yellow-400">{data.rating.toFixed(1)}</span></div>
                <div>下载: {data.downloads.toLocaleString()}</div>
                <div>作者: {data.author || '未知'}</div>
                <div>更新: {new Date(data.updated_at).toLocaleDateString()}</div>
              </div>
              {data.reviews && data.reviews.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-800">
                  <div className="text-xs text-gray-500 mb-1">最新评价:</div>
                  {data.reviews.slice(0, 2).map((review, i) => (
                    <div key={i} className="text-xs text-gray-400 mb-1">
                      <span className="text-yellow-400">{review.rating}★</span> {review.content.slice(0, 50)}...
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
