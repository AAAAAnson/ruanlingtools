'use client';

import { useState } from 'react';

interface PixelSliderProps {
  label?: string;
  min?: number;
  max?: number;
  step?: number;
  value: number;
  onChange: (value: number) => void;
  unit?: string;
}

export function PixelSlider({
  label,
  min = 0,
  max = 100,
  step = 1,
  value,
  onChange,
  unit = '',
}: PixelSliderProps) {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <label className="font-pixel text-xs text-secondary">{label}</label>
          <span className="font-pixel text-xs text-primary">
            {value}{unit}
          </span>
        </div>
      )}
      <div className="relative h-8">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="absolute w-full h-full opacity-0 cursor-pointer z-10"
        />
        <div className="absolute w-full h-full border-2 border-[#333344] bg-[#0F0F1E]">
          <div
            className="h-full bg-secondary transition-all duration-200"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}
