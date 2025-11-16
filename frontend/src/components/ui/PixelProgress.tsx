'use client';

interface PixelProgressProps {
  value: number;
  max?: number;
  showPercentage?: boolean;
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  animated?: boolean;
}

export function PixelProgress({
  value,
  max = 100,
  showPercentage = true,
  variant = 'secondary',
  animated = true,
}: PixelProgressProps) {
  const percentage = Math.min((value / max) * 100, 100);

  const variantColors = {
    primary: '#FF6B6B',
    secondary: '#4ECDC4',
    success: '#51CF66',
    danger: '#FF6B6B',
  };

  return (
    <div className="w-full">
      <div className="pixel-progress">
        <div
          className={`pixel-progress-bar ${animated ? 'transition-all duration-300' : ''}`}
          style={{
            width: `${percentage}%`,
            backgroundColor: variantColors[variant],
          }}
        />
      </div>
      {showPercentage && (
        <div className="text-center font-pixel text-xs mt-2">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
}
