import { getSkillsData } from '@/lib/data';
import HomePage from '@/components/HomePage';

export default async function Home() {
  const data = await getSkillsData();
  
  return <HomePage skills={data.skills} metadata={data.metadata} />;
}
