/**
 * Pixel Art Theme Configuration
 *
 * This file defines the color scheme, fonts, and visual styles
 * for the pixel art themed interface.
 */

export const pixelTheme = {
  colors: {
    // Primary colors
    primary: '#FF6B6B',      // Pixel Red - main accent color
    secondary: '#4ECDC4',    // Pixel Cyan - secondary accent
    accent: '#FFE66D',       // Pixel Yellow - highlights

    // Status colors
    success: '#51CF66',      // Pixel Green - success states
    danger: '#FF6B6B',       // Pixel Red - error states
    warning: '#FFD93D',      // Pixel Yellow - warning states
    info: '#4ECDC4',         // Pixel Cyan - info states

    // Background colors
    dark: '#1A1A2E',         // Dark background
    darker: '#0F0F1E',       // Darker background
    light: '#F0F0F0',        // Light background

    // UI colors
    border: '#333344',       // Border color
    text: {
      primary: '#FFFFFF',    // Primary text (light)
      secondary: '#A0A0B0',  // Secondary text (dimmed)
      dark: '#1A1A2E',       // Dark text (for light backgrounds)
    },
  },

  fonts: {
    // Pixel font for headings, buttons, and key UI elements
    pixel: '"Press Start 2P", monospace',

    // Regular font for body text (more readable)
    body: '"Roboto", sans-serif',
  },

  shadows: {
    // Pixel-style shadow (no blur, just offset)
    pixel: '0 0 0 2px #000',

    // Glow effect for hover states
    glow: '0 0 20px currentColor',

    // Stronger glow for active states
    glowStrong: '0 0 30px currentColor',
  },

  spacing: {
    // Pixel-perfect spacing units (multiples of 4px)
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
    '3xl': '64px',
  },

  borderRadius: {
    // Minimal border radius for pixel aesthetic
    none: '0px',
    sm: '2px',
    md: '4px',
    lg: '8px',
  },

  transitions: {
    // Fast transitions for responsive feel
    fast: '0.1s ease-in-out',
    normal: '0.2s ease-in-out',
    slow: '0.3s ease-in-out',
  },
} as const;

// Export type for TypeScript autocomplete
export type PixelTheme = typeof pixelTheme;
