'use client';

import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import {
  File,
  FileImage,
  FilePlus,
  FileText,
  Split,
  Info
} from 'lucide-react';
import Link from 'next/link';

const pdfTools = [
  {
    id: 'to-images',
    name: 'PDF to Images',
    description: 'Convert PDF pages to image files (PNG, JPG)',
    icon: FileImage,
    path: '/pdf/to-images',
    color: '#FF6B6B'
  },
  {
    id: 'merge',
    name: 'Merge PDFs',
    description: 'Combine multiple PDF files into one document',
    icon: FilePlus,
    path: '/pdf/merge',
    color: '#4ECDC4'
  },
  {
    id: 'split',
    name: 'Split PDF',
    description: 'Split PDF into multiple files by page ranges',
    icon: Split,
    path: '/pdf/split',
    color: '#FFE66D'
  },
  {
    id: 'extract-text',
    name: 'Extract Text',
    description: 'Extract text content from PDF documents',
    icon: FileText,
    path: '/pdf/extract-text',
    color: '#51CF66'
  },
  {
    id: 'info',
    name: 'PDF Info',
    description: 'View PDF metadata and document information',
    icon: Info,
    path: '/pdf/info',
    color: '#FF6B6B'
  }
];

export default function PDFToolsPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary">PDF Processing Tools</h1>
          <p className="text-pixel-text-secondary">
            Professional PDF tools for conversion, merging, splitting, and text extraction.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pdfTools.map((tool) => {
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
            <File className="text-pixel-primary mt-1" size={20} />
            <div>
              <h3 className="font-pixel text-sm mb-2">Supported Features</h3>
              <ul className="text-sm text-pixel-text-secondary space-y-1">
                <li>• Convert PDF pages to high-quality images</li>
                <li>• Merge multiple PDFs while preserving formatting</li>
                <li>• Split large PDFs into smaller documents</li>
                <li>• Extract text content for editing or analysis</li>
                <li>• View detailed PDF metadata and properties</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
