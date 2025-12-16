'use client';

import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { Mic, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function AudioToolsPage() {
  const tools = [
    {
      title: 'Speech to Text',
      description: 'Convert audio files to text using Whisper AI. Supports 99+ languages with high accuracy.',
      href: '/audio/transcribe',
      icon: Mic,
      features: [
        'Multiple models (Tiny/Base/Small)',
        'Auto language detection',
        'SRT/VTT subtitle export',
        'Batch processing'
      ],
      status: 'available'
    }
  ];

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient">Audio Tools</h1>
          <p className="text-gray-300">
            AI-powered audio processing tools for transcription and analysis
          </p>
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tools.map((tool, index) => {
            const Icon = tool.icon;
            return (
              <Link key={index} href={tool.href}>
                <PixelCard className="h-full hover:border-primary transition-colors cursor-pointer">
                  <div className="flex flex-col h-full">
                    {/* Icon & Title */}
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-primary/10 rounded border border-primary/30">
                        <Icon size={24} className="text-primary" />
                      </div>
                      <h2 className="font-pixel text-lg text-primary">{tool.title}</h2>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-gray-300 mb-4 flex-1">
                      {tool.description}
                    </p>

                    {/* Features */}
                    <ul className="space-y-1 mb-4">
                      {tool.features.map((feature, i) => (
                        <li key={i} className="text-xs text-gray-400 flex items-center gap-2">
                          <div className="w-1 h-1 bg-secondary rounded-full"></div>
                          {feature}
                        </li>
                      ))}
                    </ul>

                    {/* Status & Arrow */}
                    <div className="flex items-center justify-between pt-3 border-t border-[#333344]">
                      <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded border border-green-500/30">
                        Available
                      </span>
                      <ArrowRight size={16} className="text-primary" />
                    </div>
                  </div>
                </PixelCard>
              </Link>
            );
          })}

          {/* Coming Soon Cards */}
          <PixelCard className="opacity-50">
            <div className="flex flex-col h-full">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-gray-500/10 rounded border border-gray-500/30">
                  <Mic size={24} className="text-gray-500" />
                </div>
                <h2 className="font-pixel text-lg text-gray-500">Audio Enhancement</h2>
              </div>
              <p className="text-sm text-gray-500 mb-4 flex-1">
                Remove noise and enhance audio quality
              </p>
              <div className="flex items-center justify-between pt-3 border-t border-[#333344]">
                <span className="text-xs px-2 py-1 bg-gray-500/20 text-gray-400 rounded border border-gray-500/30">
                  Coming Soon
                </span>
              </div>
            </div>
          </PixelCard>

          <PixelCard className="opacity-50">
            <div className="flex flex-col h-full">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-gray-500/10 rounded border border-gray-500/30">
                  <Mic size={24} className="text-gray-500" />
                </div>
                <h2 className="font-pixel text-lg text-gray-500">Audio Converter</h2>
              </div>
              <p className="text-sm text-gray-500 mb-4 flex-1">
                Convert between audio formats (MP3, WAV, FLAC, etc.)
              </p>
              <div className="flex items-center justify-between pt-3 border-t border-[#333344]">
                <span className="text-xs px-2 py-1 bg-gray-500/20 text-gray-400 rounded border border-gray-500/30">
                  Coming Soon
                </span>
              </div>
            </div>
          </PixelCard>
        </div>

        {/* Info Section */}
        <div className="mt-12">
          <PixelCard>
            <h2 className="font-pixel text-lg text-primary mb-4">About Audio Tools</h2>
            <div className="space-y-3 text-sm text-gray-300">
              <p>
                Our audio tools use state-of-the-art AI models to process your audio files locally on your NAS,
                ensuring privacy and security.
              </p>
              <p>
                <strong className="text-white">Speech to Text</strong> uses OpenAI's Whisper model, optimized for
                systems with 4GB RAM. Choose from three model sizes based on your needs:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-400 ml-4">
                <li><strong className="text-white">Tiny</strong> - Fastest processing, good for quick previews</li>
                <li><strong className="text-white">Base</strong> - Balanced speed and accuracy (recommended)</li>
                <li><strong className="text-white">Small</strong> - Highest quality, slower processing</li>
              </ul>
            </div>
          </PixelCard>
        </div>
      </div>
    </MainLayout>
  );
}
