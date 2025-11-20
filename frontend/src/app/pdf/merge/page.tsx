'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { FilePlus, Download, Trash2, Upload, Check, FileText, ChevronUp, ChevronDown, X } from 'lucide-react';

interface UploadedFile {
  file: File;
  id: string;
}

export default function PDFMergePage() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [merging, setMerging] = useState(false);
  const [mergedFile, setMergedFile] = useState<{
    filename: string;
    downloadUrl: string;
    numFilesMerged: number;
  } | null>(null);
  const [error, setError] = useState('');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files)
        .filter(file => file.type === 'application/pdf')
        .map(file => ({
          file,
          id: Math.random().toString(36).substr(2, 9)
        }));

      if (newFiles.length < e.target.files.length) {
        setError('Some files were skipped (only PDF files are supported)');
        setTimeout(() => setError(''), 3000);
      }

      setFiles([...files, ...newFiles]);
    }
  };

  const removeFile = (id: string) => {
    setFiles(files.filter(f => f.id !== id));
  };

  const moveUp = (index: number) => {
    if (index === 0) return;
    const newFiles = [...files];
    [newFiles[index - 1], newFiles[index]] = [newFiles[index], newFiles[index - 1]];
    setFiles(newFiles);
  };

  const moveDown = (index: number) => {
    if (index === files.length - 1) return;
    const newFiles = [...files];
    [newFiles[index], newFiles[index + 1]] = [newFiles[index + 1], newFiles[index]];
    setFiles(newFiles);
  };

  const handleMerge = async () => {
    if (files.length < 2) {
      setError('Please select at least 2 PDF files to merge');
      return;
    }

    setMerging(true);
    setError('');
    setMergedFile(null);

    try {
      const formData = new FormData();
      files.forEach(({ file }) => {
        formData.append('files', file);
      });

      const response = await fetch('/api/pdf/merge', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setMergedFile({
          filename: result.data.filename,
          downloadUrl: result.data.download_url,
          numFilesMerged: result.data.num_files_merged
        });
      } else {
        setError(result.message || 'Merge failed');
      }
    } catch (err) {
      setError('Network error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setMerging(false);
    }
  };

  const handleDownload = async () => {
    if (!mergedFile) return;

    try {
      const response = await fetch(mergedFile.downloadUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = mergedFile.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Download failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleReset = () => {
    setFiles([]);
    setMergedFile(null);
    setError('');
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient flex items-center gap-3">
            <FilePlus size={32} />
            Merge PDFs
          </h1>
          <p className="text-gray-300">
            Combine multiple PDF files into a single document
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
                  PDF Merger
                  {files.length > 0 && <span className="text-sm text-gray-400">({files.length} files)</span>}
                </h2>
                {files.length > 0 && (
                  <PixelButton
                    size="sm"
                    variant="secondary"
                    icon={<Trash2 size={14} />}
                    onClick={handleReset}
                  >
                    Clear All
                  </PixelButton>
                )}
              </div>

              {/* Unified Upload & File List Area */}
              <div>
                {files.length === 0 ? (
                  /* Upload Area - Empty State */
                  <label className="border-2 border-dashed border-[#333344] rounded-lg block p-8 text-center cursor-pointer hover:border-[#4ECDC4]/50 transition-colors">
                    <input
                      type="file"
                      accept="application/pdf"
                      multiple
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <Upload className="mx-auto mb-3 text-gray-400" size={48} />
                    <p className="text-lg mb-2">Click to upload PDF files</p>
                    <p className="text-sm text-gray-400">
                      or drag and drop files here (multiple files)
                    </p>
                  </label>
                ) : (
                  <>
                    {/* File List with integrated upload */}
                    <div className="border-2 border-dashed border-[#4ECDC4]/30 rounded-lg p-4 bg-[#0F0F1E]/50">
                      {/* File Items */}
                      <div className="space-y-2 mb-4">
                        {files.map((uploadedFile, index) => (
                          <div
                            key={uploadedFile.id}
                            className="border-2 border-[#333344] p-3 bg-[#1A1A2E] rounded hover:border-[#4ECDC4]/50 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              {/* Order Number */}
                              <div className="flex-shrink-0 w-8 h-8 border-2 border-[#4ECDC4] rounded flex items-center justify-center font-pixel text-sm text-[#4ECDC4]">
                                {index + 1}
                              </div>

                              {/* File Icon & Info */}
                              <FileText className="text-[#4ECDC4] flex-shrink-0" size={20} />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium truncate" title={uploadedFile.file.name}>
                                  {uploadedFile.file.name}
                                </p>
                                <p className="text-xs text-gray-400">
                                  {(uploadedFile.file.size / 1024).toFixed(1)} KB
                                </p>
                              </div>

                              {/* Reorder Buttons */}
                              <div className="flex gap-1 flex-shrink-0">
                                <PixelButton
                                  size="sm"
                                  variant="secondary"
                                  icon={<ChevronUp size={12} />}
                                  onClick={() => moveUp(index)}
                                  disabled={index === 0}
                                  title="Move up"
                                />
                                <PixelButton
                                  size="sm"
                                  variant="secondary"
                                  icon={<ChevronDown size={12} />}
                                  onClick={() => moveDown(index)}
                                  disabled={index === files.length - 1}
                                  title="Move down"
                                />
                                <PixelButton
                                  size="sm"
                                  variant="danger"
                                  icon={<X size={12} />}
                                  onClick={() => removeFile(uploadedFile.id)}
                                  title="Remove"
                                />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Compact Upload Area - Add more files */}
                      <div className="border-2 border-dashed border-[#333344] rounded p-3 text-center hover:border-[#4ECDC4]/50 transition-colors cursor-pointer">
                        <label className="cursor-pointer block">
                          <input
                            type="file"
                            accept="application/pdf"
                            multiple
                            onChange={handleFileSelect}
                            className="hidden"
                          />
                          <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
                            <Upload size={16} />
                            <span>Click to add more PDF files</span>
                          </div>
                        </label>
                      </div>
                    </div>

                    {/* Error Display */}
                    {error && (
                      <div className="mt-4 border-2 border-red-500/30 p-3 bg-red-900/20 rounded text-red-400 text-sm">
                        {error}
                      </div>
                    )}

                    {/* Success Message */}
                    {mergedFile && (
                      <div className="mt-4 border-2 border-green-500/30 p-4 bg-green-900/20 rounded">
                        <div className="flex items-start gap-3 mb-3">
                          <Check className="text-green-400 flex-shrink-0" size={24} />
                          <div>
                            <p className="font-medium text-green-400 mb-1">
                              Successfully merged {mergedFile.numFilesMerged} PDF files!
                            </p>
                            <p className="text-sm text-gray-400">
                              Filename: {mergedFile.filename}
                            </p>
                          </div>
                        </div>
                        <PixelButton
                          icon={<Download size={16} />}
                          onClick={handleDownload}
                        >
                          Download Merged PDF
                        </PixelButton>
                      </div>
                    )}

                    {/* Merge Button */}
                    {!mergedFile && (
                      <div className="mt-4">
                        <PixelButton
                          icon={<FilePlus size={16} />}
                          onClick={handleMerge}
                          disabled={files.length < 2 || merging}
                          loading={merging}
                          className="w-full"
                        >
                          {merging ? 'Merging...' : `Merge ${files.length} PDFs`}
                        </PixelButton>
                        {files.length < 2 && (
                          <p className="text-xs text-gray-400 mt-2 text-center">
                            Add at least 2 PDF files to merge
                          </p>
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            </PixelCard>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">How to Use</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <p>1. Upload multiple PDF files</p>
                <p>2. Use ↑ ↓ buttons to reorder files</p>
                <p>3. Files will be merged in the displayed order</p>
                <p>4. Click "Merge PDFs" to combine</p>
                <p>5. Download the merged PDF file</p>
                <div className="pt-2 border-t border-[#333344] mt-3">
                  <p className="text-xs">
                    Tip: Order matters! PDFs will be combined in the sequence shown.
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Features</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <p>• Upload multiple PDF files at once</p>
                <p>• Drag and drop support</p>
                <p>• Reorder files easily</p>
                <p>• Preview file list before merging</p>
                <p>• Preserves original formatting</p>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="font-medium text-gray-300 mb-1">File Requirements:</p>
                  <p className="text-gray-400 text-xs">
                    PDF files only, minimum 2 files
                  </p>
                </div>
                <div className="pt-2 border-t border-[#333344]">
                  <p className="text-xs text-gray-400">
                    Max file size: 50 MB per PDF
                  </p>
                </div>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
