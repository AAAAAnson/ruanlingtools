'use client';

import { Check } from 'lucide-react';
import { InputHTMLAttributes, forwardRef } from 'react';

interface PixelCheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

export const PixelCheckbox = forwardRef<HTMLInputElement, PixelCheckboxProps>(
  ({ label, className = '', ...props }, ref) => {
    return (
      <label className="flex items-center gap-3 cursor-pointer group">
        <div className="relative">
          <input
            ref={ref}
            type="checkbox"
            className="peer sr-only"
            {...props}
          />
          <div className="w-6 h-6 border-2 border-secondary bg-[#0F0F1E] peer-checked:bg-secondary peer-checked:border-secondary transition-all peer-focus:ring-2 peer-focus:ring-secondary/50" />
          <Check className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 text-dark opacity-0 peer-checked:opacity-100 transition-opacity pointer-events-none" />
        </div>
        {label && <span className="text-sm group-hover:text-secondary transition-colors">{label}</span>}
      </label>
    );
  }
);

PixelCheckbox.displayName = 'PixelCheckbox';
