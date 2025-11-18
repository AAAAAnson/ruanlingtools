'use client';

import { Construction } from 'lucide-react';
import { PixelCard } from '@/components/ui/PixelCard';

export default function WatermarkPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-pixel mb-8 text-center">
          Image Watermark
        </h1>

        <PixelCard className="text-center py-12">
          <Construction className="w-16 h-16 mx-auto mb-4 text-yellow-500" />
          <h2 className="text-xl font-pixel mb-4">Coming Soon</h2>
          <p className="text-gray-400">
            The image watermark feature is under development.
          </p>
          <p className="text-sm text-gray-500 mt-4">
            This feature will allow you to add text or image watermarks to your photos.
          </p>
        </PixelCard>
      </div>
    </div>
  );
}
