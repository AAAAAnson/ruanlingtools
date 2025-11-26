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
import { Download, Image as ImageIcon, FileImage, CheckCircle, XCircle, Trash2, Eye, X, Upload, Loader2 } from 'lucide-react';

interface ConversionResult {
  original_filename: string;
  converted_filename: string;
  output_format: string;
  size: number;
  size_mb: number;
  download_url: string;
  requested_filename?: string;
}

interface ConversionResponse {
  total: number;
  successful: number;
  failed: number;
  results: ConversionResult[];
  errors?: Array<{ filename: string; original_filename?: string; error: string }>;
}

// 统一的文件项接口
interface FileItem {
  id: string;
  file: File;
  preview: string;
  status: 'pending' | 'converting' | 'success' | 'error';
  progress?: number;
  result?: ConversionResult;
  error?: string;
  displayName: string;
}

export default function ImageConvertPage() {
  // 使用统一的 FileItem 数组管理所有文件状态
  const [fileItems, setFileItems] = useState<FileItem[]>([]);
  const [outputFormat, setOutputFormat] = useState('png');
  const [quality, setQuality] = useState(85);
  const [enableResize, setEnableResize] = useState(false);
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [isConverting, setIsConverting] = useState(false);
  const [compareView, setCompareView] = useState<{ original: string; converted: string; filename: string } | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const extractBaseName = (filename: string): string => {
    const lastDotIndex = filename.lastIndexOf('.');
    if (lastDotIndex === -1) return filename;
    return filename.slice(0, lastDotIndex);
  };

  const handleFilesSelected = (selectedFiles: File[]) => {
    // 为每个新文件创建 FileItem
    const newItems: FileItem[] = [];
    let loadedCount = 0;

    selectedFiles.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        newItems.push({
          id: `${file.name}-${Date.now()}-${Math.random()}`,
          file,
          preview: reader.result as string,
          status: 'pending',
          displayName: extractBaseName(file.name)
        });
        loadedCount++;

        if (loadedCount === selectedFiles.length) {
          // 追加到现有列表
          setFileItems(prev => [...prev, ...newItems]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const handleConvert = async () => {
    // 找出所有待转换的文件
    const pendingItems = fileItems.filter(item => item.status === 'pending');
    if (pendingItems.length === 0) {
      return;
    }

    setIsConverting(true);

    // 将待转换的文件状态更新为 converting
    setFileItems(prev => prev.map(item =>
      item.status === 'pending'
        ? { ...item, status: 'converting' as const, progress: 0 }
        : item
    ));

    try {
      const formData = new FormData();

      pendingItems.forEach(item => {
        formData.append('files', item.file);
      });

      formData.append('target_names', JSON.stringify(pendingItems.map(item => ({
        original: item.file.name,
        custom: item.displayName
      }))));

      formData.append('output_format', outputFormat);
      formData.append('quality', quality.toString());

      if (enableResize && width) {
        formData.append('width', width);
      }
      if (enableResize && height) {
        formData.append('height', height);
      }

      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setFileItems(prev => prev.map(item =>
          item.status === 'converting'
            ? { ...item, progress: Math.min((item.progress || 0) + 15, 90) }
            : item
        ));
      }, 300);

      const response = await fetch(`${API_BASE}/image/convert`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      const data = await response.json();

      if (data.code === 200 && data.data) {
        const conversionData = data.data as ConversionResponse;

        // 更新每个文件的状态
        setFileItems(prev => prev.map(item => {
          if (item.status !== 'converting') return item;

          // 查找对应的结果
          const result = conversionData.results?.find(r => r.original_filename === item.file.name);
          if (result) {
            const requestedName = result.requested_filename || item.displayName;
            return {
              ...item,
              status: 'success' as const,
              progress: 100,
              result,
              displayName: requestedName
            };
          }

          // 查找对应的错误
          const error = conversionData.errors?.find(e =>
            e.filename === item.file.name || e.original_filename === item.file.name || e.filename === item.displayName
          );
          if (error) {
            return {
              ...item,
              status: 'error' as const,
              error: error.error
            };
          }

          // 如果没有结果也没有错误，标记为错误
          return {
            ...item,
            status: 'error' as const,
            error: 'Conversion failed'
          };
        }));
      } else {
        // 全部标记为失败
        setFileItems(prev => prev.map(item =>
          item.status === 'converting'
            ? { ...item, status: 'error' as const, error: data.message || 'Conversion failed' }
            : item
        ));
      }
    } catch (error) {
      // 全部标记为失败
      setFileItems(prev => prev.map(item =>
        item.status === 'converting'
          ? { ...item, status: 'error' as const, error: error instanceof Error ? error.message : 'Unknown error' }
          : item
      ));
    } finally {
      setIsConverting(false);
    }
  };

  const handleDownload = (filename: string) => {
    const downloadUrl = `${API_BASE}/image/download/${filename}`;
    window.open(downloadUrl, '_blank');
  };

  const handleDownloadAll = async () => {
    const successItems = fileItems.filter(item => item.status === 'success' && item.result);
    if (successItems.length === 0) return;

    try {
      const filenames = successItems.map(item => item.result!.converted_filename);

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
    setFileItems([]);
  };

  const handleRemoveFile = (id: string) => {
    setFileItems(prev => prev.filter(item => item.id !== id));
  };

  const handlePreview = (item: FileItem) => {
    if (!item.result) return;

    const convertedUrl = `${API_BASE}/image/download/${item.result.converted_filename}`;

    setCompareView({
      original: item.preview,
      converted: convertedUrl,
      filename: item.displayName
    });
  };

  const handleStartEditingName = (id: string) => {
    setEditingId(id);
  };

  const handleUpdateDisplayName = (id: string, value: string) => {
    setFileItems(prev => prev.map(item =>
      item.id === id
        ? { ...item, displayName: value }
        : item
    ));
  };

  const handleFinishEditing = (id: string) => {
    setFileItems(prev => prev.map(item => {
      if (item.id !== id) return item;
      const trimmed = item.displayName.trim();
      return {
        ...item,
        displayName: trimmed || extractBaseName(item.file.name)
      };
    }));
    setEditingId(null);
  };

  const pendingCount = fileItems.filter(item => item.status === 'pending').length;
  const convertingCount = fileItems.filter(item => item.status === 'converting').length;
  const successCount = fileItems.filter(item => item.status === 'success').length;
  const errorCount = fileItems.filter(item => item.status === 'error').length;

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient">Image Format Converter</h1>
          <p className="text-gray-300">
            Upload images, configure settings, and convert to your desired format
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content - 3 columns */}
          <div className="lg:col-span-3">
            {/* Single Unified Card */}
            <PixelCard hoverable={false}>
              {/* Header with Actions */}
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-pixel text-lg text-primary flex items-center gap-2">
                  <Upload size={20} />
                  Image Converter
                  {fileItems.length > 0 && <span className="text-sm text-gray-400">({fileItems.length})</span>}
                </h2>
                {fileItems.length > 0 && (
                  <div className="flex gap-2">
                    {successCount > 0 && (
                      <PixelButton
                        size="sm"
                        icon={<Download size={14} />}
                        onClick={handleDownloadAll}
                      >
                        Download All ({successCount})
                      </PixelButton>
                    )}
                    <PixelButton
                      size="sm"
                      variant="secondary"
                      icon={<Trash2 size={14} />}
                      onClick={handleClear}
                      disabled={isConverting}
                    >
                      Clear All
                    </PixelButton>
                  </div>
                )}
              </div>

              {/* Unified Upload & File List Area */}
              <div>
                {/* 如果没有文件，显示大的上传区域 */}
                {fileItems.length === 0 ? (
                  <PixelUpload
                    multiple={true}
                    accept="image/*"
                    maxSizeMB={10}
                    onFilesSelected={handleFilesSelected}
                  />
                ) : (
                  <>
                    {/* File List with integrated upload */}
                    <div className="border-2 border-dashed border-[#4ECDC4]/30 rounded-lg p-4 bg-[#0F0F1E]/50">
                      {/* Statistics */}
                      <div className="flex gap-4 mb-4 text-xs">
                        {pendingCount > 0 && (
                          <span className="text-gray-400">Pending: {pendingCount}</span>
                        )}
                        {convertingCount > 0 && (
                          <span className="text-yellow-400">Converting: {convertingCount}</span>
                        )}
                        {successCount > 0 && (
                          <span className="text-green-400">Success: {successCount}</span>
                        )}
                        {errorCount > 0 && (
                          <span className="text-red-400">Failed: {errorCount}</span>
                        )}
                      </div>

                      {/* File Items */}
                      <div className="space-y-2 mb-4">
                        {fileItems.map((item) => (
                          <div
                            key={item.id}
                            className="border-2 border-[#333344] p-3 bg-[#1A1A2E] rounded hover:border-[#4ECDC4]/50 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              {/* Thumbnail */}
                              <div className="flex-shrink-0 w-7 h-7 rounded border border-[#333344] overflow-hidden bg-black/30">
                                <img
                                  src={item.preview}
                                  alt={item.displayName}
                                  className="w-full h-full object-cover"
                                />
                              </div>

                              {/* File Info */}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  {editingId === item.id ? (
                                    <input
                                      autoFocus
                                      value={item.displayName}
                                      onChange={(e) => handleUpdateDisplayName(item.id, e.target.value)}
                                      onBlur={() => handleFinishEditing(item.id)}
                                      onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                          handleFinishEditing(item.id);
                                        }
                                        if (e.key === 'Escape') {
                                          setEditingId(null);
                                        }
                                      }}
                                      className="bg-[#0F0F1E] border border-[#4ECDC4]/40 rounded px-2 py-1 text-sm w-full focus:outline-none focus:border-[#4ECDC4]"
                                    />
                                  ) : (
                                    <p
                                      className="text-sm font-medium truncate cursor-text"
                                      title="Double-click to rename"
                                      onDoubleClick={() => handleStartEditingName(item.id)}
                                    >
                                      {item.displayName}
                                    </p>
                                  )}
                                </div>
                                <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
                                  <span>{formatFileSize(item.file.size)}</span>
                                  {item.result && (
                                    <>
                                      <span>→</span>
                                      <span className="text-[#4ECDC4]">
                                        {formatFileSize(item.result.size)} ({item.result.output_format.toUpperCase()})
                                      </span>
                                    </>
                                  )}
                                </div>
                              </div>

                              {/* Status Indicator */}
                              <div className="flex-shrink-0 min-w-[100px]">
                                {item.status === 'pending' && (
                                  <span className="text-xs text-gray-400 flex items-center gap-1">
                                    <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                                    Ready
                                  </span>
                                )}
                                {item.status === 'converting' && (
                                  <div className="flex items-center gap-2">
                                    <Loader2 size={14} className="animate-spin text-yellow-400" />
                                    <span className="text-xs text-yellow-400">{item.progress || 0}%</span>
                                  </div>
                                )}
                                {item.status === 'success' && (
                                  <span className="text-xs text-green-400 flex items-center gap-1">
                                    <CheckCircle size={14} />
                                    Complete
                                  </span>
                                )}
                                {item.status === 'error' && (
                                  <span className="text-xs text-red-400 flex items-center gap-1" title={item.error}>
                                    <XCircle size={14} />
                                    Failed
                                  </span>
                                )}
                              </div>

                              {/* Actions */}
                              <div className="flex gap-1 flex-shrink-0">
                                {item.status === 'success' && item.result && (
                                  <>
                                    <PixelButton
                                      size="sm"
                                      variant="secondary"
                                      icon={<Eye size={12} />}
                                      onClick={() => handlePreview(item)}
                                      title="Preview"
                                    />
                                    <PixelButton
                                      size="sm"
                                      icon={<Download size={12} />}
                                      onClick={() => handleDownload(item.result!.converted_filename)}
                                      title="Download"
                                    />
                                  </>
                                )}
                                {(item.status === 'pending' || item.status === 'error') && (
                                  <PixelButton
                                    size="sm"
                                    variant="danger"
                                    icon={<X size={12} />}
                                    onClick={() => handleRemoveFile(item.id)}
                                    disabled={isConverting}
                                    title="Remove"
                                  />
                                )}
                              </div>
                            </div>

                            {/* Error Message */}
                            {item.error && (
                              <div className="mt-2 text-xs text-red-300 bg-red-900/20 p-2 rounded border border-red-500/30">
                                {item.error}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>

                      {/* Compact Upload Area - 继续添加文件 */}
                      <div className="border-2 border-dashed border-[#333344] rounded p-3 text-center hover:border-[#4ECDC4]/50 transition-colors cursor-pointer">
                        <label className="cursor-pointer block">
                          <input
                            type="file"
                            multiple
                            accept="image/*"
                            className="hidden"
                            onChange={(e) => {
                              const files = Array.from(e.target.files || []);
                              if (files.length > 0) {
                                handleFilesSelected(files);
                              }
                              e.target.value = '';
                            }}
                          />
                          <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
                            <Upload size={16} />
                            <span>Click to add more images or drop them here</span>
                          </div>
                        </label>
                      </div>
                    </div>

                    {/* Convert Button */}
                    {pendingCount > 0 && (
                      <div className="mt-4">
                        <PixelButton
                          icon={<ImageIcon size={16} />}
                          onClick={handleConvert}
                          disabled={isConverting}
                          loading={isConverting}
                          className="w-full"
                        >
                          Convert {pendingCount} Image{pendingCount > 1 ? 's' : ''}
                        </PixelButton>
                      </div>
                    )}
                  </>
                )}
              </div>
            </PixelCard>
          </div>

          {/* Settings Sidebar - 1 column */}
          <div className="space-y-6">
            <PixelCard hoverable={false}>
              <div className="mb-4">
                <h2 className="font-pixel text-sm text-primary flex items-center gap-2">
                  <ImageIcon size={16} />
                  Settings
                </h2>
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

            <PixelCard hoverable={false}>
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
          </div>
        </div>
      )}
    </MainLayout>
  );
}
