import { MainLayout } from '@/components/layout/MainLayout';
import { ComingSoon } from '@/components/features/ComingSoon';

export default function TextToolsPage() {
  return (
    <MainLayout>
      <ComingSoon
        title="Text Processing Tools"
        message="Text tools including case conversion, formatting, encoding, sorting, and statistics will be implemented in P2 phase. All processing will be done locally in your browser for privacy."
        estimatedRelease="P2 Phase"
      />
    </MainLayout>
  );
}
