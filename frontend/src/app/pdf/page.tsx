import { MainLayout } from '@/components/layout/MainLayout';
import { ComingSoon } from '@/components/features/ComingSoon';

export default function PDFToolsPage() {
  return (
    <MainLayout>
      <ComingSoon
        title="PDF Tools"
        message="PDF processing tools including merge, split, compress, convert to Word, and text extraction will be implemented in P3 phase."
        estimatedRelease="P3 Phase"
      />
    </MainLayout>
  );
}
