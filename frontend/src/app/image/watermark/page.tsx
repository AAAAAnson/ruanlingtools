'use client';

import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { Droplet } from 'lucide-react';

export default function WatermarkPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary">Image Watermark</h1>
          <p className="text-pixel-text-secondary">
            Add watermarks to your images
          </p>
        </div>

        <PixelCard title="Watermark Tool" icon={<Droplet size={20} />}>
          <div className="text-center py-12">
            <Droplet size={48} className="mx-auto mb-4 text-pixel-text-secondary opacity-50" />
            <p className="text-pixel-text-secondary">
              Watermark feature coming soon...
            </p>
          </div>
        </PixelCard>
      </div>
    </MainLayout>
  );
}
