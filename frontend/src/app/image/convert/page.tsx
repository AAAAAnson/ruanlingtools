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
import { Download, Image as ImageIcon, FileImage, CheckCircle, XCircle, Trash2 } from 'lucide-react';

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

export default function ImageConvertPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [outputFormat, setOutputFormat] = useState('png');
  const [quality, setQuality] = useState(85);
  const [enableResize, setEnableResize] = useState(false);
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [isConverting, setIsConverting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ConversionResult[]>([]);
  const [errors, setErrors] = useState<Array<{ filename: string; error: string }>>([]);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleFilesSelected = (selectedFiles: File[]) => {
    setFiles(selectedFiles);
    setResults([]);
    setErrors([]);
  };

  const handleConvert = async () => {
    if (files.length === 0) {
      return;
    }

    setIsConverting(true);
    setProgress(0);
    setResults([]);
    setErrors([]);

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

      const response = await fetch(`${API_BASE}/api/image/convert`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.code === 200 && data.data) {
        const conversionData = data.data as ConversionResponse;
        setResults(conversionData.results || []);
        setErrors(conversionData.errors || []);
        setProgress(100);
      } else {
        setErrors([{ filename: 'All files', error: data.message || 'Conversion failed' }]);
      }
    } catch (error) {
      setErrors([{ filename: 'System', error: error instanceof Error ? error.message : 'Unknown error' }]);
    } finally {
      setIsConverting(false);
    }
  };

  const handleDownload = (filename: string) => {
    const downloadUrl = `${API_BASE}/api/image/download/${filename}`;
    window.open(downloadUrl, '_blank');
  };

  const handleDownloadAll = async () => {
    if (results.length === 0) return;

    try {
      const filenames = results.map(r => r.converted_filename);

      const response = await fetch(`${API_BASE}/api/image/download-zip`, {
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
    setResults([]);
    setErrors([]);
    setProgress(0);
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary">Image Format Converter</h1>
          <p className="text-pixel-text-secondary">
            Convert images between JPG, PNG, and WebP formats with batch processing support
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <PixelCard title="Upload Images">
              <PixelUpload
                multiple={true}
                accept="image/*"
                maxSizeMB={10}
                onFilesSelected={handleFilesSelected}
              />
              {files.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm text-pixel-text-secondary mb-2">
                    Selected: {files.length} file(s)
                  </p>
                  <div className="flex gap-2">
                    <PixelButton onClick={handleConvert} disabled={isConverting} loading={isConverting}>
                      Convert Images
                    </PixelButton>
                    <PixelButton variant="secondary" onClick={handleClear}>
                      <Trash2 size={16} />
                      Clear
                    </PixelButton>
                  </div>
                </div>
              )}
            </PixelCard>

            {isConverting && (
              <PixelCard title="Converting...">
                <PixelProgress value={progress} max={100} />
                <p className="text-sm text-pixel-text-secondary mt-2">
                  Processing {files.length} image(s)...
                </p>
              </PixelCard>
            )}

            {results.length > 0 && (
              <PixelCard
                title={`Conversion Results (${results.length})`}
                icon={<CheckCircle size={20} />}
              >
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-pixel-text-secondary">
                      Successfully converted {results.length} image(s)
                    </p>
                    <PixelButton size="sm" onClick={handleDownloadAll}>
                      <Download size={16} />
                      Download All
                    </PixelButton>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {results.map((result, index) => (
                      <div
                        key={index}
                        className="pixel-border p-4 bg-pixel-background-light"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate" title={result.original_filename}>
                              {result.original_filename}
                            </p>
                            <p className="text-xs text-pixel-text-secondary mt-1">
                              {result.size_mb} MB - {result.output_format.toUpperCase()}
                            </p>
                          </div>
                          <PixelButton
                            size="sm"
                            variant="secondary"
                            onClick={() => handleDownload(result.converted_filename)}
                          >
                            <Download size={14} />
                          </PixelButton>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </PixelCard>
            )}

            {errors.length > 0 && (
              <PixelCard
                title={`Errors (${errors.length})`}
                icon={<XCircle size={20} />}
              >
                <div className="space-y-2">
                  {errors.map((error, index) => (
                    <div
                      key={index}
                      className="pixel-border p-3 bg-red-50 dark:bg-red-900/20"
                    >
                      <p className="text-sm font-medium text-red-700 dark:text-red-400">
                        {error.filename}
                      </p>
                      <p className="text-xs text-red-600 dark:text-red-300 mt-1">
                        {error.error}
                      </p>
                    </div>
                  ))}
                </div>
              </PixelCard>
            )}
          </div>

          <div className="space-y-6">
            <PixelCard title="Conversion Settings">
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
                  <p className="text-xs text-pixel-text-secondary mt-1">
                    Higher quality = larger file size
                  </p>
                </div>

                <div>
                  <PixelCheckbox
                    checked={enableResize}
                    onChange={setEnableResize}
                    label="Enable Resize"
                  />
                </div>

                {enableResize && (
                  <div className="space-y-3 pl-6 border-l-2 border-pixel-primary/30">
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

                    <p className="text-xs text-pixel-text-secondary">
                      Leave empty to maintain aspect ratio
                    </p>
                  </div>
                )}
              </div>
            </PixelCard>

            <PixelCard title="Supported Formats">
              <div className="space-y-2 text-sm">
                <div>
                  <p className="font-medium mb-1">Input formats:</p>
                  <p className="text-pixel-text-secondary">
                    JPG, PNG, WebP, GIF, BMP
                  </p>
                </div>
                <div>
                  <p className="font-medium mb-1">Output formats:</p>
                  <p className="text-pixel-text-secondary">
                    JPG, PNG, WebP
                  </p>
                </div>
                <div className="pt-2 border-t border-pixel-border">
                  <p className="text-xs text-pixel-text-secondary">
                    Maximum file size: 10 MB per image
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
