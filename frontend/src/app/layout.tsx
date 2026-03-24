import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'SkillsHub Pro - 技能聚合平台',
  description: '整合 Skills.sh、ClawHub、Coze、Tencent SkillHub 四大平台的技能聚合平台',
  keywords: ['skills', 'AI', 'agent', 'platform', '技能', '工具'],
  authors: [{ name: 'SkillsHub Pro' }],
  openGraph: {
    title: 'SkillsHub Pro - 技能聚合平台',
    description: '整合 Skills.sh、ClawHub、Coze、Tencent SkillHub 四大平台的技能聚合平台',
    type: 'website',
    url: 'https://skillsagent.org',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className="dark">
      <body className={`${inter.className} bg-gray-900 text-white antialiased`}>
        {children}
      </body>
    </html>
  );
}
