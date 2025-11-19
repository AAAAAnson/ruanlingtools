'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelUpload } from '@/components/ui/PixelUpload';
import { PixelSelect } from '@/components/ui/PixelSelect';
import { PixelSlider } from '@/components/ui/PixelSlider';
import { PixelInput } from '@/components/ui/PixelInput';
import { PixelProgress } from '@/components/ui/PixelProgress';
import { PixelCheckbox } from '@/components/ui/PixelCheckbox';
import { Download, Image as ImageIcon, FileImage, CheckCircle, XCircle, Trash2, Eye, X } from 'lucide-react';

interface ConversionResult {
  original_filename: string;
  converted_filename: string;
  output_format: string;
  size: number;
  size_mb: number;
  download_url: string;
}

interface ConversionResponse {
  total: number;
  successful: number;
  failed: number;
  results: ConversionResult[];
  errors?: Array<{ filename: string; error: string }>;
}

interface FilePreview {
  file: File;
  preview: string;
}

export default function ImageConvertPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [filePreviews, setFilePreviews] = useState<FilePreview[]>([]);
  const [outputFormat, setOutputFormat] = useState('png');
  const [quality, setQuality] = useState(85);
  const [enableResize, setEnableResize] = useState(false);
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [isConverting, setIsConverting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ConversionResult[]>([]);
  const [errors, setErrors] = useState<Array<{ filename: string; error: string }>>([]);
  const [compareView, setCompareView] = useState<{ original: string; converted: string; filename: string } | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const handleFilesSelected = (selectedFiles: File[]) => {
    setFiles(selectedFiles);
    setResults([]);
    setErrors([]);

    // 创建预览
    const previews: FilePreview[] = [];
    selectedFiles.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        previews.push({
          file,
          preview: reader.result as string
        });
        if (previews.length === selectedFiles.length) {
          setFilePreviews(previews);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const handleConvert = async () => {
    if (files.length === 0) {
      return;
    }

    setIsConverting(true);
    setProgress(0);
    setResults([]);
    setErrors([]);

    // 模拟进度更新
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 200);

    try {
      const formData = new FormData();

      files.forEach(file => {
        formData.append('files', file);
      });

      formData.append('output_format', outputFormat);
      formData.append('quality', quality.toString());

      if (enableResize && width) {
        formData.append('width', width);
      }
      if (enableResize && height) {
        formData.append('height', height);
      }

      const response = await fetch(`${API_BASE}/image/convert`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      const data = await response.json();

      if (data.code === 200 && data.data) {
        const conversionData = data.data as ConversionResponse;
        setResults(conversionData.results || []);
        setErrors(conversionData.errors || []);
        setProgress(100);
      } else {
        setErrors([{ filename: 'All files', error: data.message || 'Conversion failed' }]);
        setProgress(0);
      }
    } catch (error) {
      clearInterval(progressInterval);
      setErrors([{ filename: 'System', error: error instanceof Error ? error.message : 'Unknown error' }]);
      setProgress(0);
    } finally {
      setIsConverting(false);
    }
  };

  const handleDownload = (filename: string) => {
    const downloadUrl = `${API_BASE}/image/download/${filename}`;
    window.open(downloadUrl, '_blank');
  };

  const handleDownloadAll = async () => {
    if (results.length === 0) return;

    try {
      const filenames = results.map(r => r.converted_filename);

      const response = await fetch(`${API_BASE}/image/download-zip`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filenames),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `converted_images_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Download all failed:', error);
    }
  };

  const handleClear = () => {
    setFiles([]);
    setFilePreviews([]);
    setResults([]);
    setErrors([]);
    setProgress(0);
  };

  const handlePreview = async (result: ConversionResult) => {
    const originalPreview = filePreviews.find(p => p.file.name === result.original_filename);
    if (!originalPreview) return;

    const convertedUrl = `${API_BASE}/image/download/${result.converted_filename}`;

    setCompareView({
      original: originalPreview.preview,
      converted: convertedUrl,
      filename: result.original_filename
    });
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient">Image Format Converter</h1>
          <p className="text-gray-300">
            Convert images between JPG, PNG, and WebP formats with batch processing support
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content - 3 columns */}
          <div className="lg:col-span-3 space-y-6">
            {/* Upload Section */}
            <PixelCard title="Upload Images" icon={<FileImage size={20} />} hoverable={false}>
              <PixelUpload
                multiple={true}
                accept="image/*"
                maxSizeMB={10}
                onFilesSelected={handleFilesSelected}
              />

              {/* File Previews */}
              {filePreviews.length > 0 && (
                <div className="mt-6">
                  <p className="text-sm text-gray-400 mb-3">
                    Selected: {files.length} file(s)
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 mb-4">
                    {filePreviews.map((preview, index) => (
                      <div key={index} className="relative group">
                        <div className="aspect-square rounded border-2 border-[#333344] overflow-hidden bg-[#0F0F1E]">
                          <img
                            src={preview.preview}
                            alt={preview.file.name}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div className="mt-1 text-xs text-gray-400 truncate">
                          {preview.file.name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatFileSize(preview.file.size)}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <PixelButton onClick={handleConvert} disabled={isConverting} loading={isConverting}>
                      Convert {files.length} Image{files.length > 1 ? 's' : ''}
                    </PixelButton>
                    <PixelButton variant="secondary" onClick={handleClear} disabled={isConverting}>
                      <Trash2 size={16} />
                      Clear All
                    </PixelButton>
                  </div>
                </div>
              )}
            </PixelCard>

            {/* Progress */}
            {isConverting && (
              <PixelCard title="Converting..." icon={<ImageIcon size={20} />} hoverable={false}>
                <PixelProgress value={progress} max={100} />
                <p className="text-sm text-gray-400 mt-2">
                  Processing {files.length} image(s)... {progress}%
                </p>
              </PixelCard>
            )}

            {/* Results */}
            {results.length > 0 && (
              <PixelCard
                title={`Conversion Results (${results.length})`}
                icon={<CheckCircle size={20} />}
                hoverable={false}
              >
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-400">
                      Successfully converted {results.length} image(s)
                    </p>
                    <PixelButton size="sm" onClick={handleDownloadAll}>
                      <Download size={16} />
                      Download All as ZIP
                    </PixelButton>
                  </div>

                  <div className="space-y-3">
                    {results.map((result, index) => (
                      <div
                        key={index}
                        className="border-2 border-[#333344] p-4 bg-[#0F0F1E] rounded"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate mb-1" title={result.original_filename}>
                              {result.original_filename}
                            </p>
                            <div className="flex items-center gap-3 text-xs text-gray-400">
                              <span>{formatFileSize(result.size)}</span>
                              <span>→</span>
                              <span className="text-[#4ECDC4]">{result.output_format.toUpperCase()}</span>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <PixelButton
                              size="sm"
                              variant="secondary"
                              onClick={() => handlePreview(result)}
                            >
                              <Eye size={14} />
                            </PixelButton>
                            <PixelButton
                              size="sm"
                              onClick={() => handleDownload(result.converted_filename)}
                            >
                              <Download size={14} />
                            </PixelButton>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </PixelCard>
            )}

            {/* Errors */}
            {errors.length > 0 && (
              <PixelCard
                title={`Errors (${errors.length})`}
                icon={<XCircle size={20} />}
                hoverable={false}
              >
                <div className="space-y-2">
                  {errors.map((error, index) => (
                    <div
                      key={index}
                      className="border-2 border-red-500/30 p-3 bg-red-900/20 rounded"
                    >
                      <p className="text-sm font-medium text-red-400">
                        {error.filename}
                      </p>
                      <p className="text-xs text-red-300 mt-1">
                        {error.error}
                      </p>
                    </div>
                  ))}
                </div>
              </PixelCard>
            )}
          </div>

          {/* Settings Sidebar - 1 column */}
          <div className="space-y-6">
            <PixelCard title="Settings" icon={<ImageIcon size={20} />} hoverable={false}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Output Format
                  </label>
                  <PixelSelect
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                    options={[
                      { value: 'jpg', label: 'JPG' },
                      { value: 'png', label: 'PNG' },
                      { value: 'webp', label: 'WebP' }
                    ]}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Quality: {quality}%
                  </label>
                  <PixelSlider
                    value={quality}
                    onChange={(value) => setQuality(value)}
                    min={1}
                    max={100}
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Higher quality = larger file size
                  </p>
                </div>

                <div className="pt-3 border-t border-[#333344]">
                  <PixelCheckbox
                    checked={enableResize}
                    onChange={(e) => setEnableResize(e.target.checked)}
                    label="Enable Resize"
                  />
                </div>

                {enableResize && (
                  <div className="space-y-3 pl-4 border-l-2 border-[#4ECDC4]/30">
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Width (px)
                      </label>
                      <PixelInput
                        type="number"
                        value={width}
                        onChange={(e) => setWidth(e.target.value)}
                        placeholder="Auto"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Height (px)
                      </label>
                      <PixelInput
                        type="number"
                        value={height}
                        onChange={(e) => setHeight(e.target.value)}
                        placeholder="Auto"
                      />
                    </div>

                    <p className="text-xs text-gray-400">
                      Leave empty to maintain aspect ratio
                    </p>
                  </div>
                )}
              </div>
            </PixelCard>

            <PixelCard title="Info" hoverable={false}>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="font-medium text-gray-300 mb-1">Supported Formats:</p>
                  <p className="text-gray-400 text-xs">
                    JPG, PNG, WebP, GIF, BMP
                  </p>
                </div>
                <div className="pt-2 border-t border-[#333344]">
                  <p className="text-xs text-gray-400">
                    Max file size: 10 MB per image
                  </p>
                </div>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>

      {/* Compare View Modal */}
      {compareView && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setCompareView(null)}>
          <div className="max-w-6xl w-full bg-[#1A1A2E] border-2 border-[#4ECDC4] rounded p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-pixel text-lg text-[#4ECDC4]">Before & After Comparison</h3>
              <button onClick={() => setCompareView(null)} className="text-gray-400 hover:text-white">
                <X size={24} />
              </button>
            </div>
            <p className="text-sm text-gray-400 mb-4">{compareView.filename}</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-400 mb-2 text-center">Original</p>
                <div className="border-2 border-[#333344] rounded overflow-hidden bg-[#0F0F1E]">
                  <img src={compareView.original} alt="Original" className="w-full h-auto" />
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-2 text-center">Converted ({outputFormat.toUpperCase()})</p>
                <div className="border-2 border-[#4ECDC4] rounded overflow-hidden bg-[#0F0F1E]">
                  <img src={compareView.converted} alt="Converted" className="w-full h-auto" />
                </div>
              </div>
            </div>
            <div className="mt-4 text-center">
              <PixelButton onClick={() => handleDownload(results.find(r => r.original_filename === compareView.filename)?.converted_filename || '')}>
                <Download size={16} />
                Download Converted Image
              </PixelButton>
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
