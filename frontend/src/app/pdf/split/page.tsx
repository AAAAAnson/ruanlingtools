'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelInput } from '@/components/ui/PixelInput';
import { Split, Download, Upload, FileText } from 'lucide-react';

interface SplitFile {
  range: string;
  filename: string;
  downloadUrl: string;
}

export default function PDFSplitPage() {
  const [file, setFile] = useState<File | null>(null);
  const [pageRanges, setPageRanges] = useState('');
  const [splitting, setSplitting] = useState(false);
  const [splitFiles, setSplitFiles] = useState<SplitFile[]>([]);
  const [error, setError] = useState('');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError('');
        setSplitFiles([]);
      } else {
        setError('Please select a PDF file');
      }
    }
  };

  const handleSplit = async () => {
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    if (!pageRanges.trim()) {
      setError('Please enter page ranges');
      return;
    }

    setSplitting(true);
    setError('');
    setSplitFiles([]);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('pages', pageRanges);

      const response = await fetch('/api/pdf/split', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setSplitFiles(result.data.split_files);
      } else {
        setError(result.message || 'Split failed');
      }
    } catch (err) {
      setError('Network error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setSplitting(false);
    }
  };

  const handleDownload = async (downloadUrl: string, filename: string) => {
    try {
      const response = await fetch(downloadUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Download failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleDownloadAll = async () => {
    for (const splitFile of splitFiles) {
      await handleDownload(splitFile.downloadUrl, splitFile.filename);
      // Small delay between downloads
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  };

  const loadExample = () => {
    setPageRanges('1-3,5,7-10');
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <Split size={32} />
            Split PDF
          </h1>
          <p className="text-pixel-text-secondary">
            Split a PDF file into multiple documents based on page ranges.
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
              </div>
            </PixelCard>

            <PixelCard title="Page Ranges">
              <div className="space-y-4">
                <div>
                  <PixelInput
                    value={pageRanges}
                    onChange={(e) => setPageRanges(e.target.value)}
                    placeholder="e.g., 1-3,5,7-10"
                    className="w-full"
                  />
                  <p className="text-xs text-pixel-text-secondary mt-2">
                    Enter page ranges separated by commas. Use hyphens for ranges.
                  </p>
                </div>

                {error && (
                  <div className="pixel-border p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400">
                    {error}
                  </div>
                )}

                <div className="flex gap-3">
                  <PixelButton
                    onClick={handleSplit}
                    disabled={!file || !pageRanges.trim() || splitting}
                  >
                    {splitting ? 'Splitting...' : 'Split PDF'}
                  </PixelButton>
                  <PixelButton variant="secondary" onClick={loadExample}>
                    Load Example
                  </PixelButton>
                </div>
              </div>
            </PixelCard>

            {splitFiles.length > 0 && (
              <PixelCard title="Split Files">
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm text-pixel-text-secondary">
                      Successfully split into {splitFiles.length} file(s)
                    </p>
                    <PixelButton size="sm" onClick={handleDownloadAll}>
                      Download All
                    </PixelButton>
                  </div>

                  <div className="space-y-2">
                    {splitFiles.map((splitFile, index) => (
                      <div
                        key={index}
                        className="pixel-border p-3 bg-white dark:bg-gray-800 flex items-center justify-between"
                      >
                        <div>
                          <p className="font-medium text-sm">{splitFile.range}</p>
                          <p className="text-xs text-pixel-text-secondary">
                            {splitFile.filename}
                          </p>
                        </div>
                        <PixelButton
                          size="sm"
                          onClick={() => handleDownload(splitFile.downloadUrl, splitFile.filename)}
                        >
                          <Download size={14} />
                          Download
                        </PixelButton>
                      </div>
                    ))}
                  </div>
                </div>
              </PixelCard>
            )}
          </div>

          <div className="space-y-6">
            <PixelCard title="Page Range Format">
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Single Page</h4>
                  <code className="pixel-border px-2 py-1 text-xs bg-pixel-bg">5</code>
                  <p className="text-pixel-text-secondary text-xs mt-1">
                    Extract only page 5
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Page Range</h4>
                  <code className="pixel-border px-2 py-1 text-xs bg-pixel-bg">1-3</code>
                  <p className="text-pixel-text-secondary text-xs mt-1">
                    Extract pages 1, 2, and 3
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Multiple Ranges</h4>
                  <code className="pixel-border px-2 py-1 text-xs bg-pixel-bg">1-3,5,7-10</code>
                  <p className="text-pixel-text-secondary text-xs mt-1">
                    Extract pages 1-3, 5, and 7-10 as separate files
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="How to Use">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>1. Upload a PDF file</p>
                <p>2. Enter page ranges to split</p>
                <p>3. Click "Split PDF" to process</p>
                <p>4. Download individual files or all at once</p>
                <div className="pt-2 border-t border-pixel-border mt-3">
                  <p className="text-xs">
                    Tip: Each range or page becomes a separate PDF file
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Examples">
              <div className="space-y-2 text-xs">
                <div className="pixel-border p-2 bg-pixel-bg">
                  <code>1-5</code>
                  <p className="text-pixel-text-secondary mt-1">First 5 pages</p>
                </div>
                <div className="pixel-border p-2 bg-pixel-bg">
                  <code>1,3,5,7,9</code>
                  <p className="text-pixel-text-secondary mt-1">Odd pages 1-9</p>
                </div>
                <div className="pixel-border p-2 bg-pixel-bg">
                  <code>1-10,15-20</code>
                  <p className="text-pixel-text-secondary mt-1">Two ranges</p>
                </div>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
