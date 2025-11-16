'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { Info, Upload, FileText, Calendar, User, FileType } from 'lucide-react';

interface PDFInfo {
  num_pages: number;
  is_encrypted: boolean;
  metadata: {
    title: string;
    author: string;
    subject: string;
    creator: string;
    producer: string;
    creation_date: string;
    modification_date: string;
  };
  page_size?: {
    width: number;
    height: number;
    unit: string;
  };
}

export default function PDFInfoPage() {
  const [file, setFile] = useState<File | null>(null);
  const [pdfInfo, setPdfInfo] = useState<PDFInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError('');
        setPdfInfo(null);
      } else {
        setError('Please select a PDF file');
      }
    }
  };

  const handleGetInfo = async () => {
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    setLoading(true);
    setError('');
    setPdfInfo(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/pdf/info', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setPdfInfo(result.data.info);
      } else {
        setError(result.message || 'Failed to get PDF info');
      }
    } catch (err) {
      setError('Network error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPdfInfo(null);
    setError('');
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    // PDF dates are in format D:YYYYMMDDHHmmSS
    if (dateStr.startsWith('D:')) {
      const year = dateStr.substring(2, 6);
      const month = dateStr.substring(6, 8);
      const day = dateStr.substring(8, 10);
      const hour = dateStr.substring(10, 12);
      const minute = dateStr.substring(12, 14);
      return `${year}-${month}-${day} ${hour}:${minute}`;
    }
    return dateStr;
  };

  const InfoRow = ({ label, value, icon: Icon }: { label: string; value: string | number; icon?: any }) => (
    <div className="pixel-border p-3 bg-white dark:bg-gray-800 flex items-start gap-3">
      {Icon && <Icon className="text-pixel-primary flex-shrink-0 mt-0.5" size={18} />}
      <div className="flex-1">
        <p className="text-xs text-pixel-text-secondary mb-1">{label}</p>
        <p className="font-medium">{value || 'N/A'}</p>
      </div>
    </div>
  );

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <Info size={32} />
            PDF Information
          </h1>
          <p className="text-pixel-text-secondary">
            View detailed information and metadata about PDF files.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <PixelCard title="Upload PDF File">
              <div className="space-y-4">
                <label className="pixel-border block p-8 text-center cursor-pointer hover:bg-pixel-bg-secondary transition-colors">
                  <input
                    type="file"
                    accept="application/pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <Upload className="mx-auto mb-3 text-pixel-text-secondary" size={48} />
                  <p className="text-lg mb-2">Click to upload PDF file</p>
                  <p className="text-sm text-pixel-text-secondary">
                    or drag and drop a file here
                  </p>
                </label>

                {file && (
                  <div className="pixel-border p-4 bg-pixel-bg flex items-center gap-3">
                    <FileText className="text-pixel-primary" size={24} />
                    <div className="flex-1">
                      <p className="font-medium">{file.name}</p>
                      <p className="text-sm text-pixel-text-secondary">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="pixel-border p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400">
                    {error}
                  </div>
                )}

                <div className="flex gap-3">
                  <PixelButton
                    onClick={handleGetInfo}
                    disabled={!file || loading}
                  >
                    {loading ? 'Loading...' : 'Get PDF Info'}
                  </PixelButton>
                  {file && (
                    <PixelButton variant="secondary" onClick={handleReset}>
                      Reset
                    </PixelButton>
                  )}
                </div>
              </div>
            </PixelCard>

            {pdfInfo && (
              <>
                <PixelCard title="Document Properties">
                  <div className="space-y-2">
                    <InfoRow
                      label="Number of Pages"
                      value={pdfInfo.num_pages}
                      icon={FileText}
                    />
                    <InfoRow
                      label="Encrypted"
                      value={pdfInfo.is_encrypted ? 'Yes' : 'No'}
                      icon={Info}
                    />
                    {pdfInfo.page_size && (
                      <InfoRow
                        label="Page Size"
                        value={`${pdfInfo.page_size.width.toFixed(1)} × ${pdfInfo.page_size.height.toFixed(1)} ${pdfInfo.page_size.unit}`}
                        icon={FileType}
                      />
                    )}
                  </div>
                </PixelCard>

                <PixelCard title="Metadata">
                  <div className="space-y-2">
                    <InfoRow
                      label="Title"
                      value={pdfInfo.metadata.title}
                      icon={FileText}
                    />
                    <InfoRow
                      label="Author"
                      value={pdfInfo.metadata.author}
                      icon={User}
                    />
                    <InfoRow
                      label="Subject"
                      value={pdfInfo.metadata.subject}
                      icon={Info}
                    />
                    <InfoRow
                      label="Creator"
                      value={pdfInfo.metadata.creator}
                    />
                    <InfoRow
                      label="Producer"
                      value={pdfInfo.metadata.producer}
                    />
                    <InfoRow
                      label="Creation Date"
                      value={formatDate(pdfInfo.metadata.creation_date)}
                      icon={Calendar}
                    />
                    <InfoRow
                      label="Modification Date"
                      value={formatDate(pdfInfo.metadata.modification_date)}
                      icon={Calendar}
                    />
                  </div>
                </PixelCard>
              </>
            )}
          </div>

          <div className="space-y-6">
            <PixelCard title="How to Use">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>1. Upload a PDF file</p>
                <p>2. Click "Get PDF Info"</p>
                <p>3. View document properties and metadata</p>
              </div>
            </PixelCard>

            <PixelCard title="Information Shown">
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Document Properties</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Page count, encryption status, and page dimensions
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Metadata</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Title, author, subject, creator, producer, and dates
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Use Cases">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>• Check PDF page count before splitting</p>
                <p>• View document author and creation info</p>
                <p>• Verify PDF properties and metadata</p>
                <p>• Check if PDF is encrypted</p>
              </div>
            </PixelCard>

            <PixelCard title="Notes">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>• Not all PDFs contain metadata</p>
                <p>• Some fields may be empty</p>
                <p>• Date format: YYYY-MM-DD HH:mm</p>
                <p>• Page size is shown in points (1 point = 1/72 inch)</p>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
