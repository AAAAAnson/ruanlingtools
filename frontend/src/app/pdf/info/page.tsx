'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { Info, Upload, FileText, Calendar, User, FileType, Lock } from 'lucide-react';

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
    <div className="border-2 border-[#333344] p-3 bg-[#1A1A2E] rounded flex items-start gap-3">
      {Icon && <Icon className="text-[#4ECDC4] flex-shrink-0 mt-0.5" size={18} />}
      <div className="flex-1">
        <p className="text-xs text-gray-400 mb-1">{label}</p>
        <p className="font-medium text-sm">{value || 'N/A'}</p>
      </div>
    </div>
  );

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient flex items-center gap-3">
            <Info size={32} />
            PDF Information
          </h1>
          <p className="text-gray-300">
            View detailed information, properties, and metadata about PDF files
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content - 3 columns */}
          <div className="lg:col-span-3">
            {/* Single Unified Card */}
            <PixelCard hoverable={false}>
              {/* Header */}
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-pixel text-lg text-primary flex items-center gap-2">
                  <Upload size={20} />
                  PDF Info Viewer
                  {file && <span className="text-sm text-gray-400">(1 file)</span>}
                </h2>
              </div>

              {/* Unified Upload & Content Area */}
              <div>
                {!file ? (
                  /* Upload Area - Empty State */
                  <label className="border-2 border-dashed border-[#333344] rounded-lg block p-8 text-center cursor-pointer hover:border-[#4ECDC4]/50 transition-colors">
                    <input
                      type="file"
                      accept="application/pdf"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <Upload className="mx-auto mb-3 text-gray-400" size={48} />
                    <p className="text-lg mb-2">Click to upload PDF file</p>
                    <p className="text-sm text-gray-400">
                      or drag and drop a file here
                    </p>
                  </label>
                ) : (
                  <>
                    {/* File Info & Results */}
                    <div className="border-2 border-dashed border-[#4ECDC4]/30 rounded-lg p-4 bg-[#0F0F1E]/50">
                      {/* File Display */}
                      <div className="border-2 border-[#333344] p-3 bg-[#1A1A2E] rounded mb-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <FileText className="text-[#4ECDC4]" size={24} />
                          <div>
                            <p className="font-medium text-sm">{file.name}</p>
                            <p className="text-xs text-gray-400">
                              {(file.size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                        </div>
                        <PixelButton
                          size="sm"
                          variant="secondary"
                          onClick={handleReset}
                        >
                          Change File
                        </PixelButton>
                      </div>

                      {/* Error Display */}
                      {error && (
                        <div className="border-2 border-red-500/30 p-3 bg-red-900/20 rounded text-red-400 mb-4 text-sm">
                          {error}
                        </div>
                      )}

                      {/* PDF Info Results */}
                      {pdfInfo && (
                        <div className="space-y-4 mb-4">
                          {/* Document Properties Section */}
                          <div>
                            <h3 className="font-pixel text-sm text-[#4ECDC4] mb-3 flex items-center gap-2">
                              <FileText size={16} />
                              Document Properties
                            </h3>
                            <div className="space-y-2">
                              <InfoRow
                                label="Number of Pages"
                                value={pdfInfo.num_pages}
                                icon={FileText}
                              />
                              <InfoRow
                                label="Encrypted"
                                value={pdfInfo.is_encrypted ? 'Yes' : 'No'}
                                icon={Lock}
                              />
                              {pdfInfo.page_size && (
                                <InfoRow
                                  label="Page Size"
                                  value={`${pdfInfo.page_size.width.toFixed(1)} × ${pdfInfo.page_size.height.toFixed(1)} ${pdfInfo.page_size.unit}`}
                                  icon={FileType}
                                />
                              )}
                            </div>
                          </div>

                          {/* Metadata Section */}
                          <div>
                            <h3 className="font-pixel text-sm text-[#4ECDC4] mb-3 flex items-center gap-2">
                              <Info size={16} />
                              Metadata
                            </h3>
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
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Get Info Button */}
                    {!pdfInfo && (
                      <div className="mt-4">
                        <PixelButton
                          icon={<Info size={16} />}
                          onClick={handleGetInfo}
                          disabled={loading}
                          loading={loading}
                          className="w-full"
                        >
                          {loading ? 'Getting PDF Info...' : 'Get PDF Information'}
                        </PixelButton>
                      </div>
                    )}
                  </>
                )}
              </div>
            </PixelCard>
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-6">
            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">How to Use</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <p>1. Upload a PDF file</p>
                <p>2. Click "Get PDF Information"</p>
                <p>3. View document properties and metadata</p>
                <div className="pt-2 border-t border-[#333344] mt-3">
                  <p className="text-xs">
                    Tip: Not all PDFs contain metadata - some fields may be empty
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Information Shown</h3>
              </div>
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Document Properties</h4>
                  <p className="text-gray-400 text-xs">
                    Page count, encryption status, and page dimensions
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Metadata</h4>
                  <p className="text-gray-400 text-xs">
                    Title, author, subject, creator, producer, and dates
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Use Cases</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <p>• Check PDF page count before splitting</p>
                <p>• View document author and creation info</p>
                <p>• Verify PDF properties and metadata</p>
                <p>• Check if PDF is encrypted</p>
                <p>• Get page dimensions for printing</p>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Notes</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
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
