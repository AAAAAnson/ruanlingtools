import { MainLayout } from '@/components/layout/MainLayout';
import { ComingSoon } from '@/components/features/ComingSoon';

export default function ImageConvertPage() {
  return (
    <MainLayout>
      <ComingSoon
        title="Image Format Converter"
        message="Convert images between different formats with batch processing support. This feature will be implemented in P1 phase with support for JPG, PNG, WebP, and AVIF formats."
        estimatedRelease="P1 Phase"
      />
    </MainLayout>
  );
}
