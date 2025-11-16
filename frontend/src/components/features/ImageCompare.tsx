'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MoveHorizontal } from 'lucide-react';

interface ImageCompareProps {
  beforeImage: string;
  afterImage: string;
  beforeLabel?: string;
  afterLabel?: string;
}

export function ImageCompare({
  beforeImage,
  afterImage,
  beforeLabel = 'Before',
  afterLabel = 'After'
}: ImageCompareProps) {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    
    setSliderPosition(Math.max(0, Math.min(100, percentage)));
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      handleMove(e.clientX);
    }
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (isDragging && e.touches[0]) {
      handleMove(e.touches[0].clientX);
    }
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', () => setIsDragging(false));
      document.addEventListener('touchmove', handleTouchMove);
      document.addEventListener('touchend', () => setIsDragging(false));

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', () => setIsDragging(false));
        document.removeEventListener('touchmove', handleTouchMove);
        document.removeEventListener('touchend', () => setIsDragging(false));
      };
    }
  }, [isDragging]);

  const clipValue = 100 - sliderPosition;

  return (
    <div
      ref={containerRef}
      className="relative w-full aspect-video pixel-border overflow-hidden select-none cursor-ew-resize"
      onMouseDown={() => setIsDragging(true)}
      onTouchStart={() => setIsDragging(true)}
    >
      {/* After Image */}
      <div className="absolute inset-0">
        <img
          src={afterImage}
          alt={afterLabel}
          className="w-full h-full object-cover"
          draggable={false}
        />
        <div className="absolute top-4 right-4 bg-secondary px-3 py-1 font-pixel text-xs text-dark">
          {afterLabel}
        </div>
      </div>

      {/* Before Image */}
      <div
        className="absolute inset-0"
        style={{ clipPath: `inset(0 ${clipValue}% 0 0)` }}
      >
        <img
          src={beforeImage}
          alt={beforeLabel}
          className="w-full h-full object-cover"
          draggable={false}
        />
        <div className="absolute top-4 left-4 bg-primary px-3 py-1 font-pixel text-xs text-white">
          {beforeLabel}
        </div>
      </div>

      {/* Slider */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-white z-10"
        style={{ left: `${sliderPosition}%`, transform: 'translateX(-50%)' }}
      >
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-white pixel-border flex items-center justify-center cursor-grab active:cursor-grabbing"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <MoveHorizontal className="w-6 h-6 text-dark" />
        </motion.div>
      </div>
    </div>
  );
}
