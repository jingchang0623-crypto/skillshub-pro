'use client';

import { useState, useMemo } from 'react';
import { Skill, SkillsData } from '@/types/skill';
import SkillCard from '@/components/SkillCard';
import SearchBar from '@/components/SearchBar';

const ITEMS_PER_PAGE = 12;

interface HomePageProps {
  skills: Skill[];
  metadata: SkillsData['metadata'];
}

export default function HomePage({ skills, metadata }: HomePageProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // 过滤和搜索
  const filteredSkills = useMemo(() => {
    return skills.filter((skill) => {
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
  }, [skills, searchQuery]);

  // 分页
  const totalPages = Math.ceil(filteredSkills.length / ITEMS_PER_PAGE);
  const paginatedSkills = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredSkills.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredSkills, currentPage]);

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
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
            <p className="text-gray-400 text-sm mb-2">
              全网技能聚合平台 - 一站式发现、比较、评价
            </p>
            <div className="text-xs text-gray-500">
              共收录 <span className="text-white">{metadata.total_skills}</span> 个技能 · 
              更新于 {new Date(metadata.last_updated).toLocaleString()}
            </div>
          </div>
          <SearchBar value={searchQuery} onChange={handleSearchChange} />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Results Count */}
        <div className="text-center mb-6 text-gray-400 text-sm">
          找到 <span className="text-white font-medium">{filteredSkills.length}</span> 个技能
        </div>

        {/* Skills Grid */}
        {paginatedSkills.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {paginatedSkills.map((skill, index) => (
                <SkillCard key={skill.name + index} skill={skill} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2 mt-8">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700"
                >
                  上一页
                </button>
                <span className="px-4 py-2 text-gray-400">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700"
                >
                  下一页
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-16">
            <div className="text-gray-500 text-lg mb-2">未找到匹配的技能</div>
            <div className="text-gray-600 text-sm">尝试调整搜索条件</div>
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
            © 2026 SkillsHub Pro · 
            <a href="https://skillsagent.org" className="text-blue-400 hover:text-blue-300 ml-1">
              skillsagent.org
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
