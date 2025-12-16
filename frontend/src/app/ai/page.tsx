'use client';

import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { Wand2, Mic, ImageIcon, Eraser, Sparkles } from 'lucide-react';
import Link from 'next/link';

const aiTools = [
  {
    id: 'speech-to-text',
    name: 'Speech to Text',
    description: 'Convert audio files to text using OpenAI Whisper AI. Supports 99+ languages.',
    icon: Mic,
    path: '/ai/speech-to-text',
    color: '#51CF66',
    status: 'available',
    badge: 'New'
  },
  {
    id: 'text-to-image',
    name: 'Text to Image',
    description: 'Generate images from text descriptions using AI',
    icon: ImageIcon,
    path: '#',
    color: '#FF6B6B',
    status: 'planned'
  },
  {
    id: 'background-removal',
    name: 'Background Removal',
    description: 'Remove backgrounds from images automatically',
    icon: Eraser,
    path: '#',
    color: '#4ECDC4',
    status: 'planned'
  },
  {
    id: 'image-enhancement',
    name: 'Image Enhancement',
    description: 'Enhance image quality with AI upscaling',
    icon: Sparkles,
    path: '#',
    color: '#FFE66D',
    status: 'planned'
  }
];

export default function AIToolsPage() {
  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h1 className="font-pixel text-3xl md:text-4xl mb-4 text-gradient">
            AI Tools
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Powerful AI-powered tools for audio transcription, image generation, and enhancement
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {aiTools.map((tool) => {
            const Icon = tool.icon;
            const isAvailable = tool.status === 'available';
            const opacityClass = isAvailable ? '' : 'opacity-60';

            return (
              <div key={tool.id}>
                <Link href={isAvailable ? tool.path : '#'}>
                  <PixelCard className={`h-full ${opacityClass} ${isAvailable ? 'hover:border-primary cursor-pointer' : 'cursor-not-allowed'}`}>
                    <div className="flex items-start gap-4 mb-4">
                      <div
                        className="w-12 h-12 pixel-border flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: tool.color + '20', borderColor: tool.color }}
                      >
                        <Icon style={{ color: tool.color }} className="w-6 h-6" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-pixel text-sm" style={{ color: tool.color }}>
                            {tool.name}
                          </h3>
                          {tool.badge && isAvailable && (
                            <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded border border-green-500/30 font-pixel">
                              {tool.badge}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-400">{tool.description}</p>
                      </div>
                    </div>
                    <div className="text-xs">
                      {isAvailable ? (
                        <span className="text-green-400 flex items-center gap-1">
                          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                          Available
                        </span>
                      ) : (
                        <span className="text-gray-500 flex items-center gap-1">
                          <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                          Coming Soon
                        </span>
                      )}
                    </div>
                  </PixelCard>
                </Link>
              </div>
            );
          })}
        </div>

        {/* Info Section */}
        <div className="mt-12">
          <PixelCard>
            <div className="flex items-start gap-3">
              <Wand2 className="text-primary mt-1 flex-shrink-0" size={20} />
              <div>
                <h3 className="font-pixel text-sm mb-2 text-primary">About AI Tools</h3>
                <p className="text-sm text-gray-400 mb-3">
                  Our AI tools use state-of-the-art machine learning models to process your content.
                  Speech to Text uses OpenAI's Whisper model running locally on your NAS, ensuring
                  privacy and security.
                </p>
                <div className="space-y-1 text-xs text-gray-500">
                  <p>• All processing happens on your device or local server</p>
                  <p>• No data is sent to external services</p>
                  <p>• Models are optimized for systems with 4GB RAM</p>
                </div>
              </div>
            </div>
          </PixelCard>
        </div>
      </div>
    </MainLayout>
  );
}
