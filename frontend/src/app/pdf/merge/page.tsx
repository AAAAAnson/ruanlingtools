'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { FilePlus, Download, Trash2, Upload, Check } from 'lucide-react';

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
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <FilePlus size={32} />
            Merge PDFs
          </h1>
          <p className="text-pixel-text-secondary">
            Combine multiple PDF files into a single document. Files are merged in the order shown.
          </p>
        </div>

        <div className="space-y-6">
          <PixelCard title="Upload PDF Files">
            <div className="space-y-4">
              <label className="pixel-border block p-8 text-center cursor-pointer hover:bg-pixel-bg-secondary transition-colors">
                <input
                  type="file"
                  accept="application/pdf"
                  multiple
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <Upload className="mx-auto mb-3 text-pixel-text-secondary" size={48} />
                <p className="text-lg mb-2">Click to upload PDF files</p>
                <p className="text-sm text-pixel-text-secondary">
                  or drag and drop files here
                </p>
              </label>

              {files.length > 0 && (
                <div className="pixel-border p-4 bg-pixel-bg">
                  <h3 className="font-pixel mb-3">Selected Files ({files.length})</h3>
                  <div className="space-y-2">
                    {files.map((uploadedFile, index) => (
                      <div
                        key={uploadedFile.id}
                        className="pixel-border p-3 bg-white dark:bg-gray-800 flex items-center justify-between"
                      >
                        <div className="flex items-center gap-3 flex-1">
                          <span className="pixel-border px-3 py-1 text-sm font-pixel">
                            {index + 1}
                          </span>
                          <span className="text-sm truncate">
                            {uploadedFile.file.name}
                          </span>
                          <span className="text-xs text-pixel-text-secondary">
                            ({(uploadedFile.file.size / 1024).toFixed(1)} KB)
                          </span>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => moveUp(index)}
                            disabled={index === 0}
                            className="pixel-border px-2 py-1 text-xs hover:bg-pixel-bg-secondary disabled:opacity-50"
                          >
                            ↑
                          </button>
                          <button
                            onClick={() => moveDown(index)}
                            disabled={index === files.length - 1}
                            className="pixel-border px-2 py-1 text-xs hover:bg-pixel-bg-secondary disabled:opacity-50"
                          >
                            ↓
                          </button>
                          <button
                            onClick={() => removeFile(uploadedFile.id)}
                            className="pixel-border px-2 py-1 text-xs hover:bg-red-100 dark:hover:bg-red-900/20"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
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
                  onClick={handleMerge}
                  disabled={files.length < 2 || merging}
                >
                  {merging ? 'Merging...' : 'Merge PDFs'}
                </PixelButton>
                {files.length > 0 && (
                  <PixelButton variant="secondary" onClick={handleReset}>
                    <Trash2 size={16} />
                    Clear All
                  </PixelButton>
                )}
              </div>
            </div>
          </PixelCard>

          {mergedFile && (
            <PixelCard title="Merged PDF Ready">
              <div className="space-y-4">
                <div className="pixel-border p-4 bg-green-50 dark:bg-green-900/20">
                  <div className="flex items-start gap-3">
                    <Check className="text-green-600 dark:text-green-400 flex-shrink-0" size={24} />
                    <div>
                      <p className="font-medium mb-1">
                        Successfully merged {mergedFile.numFilesMerged} PDF files!
                      </p>
                      <p className="text-sm text-pixel-text-secondary">
                        Filename: {mergedFile.filename}
                      </p>
                    </div>
                  </div>
                </div>

                <PixelButton onClick={handleDownload}>
                  <Download size={16} />
                  Download Merged PDF
                </PixelButton>
              </div>
            </PixelCard>
          )}

          <PixelCard title="How to Use">
            <div className="space-y-2 text-sm text-pixel-text-secondary">
              <p>1. Click the upload area or drag PDF files to add them</p>
              <p>2. Use ↑ ↓ buttons to reorder files (they will be merged in this order)</p>
              <p>3. Remove unwanted files using the trash icon</p>
              <p>4. Click "Merge PDFs" when you have at least 2 files</p>
              <p>5. Download the merged PDF file</p>
            </div>
          </PixelCard>
        </div>
      </div>
    </MainLayout>
  );
}
