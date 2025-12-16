'use client';

import { useState, useEffect } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelSelect } from '@/components/ui/PixelSelect';
import { Download, Mic, FileAudio, CheckCircle, XCircle, Trash2, X, Upload, Loader2, Eye, Copy, AlertCircle } from 'lucide-react';

interface TranscriptionResult {
  original_filename: string;
  file_size_mb: number;
  model_used: string;
  detected_language: string;
  language_probability: number;
  duration_seconds: number;
  output_format: string;
  output_filename: string;
  download_url: string;
  content: string | any;
}

interface AudioModel {
  name: string;
  display_name: string;
  memory_mb: number;
  speed: string;
  quality: string;
  description: string;
  max_audio_minutes: number;
  icon: string;
  available: boolean;
  model_size: string;
  recommended?: boolean;
  warning?: string;
}

interface FileItem {
  id: string;
  file: File;
  status: 'pending' | 'transcribing' | 'success' | 'error';
  progress?: number;
  result?: TranscriptionResult;
  error?: string;
}

export default function TranscribePage() {
  const [fileItems, setFileItems] = useState<FileItem[]>([]);
  const [modelSize, setModelSize] = useState('base');
  const [language, setLanguage] = useState('');
  const [outputFormat, setOutputFormat] = useState('txt');
  const [task, setTask] = useState('transcribe');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [availableModels, setAvailableModels] = useState<AudioModel[]>([]);
  const [previewContent, setPreviewContent] = useState<{ filename: string; content: string; format: string } | null>(null);

  // Always use relative URL for API calls (goes through nginx proxy)
  // This works in browser, and useEffect/handlers are client-side only
  const API_BASE = '/api';

  // Fetch available models on mount (client-side only)
  useEffect(() => {
    fetchAvailableModels();
  }, []);

  const fetchAvailableModels = async () => {
    try {
      // Add timestamp to prevent caching
      const url = `${API_BASE}/audio/models?t=${Date.now()}`;
      console.log('Fetching models from:', url);

      const response = await fetch(url, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache',
        },
      });
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const text = await response.text();
        console.error('Response not OK:', response.status, text.substring(0, 200));
        return;
      }

      const data = await response.json();
      console.log('Models data:', data);

      if (data.code === 200 && data.data) {
        setAvailableModels(data.data.models || []);
        // Set default model to recommended one
        const recommended = data.data.models.find((m: AudioModel) => m.recommended);
        if (recommended) {
          setModelSize(recommended.model_size);
        }
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
      if (error instanceof Error) {
        console.error('Error details:', error.message, error.stack);
      }
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleFilesSelected = (files: File[]) => {
    const newItems: FileItem[] = files.map(file => ({
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      file,
      status: 'pending'
    }));
    setFileItems(prev => [...prev, ...newItems]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFilesSelected(files);
    }
  };

  const handleTranscribe = async () => {
    const pendingItems = fileItems.filter(item => item.status === 'pending');
    if (pendingItems.length === 0) return;

    setIsTranscribing(true);

    // Process files one by one for better UX
    for (const item of pendingItems) {
      setFileItems(prev => prev.map(i =>
        i.id === item.id
          ? { ...i, status: 'transcribing' as const, progress: 0 }
          : i
      ));

      try {
        const formData = new FormData();
        formData.append('file', item.file);
        formData.append('model_size', modelSize);
        formData.append('output_format', outputFormat);
        formData.append('task', task);
        if (language) {
          formData.append('language', language);
        }

        // Simulate progress
        const progressInterval = setInterval(() => {
          setFileItems(prev => prev.map(i =>
            i.id === item.id && i.status === 'transcribing'
              ? { ...i, progress: Math.min((i.progress || 0) + 10, 90) }
              : i
          ));
        }, 1000);

        const response = await fetch(`${API_BASE}/audio/transcribe`, {
          method: 'POST',
          body: formData,
        });

        clearInterval(progressInterval);
        const data = await response.json();

        if (data.code === 200 && data.data) {
          setFileItems(prev => prev.map(i =>
            i.id === item.id
              ? {
                  ...i,
                  status: 'success' as const,
                  progress: 100,
                  result: data.data
                }
              : i
          ));
        } else {
          setFileItems(prev => prev.map(i =>
            i.id === item.id
              ? {
                  ...i,
                  status: 'error' as const,
                  error: data.message || 'Transcription failed'
                }
              : i
          ));
        }
      } catch (error) {
        setFileItems(prev => prev.map(i =>
          i.id === item.id
            ? {
                ...i,
                status: 'error' as const,
                error: error instanceof Error ? error.message : 'Unknown error'
              }
            : i
        ));
      }
    }

    setIsTranscribing(false);
  };

  const handleDownload = (filename: string) => {
    const downloadUrl = `${API_BASE}/audio/download/${filename}`;
    window.open(downloadUrl, '_blank');
  };

  const handlePreview = (item: FileItem) => {
    if (!item.result) return;

    let content = '';
    if (typeof item.result.content === 'string') {
      content = item.result.content;
    } else if (typeof item.result.content === 'object') {
      content = JSON.stringify(item.result.content, null, 2);
    }

    setPreviewContent({
      filename: item.file.name,
      content,
      format: item.result.output_format
    });
  };

  const handleCopyContent = () => {
    if (previewContent) {
      navigator.clipboard.writeText(previewContent.content);
    }
  };

  const handleRemoveFile = (id: string) => {
    setFileItems(prev => prev.filter(item => item.id !== id));
  };

  const handleClear = () => {
    setFileItems([]);
  };

  const pendingCount = fileItems.filter(item => item.status === 'pending').length;
  const transcribingCount = fileItems.filter(item => item.status === 'transcribing').length;
  const successCount = fileItems.filter(item => item.status === 'success').length;
  const errorCount = fileItems.filter(item => item.status === 'error').length;

  const selectedModel = availableModels.find(m => m.model_size === modelSize);

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-gradient">AI Speech to Text</h1>
          <p className="text-gray-300">
            Powered by OpenAI Whisper • Convert audio to text with 99+ language support
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content - 3 columns */}
          <div className="lg:col-span-3">
            <PixelCard hoverable={false}>
              {/* Header */}
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-pixel text-lg text-primary flex items-center gap-2">
                  <Mic size={20} />
                  Audio Transcription
                  {fileItems.length > 0 && <span className="text-sm text-gray-400">({fileItems.length})</span>}
                </h2>
                {fileItems.length > 0 && (
                  <PixelButton
                    size="sm"
                    variant="secondary"
                    icon={<Trash2 size={14} />}
                    onClick={handleClear}
                    disabled={isTranscribing}
                  >
                    Clear All
                  </PixelButton>
                )}
              </div>

              {/* Upload Area or File List */}
              {fileItems.length === 0 ? (
                <div
                  className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                    isDragging
                      ? 'border-primary bg-primary/10'
                      : 'border-[#4ECDC4]/30 bg-[#0F0F1E]/50'
                  }`}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setIsDragging(true);
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                >
                  <input
                    type="file"
                    accept="audio/*,.mp3,.wav,.m4a,.flac,.ogg,.aac"
                    multiple
                    onChange={(e) => {
                      const files = Array.from(e.target.files || []);
                      if (files.length > 0) {
                        handleFilesSelected(files);
                      }
                      e.target.value = '';
                    }}
                    className="hidden"
                    id="audio-upload"
                  />
                  <label htmlFor="audio-upload" className="cursor-pointer">
                    <FileAudio className="w-16 h-16 mx-auto mb-4 text-secondary" />
                    <p className="font-pixel text-lg mb-2">Drop audio files here or click to upload</p>
                    <p className="text-sm text-gray-400">
                      Supports MP3, WAV, M4A, FLAC, OGG, AAC
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                      Max 25MB per file
                    </p>
                  </label>
                </div>
              ) : (
                <>
                  {/* File List */}
                  <div className="border-2 border-dashed border-[#4ECDC4]/30 rounded-lg p-4 bg-[#0F0F1E]/50">
                    {/* Statistics */}
                    {fileItems.length > 0 && (
                      <div className="flex gap-4 mb-4 text-xs">
                        {pendingCount > 0 && <span className="text-gray-400">Pending: {pendingCount}</span>}
                        {transcribingCount > 0 && <span className="text-yellow-400">Processing: {transcribingCount}</span>}
                        {successCount > 0 && <span className="text-green-400">Success: {successCount}</span>}
                        {errorCount > 0 && <span className="text-red-400">Failed: {errorCount}</span>}
                      </div>
                    )}

                    {/* File Items */}
                    <div className="space-y-2 mb-4">
                      {fileItems.map((item) => (
                        <div
                          key={item.id}
                          className="border-2 border-[#333344] p-3 bg-[#1A1A2E] rounded hover:border-[#4ECDC4]/50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            {/* Icon */}
                            <div className="flex-shrink-0">
                              <FileAudio size={20} className="text-secondary" />
                            </div>

                            {/* File Info */}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium truncate">{item.file.name}</p>
                              <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
                                <span>{formatFileSize(item.file.size)}</span>
                                {item.result && (
                                  <>
                                    <span>•</span>
                                    <span className="text-[#4ECDC4]">
                                      {formatDuration(item.result.duration_seconds)}
                                    </span>
                                    <span>•</span>
                                    <span className="text-[#4ECDC4]">
                                      {item.result.detected_language.toUpperCase()}
                                    </span>
                                  </>
                                )}
                              </div>
                            </div>

                            {/* Status */}
                            <div className="flex-shrink-0 min-w-[120px]">
                              {item.status === 'pending' && (
                                <span className="text-xs text-gray-400 flex items-center gap-1">
                                  <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                                  Ready
                                </span>
                              )}
                              {item.status === 'transcribing' && (
                                <div className="flex items-center gap-2">
                                  <Loader2 size={14} className="animate-spin text-yellow-400" />
                                  <span className="text-xs text-yellow-400">Processing...</span>
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
                                    onClick={() => handleDownload(item.result!.output_filename)}
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
                                  disabled={isTranscribing}
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

                    {/* Add More */}
                    <div className="border-2 border-dashed border-[#333344] rounded p-3 text-center hover:border-[#4ECDC4]/50 transition-colors cursor-pointer">
                      <label className="cursor-pointer block">
                        <input
                          type="file"
                          accept="audio/*,.mp3,.wav,.m4a,.flac,.ogg,.aac"
                          multiple
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
                          <span>Click to add more audio files</span>
                        </div>
                      </label>
                    </div>
                  </div>

                  {/* Transcribe Button */}
                  {pendingCount > 0 && (
                    <div className="mt-4">
                      <PixelButton
                        icon={<Mic size={16} />}
                        onClick={handleTranscribe}
                        disabled={isTranscribing}
                        loading={isTranscribing}
                        className="w-full"
                      >
                        Transcribe {pendingCount} File{pendingCount > 1 ? 's' : ''}
                      </PixelButton>
                    </div>
                  )}
                </>
              )}
            </PixelCard>
          </div>

          {/* Settings Sidebar - 1 column */}
          <div className="space-y-6">
            {/* Model Selection */}
            <PixelCard hoverable={false}>
              <div className="mb-4">
                <h2 className="font-pixel text-sm text-primary flex items-center gap-2">
                  <Mic size={16} />
                  Settings
                </h2>
              </div>

              <div className="space-y-4">
                {/* Model */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Model
                  </label>
                  <PixelSelect
                    value={modelSize}
                    onChange={(e) => setModelSize(e.target.value)}
                    options={availableModels.map(m => ({
                      value: m.model_size,
                      label: `${m.icon} ${m.display_name}`,
                      disabled: !m.available
                    }))}
                  />
                  {selectedModel && (
                    <div className="mt-2 p-2 bg-[#0F0F1E] rounded border border-[#333344]">
                      <p className="text-xs text-gray-400">{selectedModel.description}</p>
                      <div className="mt-1 flex gap-2 text-xs">
                        <span className="text-gray-500">Speed: {selectedModel.speed}</span>
                        <span className="text-gray-500">•</span>
                        <span className="text-gray-500">Quality: {selectedModel.quality}</span>
                      </div>
                      {selectedModel.warning && (
                        <div className="mt-2 flex items-start gap-1 text-xs text-yellow-400">
                          <AlertCircle size={12} className="mt-0.5 flex-shrink-0" />
                          <span>{selectedModel.warning}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Language */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Language (Optional)
                  </label>
                  <PixelSelect
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    options={[
                      { value: '', label: 'Auto Detect' },
                      { value: 'zh', label: '中文 (Chinese)' },
                      { value: 'en', label: 'English' },
                      { value: 'ja', label: '日本語 (Japanese)' },
                      { value: 'ko', label: '한국어 (Korean)' },
                      { value: 'es', label: 'Español (Spanish)' },
                      { value: 'fr', label: 'Français (French)' },
                      { value: 'de', label: 'Deutsch (German)' },
                    ]}
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Leave empty for automatic detection
                  </p>
                </div>

                {/* Output Format */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Output Format
                  </label>
                  <PixelSelect
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                    options={[
                      { value: 'txt', label: 'Plain Text' },
                      { value: 'srt', label: 'SRT Subtitle' },
                      { value: 'vtt', label: 'WebVTT Subtitle' },
                      { value: 'json', label: 'JSON Data' },
                    ]}
                  />
                </div>

                {/* Task */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Task
                  </label>
                  <PixelSelect
                    value={task}
                    onChange={(e) => setTask(e.target.value)}
                    options={[
                      { value: 'transcribe', label: 'Transcribe' },
                      { value: 'translate', label: 'Translate to English' },
                    ]}
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Translate converts to English
                  </p>
                </div>
              </div>
            </PixelCard>

            {/* Info */}
            <PixelCard hoverable={false}>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="font-medium text-gray-300 mb-1">Supported Formats:</p>
                  <p className="text-gray-400 text-xs">
                    MP3, WAV, M4A, FLAC, OGG, AAC
                  </p>
                </div>
                <div className="pt-2 border-t border-[#333344]">
                  <p className="text-xs text-gray-400">
                    Max file size: 25 MB<br />
                    Supports 99+ languages
                  </p>
                </div>
              </div>
            </PixelCard>
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {previewContent && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setPreviewContent(null)}>
          <div className="max-w-4xl w-full bg-[#1A1A2E] border-2 border-[#4ECDC4] rounded p-6 max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-pixel text-lg text-[#4ECDC4]">Transcription Preview</h3>
              <div className="flex gap-2">
                <PixelButton
                  size="sm"
                  variant="secondary"
                  icon={<Copy size={14} />}
                  onClick={handleCopyContent}
                >
                  Copy
                </PixelButton>
                <button onClick={() => setPreviewContent(null)} className="text-gray-400 hover:text-white">
                  <X size={24} />
                </button>
              </div>
            </div>
            <p className="text-sm text-gray-400 mb-4">{previewContent.filename}</p>
            <div className="flex-1 overflow-auto bg-[#0F0F1E] border border-[#333344] rounded p-4">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                {previewContent.content}
              </pre>
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
