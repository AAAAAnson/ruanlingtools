'use client';

import { Image, FileText, File, Wand2, Youtube, TrendingUp, ArrowRight, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';

const toolCategories = [
  {
    title: 'Image Tools',
    description: 'Convert, resize, and optimize images',
    icon: Image,
    href: '/image',
    color: '#FF6B6B',
    features: ['Format Conversion', 'Batch Processing', 'Watermark'],
  },
  {
    title: 'Text Tools',
    description: 'Format, transform, and analyze text',
    icon: FileText,
    href: '/text',
    color: '#4ECDC4',
    features: ['Case Converter', 'Formatter', 'Statistics'],
  },
  {
    title: 'PDF Tools',
    description: 'Merge, split, and convert PDFs',
    icon: File,
    href: '/pdf',
    color: '#FFE66D',
    features: ['Merge & Split', 'Compress', 'Extract Text'],
  },
  {
    title: 'AI Tools',
    description: 'AI-powered image generation',
    icon: Wand2,
    href: '/ai',
    color: '#51CF66',
    features: ['Text to Image', 'Background Removal', 'Coming Soon'],
  },
  {
    title: 'YouTube',
    description: 'Search and analyze YouTube content',
    icon: Youtube,
    href: '/youtube',
    color: '#FF6B6B',
    features: ['KOL Search', 'Channel Info', 'Coming Soon'],
  },
  {
    title: 'More Tools',
    description: 'Additional utilities coming soon',
    icon: Sparkles,
    href: '#',
    color: '#A78BFA',
    features: ['Stay Tuned', 'More Features', 'Updates'],
  },
];

const stats = [
  { label: 'Total Tools', value: '20+', color: '#FF6B6B' },
  { label: 'Categories', value: '5', color: '#4ECDC4' },
  { label: 'Free to Use', value: '100%', color: '#51CF66' },
];

export default function HomePage() {
  return (
    <MainLayout>
      <div className="min-h-screen">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          <div className="text-center">
            <div>
              <h1 className="font-pixel text-3xl md:text-5xl mb-6 text-gradient">
                Soft Collar Toolbox
              </h1>
              <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
                Your all-in-one pixel art themed toolbox for image processing,
                PDF manipulation, and text formatting
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/image">
                  <button className="pixel-btn pixel-btn-primary pixel-btn-lg flex items-center gap-2">
                    Get Started
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </Link>
                <Link href="#tools">
                  <button className="pixel-btn pixel-btn-secondary pixel-btn-lg">
                    Explore Tools
                  </button>
                </Link>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
            {stats.map((stat, index) => (
              <PixelCard key={index} className="text-center">
                <div className="font-pixel text-3xl mb-2" style={{ color: stat.color }}>
                  {stat.value}
                </div>
                <div className="text-sm text-gray-400">{stat.label}</div>
              </PixelCard>
            ))}
          </div>
        </section>

        {/* Tool Categories */}
        <section id="tools" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div>
            <h2 className="font-pixel text-2xl md:text-3xl text-center mb-12 text-secondary">
              Available Tools
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {toolCategories.map((category, index) => {
                const Icon = category.icon;
                return (
                  <div key={index}>
                    <Link href={category.href}>
                      <PixelCard className="h-full hover:border-primary cursor-pointer">
                        <div className="flex items-start gap-4 mb-4">
                          <div
                            className="w-12 h-12 pixel-border flex items-center justify-center flex-shrink-0"
                            style={{ backgroundColor: category.color + '20', borderColor: category.color }}
                          >
                            <Icon style={{ color: category.color }} className="w-6 h-6" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-pixel text-sm mb-2" style={{ color: category.color }}>
                              {category.title}
                            </h3>
                            <p className="text-xs text-gray-400">{category.description}</p>
                          </div>
                        </div>
                        <div className="space-y-1">
                          {category.features.map((feature, i) => (
                            <div key={i} className="text-xs text-gray-500 flex items-center gap-2">
                              <span className="w-1 h-1 bg-secondary" />
                              {feature}
                            </div>
                          ))}
                        </div>
                      </PixelCard>
                    </Link>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Recent Usage */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h2 className="font-pixel text-2xl md:text-3xl text-center mb-12 text-accent">
            Recent Activity
          </h2>
          <PixelCard className="text-center py-16">
            <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-600" />
            <p className="font-pixel text-sm text-gray-500 mb-2">No recent activity</p>
            <p className="text-xs text-gray-600">Start using tools to see your activity here</p>
          </PixelCard>
        </section>

        {/* Features */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <PixelCard>
              <h3 className="font-pixel text-sm text-primary mb-3">Local Processing</h3>
              <p className="text-sm text-gray-400">
                All processing happens locally on your device. Your data stays private and secure.
              </p>
            </PixelCard>
            <PixelCard>
              <h3 className="font-pixel text-sm text-secondary mb-3">Free Forever</h3>
              <p className="text-sm text-gray-400">
                All tools are completely free to use. No subscriptions, no hidden fees.
              </p>
            </PixelCard>
            <PixelCard>
              <h3 className="font-pixel text-sm text-accent mb-3">Pixel Art Style</h3>
              <p className="text-sm text-gray-400">
                Unique 8-bit game aesthetic with smooth animations and retro vibes.
              </p>
            </PixelCard>
          </div>
        </section>
      </div>
    </MainLayout>
  );
}
