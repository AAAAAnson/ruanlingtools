'use client';

import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import {
  FileText,
  Type,
  AlignLeft,
  Code2,
  ArrowUpDown,
  BarChart3
} from 'lucide-react';
import Link from 'next/link';

const textTools = [
  {
    id: 'case-converter',
    name: 'Case Converter',
    description: 'Convert text between different cases (UPPER, lower, Title, camelCase, etc.)',
    icon: Type,
    path: '/text/case-converter',
    color: '#FF6B6B'
  },
  {
    id: 'formatter',
    name: 'Text Formatter',
    description: 'Format and clean text (trim, remove duplicates, add line numbers)',
    icon: AlignLeft,
    path: '/text/formatter',
    color: '#4ECDC4'
  },
  {
    id: 'encoder',
    name: 'Text Encoder',
    description: 'Encode and decode text (Base64, URL, HTML entities)',
    icon: Code2,
    path: '/text/encoder',
    color: '#FFE66D'
  },
  {
    id: 'sorter',
    name: 'Text Sorter',
    description: 'Sort lines alphabetically, numerically, or in reverse',
    icon: ArrowUpDown,
    path: '/text/sorter',
    color: '#51CF66'
  },
  {
    id: 'statistics',
    name: 'Text Statistics',
    description: 'Analyze text and get detailed statistics (words, characters, lines)',
    icon: BarChart3,
    path: '/text/statistics',
    color: '#FF6B6B'
  }
];

export default function TextToolsPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary">Text Processing Tools</h1>
          <p className="text-pixel-text-secondary">
            All text processing is done locally in your browser for privacy. No data is sent to the server.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {textTools.map((tool) => {
            const Icon = tool.icon;
            return (
              <Link key={tool.id} href={tool.path}>
                <PixelCard
                  className="h-full cursor-pointer hover:border-pixel-primary transition-colors"
                >
                    <div className="flex items-start gap-4">
                      <div
                        className="p-3 rounded pixel-border"
                        style={{ backgroundColor: `${tool.color}20` }}
                      >
                        <Icon size={24} style={{ color: tool.color }} />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-pixel mb-2">{tool.name}</h3>
                        <p className="text-sm text-pixel-text-secondary">
                          {tool.description}
                        </p>
                      </div>
                    </div>
                </PixelCard>
              </Link>
            );
          })}
        </div>

        <div className="mt-12 pixel-border p-6 bg-pixel-background-light">
          <div className="flex items-start gap-3">
            <FileText className="text-pixel-primary mt-1" size={20} />
            <div>
              <h3 className="font-pixel text-sm mb-2">Privacy Notice</h3>
              <p className="text-sm text-pixel-text-secondary">
                All text processing tools work entirely in your browser using JavaScript.
                Your text never leaves your device and is not stored anywhere.
                This ensures complete privacy for sensitive content.
              </p>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
