'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelSelect } from '@/components/ui/PixelSelect';
import { PixelInput } from '@/components/ui/PixelInput';
import { PixelCheckbox } from '@/components/ui/PixelCheckbox';
import { FileImage, Download, Upload, FileText, Image as ImageIcon, Eye, X } from 'lucide-react';

interface ConvertedImage {
  page_number: number;
  filename: string;
  download_url: string;
  size: number;
}

interface ConversionResponse {
  total_pages: number;
  images: ConvertedImage[];
}

export default function PDFToImagesPage() {
  const [file, setFile] = useState<File | null>(null);
  const [outputFormat, setOutputFormat] = useState('png');
  const [dpi, setDpi] = useState('150');
  const [convertAllPages, setConvertAllPages] = useState(true);
  const [pageRange, setPageRange] = useState('');
  const [converting, setConverting] = useState(false);
  const [images, setImages] = useState<ConvertedImage[]>([]);
  const [error, setError] = useState('');
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError('');
        setImages([]);
      } else {
        setError('Please select a PDF file');
      }
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const handleConvert = async () => {
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    if (!convertAllPages && !pageRange.trim()) {
      setError('Please enter page range');
      return;
    }

    setConverting(true);
    setError('');
    setImages([]);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('output_format', outputFormat);
      formData.append('dpi', dpi);

      if (!convertAllPages && pageRange.trim()) {
        formData.append('pages', pageRange);
      }

      const response = await fetch(`${API_BASE}/pdf/to-images`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.code === 200 && result.data) {
        const data = result.data as ConversionResponse;
        setImages(data.images || []);
      } else {
        setError(result.message || 'Conversion failed');
      }
    } catch (err) {
      setError('Network error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setConverting(false);
    }
  };

  const handleDownload = (downloadUrl: string, filename: string) => {
    const fullUrl = `${API_BASE}${downloadUrl}`;
    window.open(fullUrl, '_blank');
  };

  const handleDownloadAll = async () => {
    if (images.length === 0) return;

    try {
      const filenames = images.map(img => img.filename);

      const response = await fetch(`${API_BASE}/pdf/download-images-zip`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filenames }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pdf_images_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setError('Download all failed');
      }
    } catch (err) {
      setError('Download all failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handlePreview = (downloadUrl: string) => {
    const fullUrl = `${API_BASE}${downloadUrl}`;
    setPreviewImage(fullUrl);
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient flex items-center gap-3">
            <FileImage size={32} />
            PDF to Images
          </h1>
          <p className="text-gray-300">
            Convert PDF pages to high-quality image files (PNG or JPG)
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Upload Section */}
            <PixelCard hoverable={false}>
              <div className="mb-4">
                <h2 className="font-pixel text-lg text-primary flex items-center gap-2">
                  <Upload size={20} />
                  Upload PDF
                </h2>
              </div>

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

              {file && (
                <div className="mt-4 border-2 border-[#333344] p-4 bg-[#0F0F1E] rounded flex items-center gap-3">
                  <FileText className="text-[#4ECDC4]" size={24} />
                  <div className="flex-1">
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-gray-400">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
              )}
            </PixelCard>

            {/* Page Selection */}
            {file && (
              <PixelCard hoverable={false}>
                <div className="mb-4">
                  <h2 className="font-pixel text-lg text-primary">Page Selection</h2>
                </div>

                <div className="space-y-4">
                  <PixelCheckbox
                    checked={convertAllPages}
                    onChange={(e) => setConvertAllPages(e.target.checked)}
                    label="Convert all pages"
                  />

                  {!convertAllPages && (
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Page Range
                      </label>
                      <PixelInput
                        value={pageRange}
                        onChange={(e) => setPageRange(e.target.value)}
                        placeholder="e.g., 1-3,5,7-10"
                        className="w-full"
                      />
                      <p className="text-xs text-gray-400 mt-2">
                        Enter page numbers or ranges separated by commas
                      </p>
                    </div>
                  )}
                </div>
              </PixelCard>
            )}

            {/* Error Display */}
            {error && (
              <div className="border-2 border-red-500/30 p-4 bg-red-900/20 rounded text-red-400">
                {error}
              </div>
            )}

            {/* Convert Button */}
            {file && (
              <PixelButton
                icon={<ImageIcon size={16} />}
                onClick={handleConvert}
                disabled={converting}
                loading={converting}
                className="w-full"
              >
                {converting ? 'Converting...' : 'Convert to Images'}
              </PixelButton>
            )}

            {/* Results */}
            {images.length > 0 && (
              <PixelCard hoverable={false}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="font-pixel text-lg text-primary">
                    Converted Images ({images.length})
                  </h2>
                  <PixelButton
                    size="sm"
                    icon={<Download size={14} />}
                    onClick={handleDownloadAll}
                  >
                    Download All
                  </PixelButton>
                </div>

                <div className="space-y-2">
                  {images.map((image) => (
                    <div
                      key={image.page_number}
                      className="border-2 border-[#333344] p-3 bg-[#0F0F1E] rounded hover:border-[#4ECDC4]/50 transition-colors"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3 flex-1">
                          <ImageIcon size={20} className="text-[#4ECDC4]" />
                          <div>
                            <p className="font-medium text-sm">
                              Page {image.page_number}
                            </p>
                            <p className="text-xs text-gray-400">
                              {image.filename} • {formatFileSize(image.size)}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-1">
                          <PixelButton
                            size="sm"
                            variant="secondary"
                            icon={<Eye size={12} />}
                            onClick={() => handlePreview(image.download_url)}
                            title="Preview"
                          />
                          <PixelButton
                            size="sm"
                            icon={<Download size={12} />}
                            onClick={() => handleDownload(image.download_url, image.filename)}
                            title="Download"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </PixelCard>
            )}
          </div>

          {/* Settings Sidebar */}
          <div className="space-y-6">
            <PixelCard hoverable={false}>
              <div className="mb-4">
                <h2 className="font-pixel text-sm text-primary">Settings</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Output Format
                  </label>
                  <PixelSelect
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                    options={[
                      { value: 'png', label: 'PNG' },
                      { value: 'jpg', label: 'JPG' }
                    ]}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    DPI (Quality)
                  </label>
                  <PixelSelect
                    value={dpi}
                    onChange={(e) => setDpi(e.target.value)}
                    options={[
                      { value: '72', label: '72 DPI (Web)' },
                      { value: '150', label: '150 DPI (Standard)' },
                      { value: '300', label: '300 DPI (High Quality)' },
                      { value: '600', label: '600 DPI (Print)' }
                    ]}
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Higher DPI = better quality but larger files
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="font-medium text-gray-300 mb-1">Supported Formats:</p>
                  <p className="text-gray-400 text-xs">
                    PNG (lossless), JPG (compressed)
                  </p>
                </div>
                <div className="pt-2 border-t border-[#333344]">
                  <p className="text-xs text-gray-400">
                    Max PDF size: 50 MB
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard hoverable={false}>
              <div className="mb-2">
                <h3 className="font-medium text-sm">How to Use</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <p>1. Upload your PDF file</p>
                <p>2. Select output format and quality</p>
                <p>3. Choose pages to convert</p>
                <p>4. Click "Convert to Images"</p>
                <p>5. Download individual images or all as ZIP</p>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {previewImage && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setPreviewImage(null)}>
          <div className="max-w-4xl w-full bg-[#1A1A2E] border-2 border-[#4ECDC4] rounded p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-pixel text-lg text-[#4ECDC4]">Image Preview</h3>
              <button onClick={() => setPreviewImage(null)} className="text-gray-400 hover:text-white">
                <X size={24} />
              </button>
            </div>
            <div className="border-2 border-[#333344] rounded overflow-hidden bg-[#0F0F1E]">
              <img src={previewImage} alt="Preview" className="w-full h-auto" />
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
