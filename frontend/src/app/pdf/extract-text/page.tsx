'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { FileText, Upload, Copy, Check, Download } from 'lucide-react';

export default function PDFExtractTextPage() {
  const [file, setFile] = useState<File | null>(null);
  const [extractedText, setExtractedText] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [textLength, setTextLength] = useState(0);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError('');
        setExtractedText('');
        setTextLength(0);
      } else {
        setError('Please select a PDF file');
      }
    }
  };

  const handleExtract = async () => {
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    setExtracting(true);
    setError('');
    setExtractedText('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/pdf/extract-text', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setExtractedText(result.data.text);
        setTextLength(result.data.length);
      } else {
        setError(result.message || 'Text extraction failed');
      }
    } catch (err) {
      setError('Network error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setExtracting(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(extractedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadText = () => {
    const blob = new Blob([extractedText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${file?.name.replace('.pdf', '')}_extracted.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleReset = () => {
    setFile(null);
    setExtractedText('');
    setError('');
    setTextLength(0);
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <FileText size={32} />
            Extract Text from PDF
          </h1>
          <p className="text-pixel-text-secondary">
            Extract all text content from PDF files. Great for copying text from scanned documents or PDFs.
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
                    onClick={handleExtract}
                    disabled={!file || extracting}
                  >
                    {extracting ? 'Extracting...' : 'Extract Text'}
                  </PixelButton>
                  {file && (
                    <PixelButton variant="secondary" onClick={handleReset}>
                      Reset
                    </PixelButton>
                  )}
                </div>
              </div>
            </PixelCard>

            {extractedText && (
              <PixelCard title="Extracted Text">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-pixel-text-secondary">
                      {textLength.toLocaleString()} characters extracted
                    </p>
                    <div className="flex gap-2">
                      <PixelButton size="sm" onClick={handleCopy}>
                        {copied ? (
                          <>
                            <Check size={14} />
                            Copied
                          </>
                        ) : (
                          <>
                            <Copy size={14} />
                            Copy
                          </>
                        )}
                      </PixelButton>
                      <PixelButton size="sm" onClick={handleDownloadText}>
                        <Download size={14} />
                        Download
                      </PixelButton>
                    </div>
                  </div>

                  <PixelTextarea
                    value={extractedText}
                    onChange={(e) => setExtractedText(e.target.value)}
                    rows={20}
                    className="w-full font-mono text-sm"
                    placeholder="Extracted text will appear here..."
                  />
                </div>
              </PixelCard>
            )}
          </div>

          <div className="space-y-6">
            <PixelCard title="How to Use">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>1. Upload a PDF file</p>
                <p>2. Click "Extract Text" to process</p>
                <p>3. View, copy, or download the extracted text</p>
                <p>4. Edit the text directly if needed</p>
              </div>
            </PixelCard>

            <PixelCard title="Features">
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Page-by-Page</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Text is extracted from all pages with page markers
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Editable Output</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    You can edit the extracted text before copying or downloading
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Multiple Formats</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Copy to clipboard or download as a .txt file
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Notes">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>• Works best with text-based PDFs</p>
                <p>• Scanned PDFs may not contain extractable text</p>
                <p>• Formatting may not be preserved</p>
                <p>• Tables and complex layouts may appear differently</p>
              </div>
            </PixelCard>

            <PixelCard title="Use Cases">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>• Copy text from PDF documents</p>
                <p>• Convert PDFs to plain text</p>
                <p>• Extract content for further processing</p>
                <p>• Get text for translation or analysis</p>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
