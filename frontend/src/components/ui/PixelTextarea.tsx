'use client';

import { TextareaHTMLAttributes, forwardRef } from 'react';

interface PixelTextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const PixelTextarea = forwardRef<HTMLTextAreaElement, PixelTextareaProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block font-pixel text-xs mb-2 text-secondary">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={`pixel-input resize-y min-h-[100px] ${error ? 'border-danger' : ''} ${className}`}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-danger">{error}</p>
        )}
      </div>
    );
  }
);

PixelTextarea.displayName = 'PixelTextarea';
