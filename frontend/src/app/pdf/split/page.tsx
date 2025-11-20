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
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient flex items-center gap-3">
            <Split size={32} />
            Split PDF
          </h1>
          <p className="text-gray-300">
            Split a PDF file into multiple documents based on page ranges
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            {/* Single Unified Card */}
            <PixelCard hoverable={false}>
              {/* Header */}
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-pixel text-lg text-primary flex items-center gap-2">
                  <Upload size={20} />
                  PDF Splitter
                  {file && <span className="text-sm text-gray-400">(1 file)</span>}
                </h2>
                {splitFiles.length > 0 && (
                  <PixelButton
                    size="sm"
                    icon={<Download size={14} />}
                    onClick={handleDownloadAll}
                  >
                    Download All ({splitFiles.length})
                  </PixelButton>
                )}
              </div>

              {/* Unified Upload & Content Area */}
              <div>
                {!file ? (
                  /* Upload Area */
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
                    {/* File Info & Settings */}
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
                          onClick={() => {
                            setFile(null);
                            setSplitFiles([]);
                            setError('');
                          }}
                        >
                          Change File
                        </PixelButton>
                      </div>

                      {/* Page Ranges Input */}
                      <div className="mb-4">
                        <label className="block text-sm font-medium mb-2">
                          Page Ranges
                        </label>
                        <PixelInput
                          value={pageRanges}
                          onChange={(e) => setPageRanges(e.target.value)}
                          placeholder="e.g., 1-3,5,7-10"
                          className="w-full"
                        />
                        <p className="text-xs text-gray-400 mt-2">
                          Enter page ranges separated by commas. Use hyphens for ranges.
                        </p>
                        <div className="mt-2">
                          <PixelButton size="sm" variant="secondary" onClick={loadExample}>
                            Load Example
                          </PixelButton>
                        </div>
                      </div>

                      {/* Error Display */}
                      {error && (
                        <div className="border-2 border-red-500/30 p-3 bg-red-900/20 rounded text-red-400 mb-4 text-sm">
                          {error}
                        </div>
                      )}

                      {/* Split Results */}
                      {splitFiles.length > 0 && (
                        <div className="mb-4">
                          <p className="text-xs text-gray-400 mb-2">
                            Successfully split into {splitFiles.length} file(s)
                          </p>
                          <div className="space-y-2">
                            {splitFiles.map((splitFile, index) => (
                              <div
                                key={index}
                                className="border-2 border-[#333344] p-3 bg-[#1A1A2E] rounded hover:border-[#4ECDC4]/50 transition-colors"
                              >
                                <div className="flex items-center justify-between gap-3">
                                  <div className="flex items-center gap-3 flex-1">
                                    <FileText size={20} className="text-[#4ECDC4]" />
                                    <div>
                                      <p className="font-medium text-sm">Pages {splitFile.range}</p>
                                      <p className="text-xs text-gray-400">
                                        {splitFile.filename}
                                      </p>
                                    </div>
                                  </div>
                                  <PixelButton
                                    size="sm"
                                    icon={<Download size={12} />}
                                    onClick={() => handleDownload(splitFile.downloadUrl, splitFile.filename)}
                                    title="Download"
                                  />
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Split Button */}
                    <div className="mt-4">
                      <PixelButton
                        icon={<Split size={16} />}
                        onClick={handleSplit}
                        disabled={!pageRanges.trim() || splitting}
                        loading={splitting}
                        className="w-full"
                      >
                        {splitting ? 'Splitting...' : 'Split PDF'}
                      </PixelButton>
                    </div>
                  </>
                )}
              </div>
            </PixelCard>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Page Range Format</h3>
              </div>
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Single Page</h4>
                  <code className="border-2 border-[#333344] px-2 py-1 text-xs bg-[#0F0F1E] rounded">5</code>
                  <p className="text-gray-400 text-xs mt-1">
                    Extract only page 5
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Page Range</h4>
                  <code className="border-2 border-[#333344] px-2 py-1 text-xs bg-[#0F0F1E] rounded">1-3</code>
                  <p className="text-gray-400 text-xs mt-1">
                    Extract pages 1, 2, and 3
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Multiple Ranges</h4>
                  <code className="border-2 border-[#333344] px-2 py-1 text-xs bg-[#0F0F1E] rounded">1-3,5,7-10</code>
                  <p className="text-gray-400 text-xs mt-1">
                    Extract pages 1-3, 5, and 7-10 as separate files
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">How to Use</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <p>1. Upload a PDF file</p>
                <p>2. Enter page ranges to split</p>
                <p>3. Click "Split PDF" to process</p>
                <p>4. Download individual files or all at once</p>
                <div className="pt-2 border-t border-[#333344] mt-3">
                  <p className="text-xs">
                    Tip: Each range or page becomes a separate PDF file
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Examples</h3>
              </div>
              <div className="space-y-2 text-xs">
                <div className="border-2 border-[#333344] p-2 bg-[#0F0F1E] rounded">
                  <code>1-5</code>
                  <p className="text-gray-400 mt-1">First 5 pages</p>
                </div>
                <div className="border-2 border-[#333344] p-2 bg-[#0F0F1E] rounded">
                  <code>1,3,5,7,9</code>
                  <p className="text-gray-400 mt-1">Odd pages 1-9</p>
                </div>
                <div className="border-2 border-[#333344] p-2 bg-[#0F0F1E] rounded">
                  <code>1-10,15-20</code>
                  <p className="text-gray-400 mt-1">Two ranges</p>
                </div>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
