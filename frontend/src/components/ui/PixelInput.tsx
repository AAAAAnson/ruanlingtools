'use client';

import { InputHTMLAttributes, forwardRef } from 'react';

interface PixelInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const PixelInput = forwardRef<HTMLInputElement, PixelInputProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block font-pixel text-xs mb-2 text-secondary">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`pixel-input ${error ? 'border-danger' : ''} ${className}`}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-danger">{error}</p>
        )}
      </div>
    );
  }
);

PixelInput.displayName = 'PixelInput';
