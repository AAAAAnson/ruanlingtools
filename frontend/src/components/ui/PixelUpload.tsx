'use client';

import { Upload, X } from 'lucide-react';
import { useCallback, useState } from 'react';

interface PixelUploadProps {
  onFilesSelected: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
  maxFiles?: number;
  maxSizeMB?: number;
}

export function PixelUpload({
  onFilesSelected,
  accept,
  multiple = true,
  maxFiles = 10,
  maxSizeMB = 50,
}: PixelUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files) return;
      const fileArray = Array.from(files).slice(0, maxFiles);
      const validFiles = fileArray.filter(
        (file) => file.size <= maxSizeMB * 1024 * 1024
      );
      setSelectedFiles(validFiles);
      onFilesSelected(validFiles);
    },
    [maxFiles, maxSizeMB, onFilesSelected]
  );

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
  };

  return (
    <div className="w-full">
      <div
        className={`pixel-card text-center cursor-pointer transition-all ${
          isDragging ? 'border-primary bg-primary/10' : ''
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
      >
        <input
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="cursor-pointer block">
          <Upload className="w-12 h-12 mx-auto mb-4 text-secondary" />
          <p className="font-pixel text-sm mb-2">Drop files here or click to upload</p>
          <p className="text-xs text-gray-400">
            Max {maxFiles} files, {maxSizeMB}MB each
          </p>
        </label>
      </div>
      {selectedFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          {selectedFiles.map((file, index) => (
            <div key={index} className="pixel-card flex items-center justify-between">
              <span className="text-sm truncate flex-1">{file.name}</span>
              <span className="text-xs text-gray-400 mx-2">
                {(file.size / 1024 / 1024).toFixed(2)}MB
              </span>
              <button onClick={() => removeFile(index)} className="hover:text-danger">
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
