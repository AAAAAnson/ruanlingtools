'use client';

import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { Search, Youtube, TrendingUp, MessageSquare } from 'lucide-react';
import Link from 'next/link';

// Reddit Icon Component
const RedditIcon = ({ className, color }: { className?: string; color?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor" style={{ color }}>
    <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
  </svg>
);

const searchTools = [
  {
    id: 'youtube',
    name: 'YouTube KOL Search',
    description: 'Discover influential YouTube channels and analyze their performance metrics',
    icon: Youtube,
    path: '/search/youtube',
    color: '#FF0000',
    features: [
      'Search KOLs by keyword',
      'Analyze channel statistics',
      'View engagement rates',
      'Track video performance'
    ]
  },
  {
    id: 'reddit',
    name: 'Reddit Keyword Search',
    description: 'Search Reddit posts by keyword and export results to Excel spreadsheets',
    icon: RedditIcon,
    path: '/search/reddit',
    color: '#FF4500',
    features: [
      'Site-wide keyword search',
      'Filter by time range',
      'Export to Excel',
      'Filter promoted posts'
    ]
  }
];

export default function SearchToolsPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Search className="w-12 h-12 text-primary" />
            <h1 className="font-pixel text-4xl text-primary">Search Tools</h1>
          </div>
          <p className="text-gray-400 max-w-2xl mx-auto font-body">
            Powerful search tools to discover and analyze content across YouTube and Reddit platforms
          </p>
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {searchTools.map((tool) => {
            const Icon = tool.icon;
            return (
              <Link key={tool.id} href={tool.path}>
                <PixelCard className="h-full cursor-pointer transition-all hover:scale-[1.02]">
                  <div className="space-y-4">
                    {/* Tool Header */}
                    <div className="flex items-start gap-4">
                      <div
                        className="w-16 h-16 pixel-border flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: `${tool.color}20`, borderColor: tool.color }}
                      >
                        <Icon className="w-8 h-8" color={tool.color} />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-pixel text-xl mb-2" style={{ color: tool.color }}>
                          {tool.name}
                        </h3>
                        <p className="text-sm text-gray-400 font-body">
                          {tool.description}
                        </p>
                      </div>
                    </div>

                    {/* Features List */}
                    <div className="pt-4 border-t-2 border-gray-700">
                      <h4 className="font-pixel text-xs text-gray-500 mb-3">KEY FEATURES</h4>
                      <ul className="space-y-2">
                        {tool.features.map((feature, idx) => (
                          <li key={idx} className="flex items-center gap-2 text-sm text-gray-300 font-body">
                            <span className="text-primary">▸</span>
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* CTA */}
                    <div className="pt-4 flex items-center justify-between">
                      <span className="text-xs text-success font-pixel">Available Now</span>
                      <div className="flex items-center gap-2 text-primary">
                        <span className="text-sm font-pixel">Explore Tool</span>
                        <span className="text-xl">→</span>
                      </div>
                    </div>
                  </div>
                </PixelCard>
              </Link>
            );
          })}
        </div>

        {/* Info Section */}
        <PixelCard className="bg-gradient-to-r from-blue-500/10 to-purple-500/10" hoverable={false}>
          <div className="flex items-start gap-4">
            <TrendingUp className="text-primary mt-1 flex-shrink-0" size={24} />
            <div>
              <h3 className="font-pixel text-lg mb-3 text-primary">About Search Tools</h3>
              <div className="space-y-2 text-sm text-gray-300 font-body">
                <p>
                  <strong className="text-secondary">YouTube KOL Search:</strong> Find influential content creators,
                  analyze their channel performance, subscriber counts, engagement rates, and video statistics.
                  Perfect for marketing research and influencer discovery.
                </p>
                <p>
                  <strong className="text-accent">Reddit Keyword Search:</strong> Search across all of Reddit
                  for posts matching your keywords. Filter by time range, score, and comments. Export results
                  to Excel for further analysis. Ideal for market research and trend analysis.
                </p>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-700">
                <h4 className="font-pixel text-xs text-gray-500 mb-2">REQUIREMENTS</h4>
                <p className="text-xs text-gray-400">
                  Both tools require API credentials configured in{' '}
                  <Link href="/settings" className="text-primary hover:underline">
                    Settings
                  </Link>
                  . Free API keys are available for personal use.
                </p>
              </div>
            </div>
          </div>
        </PixelCard>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 mt-8">
          <PixelCard className="text-center" hoverable={false}>
            <Youtube className="w-8 h-8 mx-auto mb-2 text-[#FF0000]" />
            <div className="font-pixel text-2xl text-primary mb-1">YouTube</div>
            <div className="text-xs text-gray-400">Channel Analysis & KOL Discovery</div>
          </PixelCard>

          <PixelCard className="text-center" hoverable={false}>
            <MessageSquare className="w-8 h-8 mx-auto mb-2 text-[#FF4500]" />
            <div className="font-pixel text-2xl text-primary mb-1">Reddit</div>
            <div className="text-xs text-gray-400">Post Search & Data Export</div>
          </PixelCard>
        </div>
      </div>
    </MainLayout>
  );
}
