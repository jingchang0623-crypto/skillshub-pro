'use client';

import { useState, useMemo } from 'react';
import { Skill, Platform } from '@/types/skill';
import SkillCard from '@/components/SkillCard';
import SearchBar from '@/components/SearchBar';
import PlatformFilter from '@/components/PlatformFilter';
import Pagination from '@/components/Pagination';

const ITEMS_PER_PAGE = 12;

interface HomePageProps {
  skills: Skill[];
  platformStats: Record<Platform, number>;
}

export default function HomePage({ skills, platformStats }: HomePageProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | 'all'>('all');
  const [currentPage, setCurrentPage] = useState(1);

  // 过滤和搜索
  const filteredSkills = useMemo(() => {
    return skills.filter((skill) => {
      // 平台筛选
      if (selectedPlatform !== 'all' && skill.platform !== selectedPlatform) {
        return false;
      }

      // 搜索
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          skill.name.toLowerCase().includes(query) ||
          skill.description.toLowerCase().includes(query) ||
          skill.tags.some((tag) => tag.toLowerCase().includes(query))
        );
      }

      return true;
    });
  }, [skills, selectedPlatform, searchQuery]);

  // 分页
  const totalPages = Math.ceil(filteredSkills.length / ITEMS_PER_PAGE);
  const paginatedSkills = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredSkills.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredSkills, currentPage]);

  // 重置页码
  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handlePlatformChange = (platform: Platform | 'all') => {
    setSelectedPlatform(platform);
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center mb-6">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
              SkillsHub Pro
            </h1>
            <p className="text-gray-400 text-sm">
              整合 Skills.sh、ClawHub、Coze、Tencent SkillHub 四大平台的技能聚合平台
            </p>
          </div>
          <SearchBar value={searchQuery} onChange={handleSearchChange} />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Platform Filter */}
        <div className="mb-8">
          <PlatformFilter
            platforms={platformStats}
            selected={selectedPlatform}
            onChange={handlePlatformChange}
          />
        </div>

        {/* Results Count */}
        <div className="text-center mb-6 text-gray-400 text-sm">
          找到 <span className="text-white font-medium">{filteredSkills.length}</span> 个技能
        </div>

        {/* Skills Grid */}
        {paginatedSkills.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {paginatedSkills.map((skill) => (
                <SkillCard key={skill.id} skill={skill} />
              ))}
            </div>

            {/* Pagination */}
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          </>
        ) : (
          <div className="text-center py-16">
            <div className="text-gray-500 text-lg mb-2">未找到匹配的技能</div>
            <div className="text-gray-600 text-sm">尝试调整搜索条件或平台筛选</div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-gray-900/50 mt-16">
        <div className="container mx-auto px-4 py-8 text-center text-gray-500 text-sm">
          <div className="mb-2">
            Powered by Next.js + Tailwind CSS
          </div>
          <div>
            © 2024 SkillsHub Pro · 
            <a href="https://skillsagent.org" className="text-blue-400 hover:text-blue-300 ml-1">
              skillsagent.org
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
