'use client';

import { PixelCard } from '@/components/ui/PixelCard';
import { motion } from 'framer-motion';
import { listContainerAnimation, listItemAnimation } from '@/lib/animations';

interface TextStatsProps {
  text: string;
}

interface StatItem {
  label: string;
  value: number | string;
  color: string;
}

export function TextStats({ text }: TextStatsProps) {
  // Calculate statistics
  const characters = text.length;
  const charactersNoSpaces = text.replace(/\s/g, '').length;
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const lines = text.split('\n').length;
  const sentences = (text.match(/[.!?]+/g) || []).length;
  const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim()).length;
  
  // Average calculations
  const avgWordLength = words > 0 ? (charactersNoSpaces / words).toFixed(1) : '0';
  const avgWordsPerSentence = sentences > 0 ? (words / sentences).toFixed(1) : '0';

  const stats: StatItem[] = [
    { label: 'Characters', value: characters, color: '#FF6B6B' },
    { label: 'Characters (no spaces)', value: charactersNoSpaces, color: '#4ECDC4' },
    { label: 'Words', value: words, color: '#FFE66D' },
    { label: 'Lines', value: lines, color: '#51CF66' },
    { label: 'Sentences', value: sentences, color: '#FF6B6B' },
    { label: 'Paragraphs', value: paragraphs, color: '#4ECDC4' },
    { label: 'Avg. word length', value: avgWordLength, color: '#FFE66D' },
    { label: 'Avg. words/sentence', value: avgWordsPerSentence, color: '#51CF66' },
  ];

  return (
    <PixelCard title="Text Statistics">
      <motion.div
        variants={listContainerAnimation}
        initial="hidden"
        animate="show"
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {stats.map((stat, index) => (
          <motion.div
            key={index}
            variants={listItemAnimation}
            className="text-center"
          >
            <div
              className="font-pixel text-2xl md:text-3xl mb-2"
              style={{ color: stat.color }}
            >
              {stat.value}
            </div>
            <div className="text-xs text-gray-400">{stat.label}</div>
          </motion.div>
        ))}
      </motion.div>
    </PixelCard>
  );
}
