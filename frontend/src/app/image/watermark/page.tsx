'use client';

import { MainLayout } from '@/components/layout/MainLayout';
import { ComingSoon } from '@/components/features/ComingSoon';

export default function WatermarkPage() {
  return (
    <MainLayout>
      <ComingSoon
        title="Image Watermark"
        message="Add text or image watermarks to your photos"
      />
    </MainLayout>
  );
}
