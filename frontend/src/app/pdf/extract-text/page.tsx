'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { FileText, Upload, Copy, Check, Download, X } from 'lucide-react';

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
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient flex items-center gap-3">
            <FileText size={32} />
            Extract Text from PDF
          </h1>
          <p className="text-gray-300">
            Extract all text content from PDF files for copying, editing, or further processing
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
                  Text Extractor
                  {file && <span className="text-sm text-gray-400">(1 file)</span>}
                </h2>
                {extractedText && (
                  <div className="flex gap-2">
                    <PixelButton
                      size="sm"
                      icon={copied ? <Check size={14} /> : <Copy size={14} />}
                      onClick={handleCopy}
                    >
                      {copied ? 'Copied' : 'Copy Text'}
                    </PixelButton>
                    <PixelButton
                      size="sm"
                      icon={<Download size={14} />}
                      onClick={handleDownloadText}
                    >
                      Download TXT
                    </PixelButton>
                  </div>
                )}
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

                      {/* Extracted Text Results */}
                      {extractedText && (
                        <div className="mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <p className="text-xs text-gray-400">
                              Extracted {textLength.toLocaleString()} characters
                            </p>
                            <p className="text-xs text-[#4ECDC4]">
                              Text is editable
                            </p>
                          </div>
                          <PixelTextarea
                            value={extractedText}
                            onChange={(e) => setExtractedText(e.target.value)}
                            rows={20}
                            className="w-full font-mono text-sm"
                            placeholder="Extracted text will appear here..."
                          />
                        </div>
                      )}
                    </div>

                    {/* Extract Button */}
                    {!extractedText && (
                      <div className="mt-4">
                        <PixelButton
                          icon={<FileText size={16} />}
                          onClick={handleExtract}
                          disabled={extracting}
                          loading={extracting}
                          className="w-full"
                        >
                          {extracting ? 'Extracting Text...' : 'Extract Text from PDF'}
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
                <p>2. Click "Extract Text" to process</p>
                <p>3. View and edit the extracted text</p>
                <p>4. Copy to clipboard or download as TXT</p>
                <div className="pt-2 border-t border-[#333344] mt-3">
                  <p className="text-xs">
                    Tip: The extracted text is editable before copying or downloading
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Features</h3>
              </div>
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Page-by-Page</h4>
                  <p className="text-gray-400 text-xs">
                    Text is extracted from all pages with page markers
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Editable Output</h4>
                  <p className="text-gray-400 text-xs">
                    Edit the extracted text before copying or downloading
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Multiple Formats</h4>
                  <p className="text-gray-400 text-xs">
                    Copy to clipboard or download as a .txt file
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Use Cases</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <p>• Copy text from PDF documents</p>
                <p>• Convert PDFs to plain text</p>
                <p>• Extract content for further processing</p>
                <p>• Get text for translation or analysis</p>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-3">
                <h3 className="font-pixel text-sm text-primary">Notes</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <p>• Works best with text-based PDFs</p>
                <p>• Scanned PDFs may not contain extractable text</p>
                <p>• Formatting may not be preserved</p>
                <p>• Tables and complex layouts may appear differently</p>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
