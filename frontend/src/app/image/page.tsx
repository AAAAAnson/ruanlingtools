'use client';

import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { Image, Wand2, Scissors, FileImage } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { pageTransitions, listContainerAnimation, listItemAnimation } from '@/lib/animations';

const imageTools = [
  {
    id: 'convert',
    name: 'Format Converter',
    description: 'Convert images between JPG, PNG, WebP formats',
    icon: FileImage,
    status: 'available',
    href: '/image/convert',
    color: '#FF6B6B',
  },
  {
    id: 'resize',
    name: 'Resize & Compress',
    description: 'Resize images and reduce file size',
    icon: Scissors,
    status: 'planned',
    href: '#',
    color: '#4ECDC4',
  },
  {
    id: 'watermark',
    name: 'Add Watermark',
    description: 'Add text or image watermarks',
    icon: Wand2,
    status: 'planned',
    href: '/image/watermark',
    color: '#FFE66D',
  },
];

export default function ImageToolsPage() {
  return (
    <MainLayout>
      <motion.div
        variants={pageTransitions}
        initial="initial"
        animate="animate"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16"
      >
        <div className="text-center mb-12">
          <h1 className="font-pixel text-3xl md:text-4xl mb-4 text-gradient">
            Image Tools
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Process and transform your images with our pixel-perfect tools
          </p>
        </div>

        <motion.div
          variants={listContainerAnimation}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {imageTools.map((tool) => {
            const Icon = tool.icon;
            const isAvailable = tool.status === 'available';
            const opacityClass = isAvailable ? '' : 'opacity-60';

            return (
              <motion.div key={tool.id} variants={listItemAnimation}>
                <Link href={isAvailable ? tool.href : '#'}>
                  <PixelCard className={`h-full ${opacityClass}`}>
                    <div className="flex items-start gap-4 mb-4">
                      <div
                        className="w-12 h-12 pixel-border flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: tool.color + '20', borderColor: tool.color }}
                      >
                        <Icon style={{ color: tool.color }} className="w-6 h-6" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-pixel text-sm mb-2" style={{ color: tool.color }}>
                          {tool.name}
                        </h3>
                        <p className="text-xs text-gray-400">{tool.description}</p>
                      </div>
                    </div>
                    <div className="text-xs">
                      {isAvailable ? (
                        <span className="text-success">Available</span>
                      ) : (
                        <span className="text-accent">Coming Soon</span>
                      )}
                    </div>
                  </PixelCard>
                </Link>
              </motion.div>
            );
          })}
        </motion.div>
      </motion.div>
    </MainLayout>
  );
}
