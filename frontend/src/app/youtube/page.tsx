import { MainLayout } from '@/components/layout/MainLayout';
import { ComingSoon } from '@/components/features/ComingSoon';

export default function YouTubePage() {
  return (
    <MainLayout>
      <ComingSoon
        title="YouTube KOL Search"
        message="YouTube channel search and analytics features are coming soon. Search for influential creators, analyze channel statistics, and discover trending content."
        estimatedRelease="Future Phase"
      />
    </MainLayout>
  );
}
