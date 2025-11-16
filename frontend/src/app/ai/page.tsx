import { MainLayout } from '@/components/layout/MainLayout';
import { ComingSoon } from '@/components/features/ComingSoon';

export default function AIToolsPage() {
  return (
    <MainLayout>
      <ComingSoon
        title="AI Tools"
        message="AI-powered features including text-to-image generation, background removal, and image enhancement are coming soon. These features will require API integration and will be available in future updates."
        estimatedRelease="Future Phase"
      />
    </MainLayout>
  );
}
