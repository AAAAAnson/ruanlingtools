'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { Type, Copy, Check } from 'lucide-react';

export default function CaseConverterPage() {
  const [inputText, setInputText] = useState('');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const conversions = [
    {
      name: 'UPPERCASE',
      convert: (text: string) => text.toUpperCase(),
      description: 'Convert all letters to uppercase'
    },
    {
      name: 'lowercase',
      convert: (text: string) => text.toLowerCase(),
      description: 'Convert all letters to lowercase'
    },
    {
      name: 'Title Case',
      convert: (text: string) => {
        return text.replace(/\w\S*/g, (txt) => {
          return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        });
      },
      description: 'Capitalize first letter of each word'
    },
    {
      name: 'Sentence case',
      convert: (text: string) => {
        return text.toLowerCase().replace(/(^\s*\w|[.!?]\s*\w)/g, (c) => c.toUpperCase());
      },
      description: 'Capitalize first letter of each sentence'
    },
    {
      name: 'camelCase',
      convert: (text: string) => {
        const words = text.toLowerCase().split(/[\s_-]+/);
        return words[0] + words.slice(1).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('');
      },
      description: 'Convert to camelCase format'
    },
    {
      name: 'PascalCase',
      convert: (text: string) => {
        return text.toLowerCase().split(/[\s_-]+/).map(w =>
          w.charAt(0).toUpperCase() + w.slice(1)
        ).join('');
      },
      description: 'Convert to PascalCase format'
    },
    {
      name: 'snake_case',
      convert: (text: string) => {
        return text.toLowerCase().replace(/[\s-]+/g, '_');
      },
      description: 'Convert to snake_case format'
    },
    {
      name: 'kebab-case',
      convert: (text: string) => {
        return text.toLowerCase().replace(/[\s_]+/g, '-');
      },
      description: 'Convert to kebab-case format'
    },
    {
      name: 'CONSTANT_CASE',
      convert: (text: string) => {
        return text.toUpperCase().replace(/[\s-]+/g, '_');
      },
      description: 'Convert to CONSTANT_CASE format'
    },
    {
      name: 'iNVERSE cASE',
      convert: (text: string) => {
        return text.split('').map(c =>
          c === c.toUpperCase() ? c.toLowerCase() : c.toUpperCase()
        ).join('');
      },
      description: 'Invert the case of each letter'
    },
    {
      name: 'aLtErNaTiNg CaSe',
      convert: (text: string) => {
        return text.split('').map((c, i) =>
          i % 2 === 0 ? c.toLowerCase() : c.toUpperCase()
        ).join('');
      },
      description: 'Alternate between lower and upper case'
    }
  ];

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <Type size={32} />
            Case Converter
          </h1>
          <p className="text-pixel-text-secondary">
            Convert text between different cases. All processing is done locally in your browser.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <PixelCard title="Input Text">
              <PixelTextarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type or paste your text here..."
                rows={8}
                className="w-full"
              />
              <div className="mt-4 flex gap-2">
                <PixelButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setInputText('')}
                >
                  Clear
                </PixelButton>
                <PixelButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setInputText('Hello World! This is a sample text.')}
                >
                  Load Sample
                </PixelButton>
              </div>
            </PixelCard>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {conversions.map((conversion, index) => {
                const result = inputText ? conversion.convert(inputText) : '';
                const isCopied = copiedIndex === index;

                return (
                  <PixelCard key={conversion.name}>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h3 className="font-pixel text-sm">{conversion.name}</h3>
                        {inputText && (
                          <PixelButton
                            size="sm"
                            variant="secondary"
                            onClick={() => handleCopy(result, index)}
                          >
                            {isCopied ? (
                              <>
                                <Check size={14} />
                                Copied
                              </>
                            ) : (
                              <>
                                <Copy size={14} />
                                Copy
                              </>
                            )}
                          </PixelButton>
                        )}
                      </div>
                      <p className="text-xs text-pixel-text-secondary mb-2">
                        {conversion.description}
                      </p>
                      <div className="pixel-border p-3 bg-pixel-background-light min-h-[60px] break-words font-mono text-sm">
                        {result || (
                          <span className="text-pixel-text-secondary italic">
                            Result will appear here...
                          </span>
                        )}
                      </div>
                    </div>
                  </PixelCard>
                );
              })}
            </div>
          </div>

          <div className="space-y-6">
            <PixelCard title="About Case Converter">
              <div className="space-y-4 text-sm">
                <p className="text-pixel-text-secondary">
                  This tool converts text between different case formats commonly used in programming and writing.
                </p>
                <div>
                  <h4 className="font-medium mb-2">Available Formats:</h4>
                  <ul className="space-y-1 text-pixel-text-secondary">
                    <li>• UPPERCASE - All caps</li>
                    <li>• lowercase - All small</li>
                    <li>• Title Case - Words capitalized</li>
                    <li>• Sentence case - Sentences capitalized</li>
                    <li>• camelCase - Programming style</li>
                    <li>• PascalCase - Class names</li>
                    <li>• snake_case - Python style</li>
                    <li>• kebab-case - URL friendly</li>
                    <li>• CONSTANT_CASE - Constants</li>
                    <li>• iNVERSE cASE - Inverted</li>
                    <li>• aLtErNaTiNg CaSe - Alternating</li>
                  </ul>
                </div>
                <div className="pt-2 border-t border-pixel-border">
                  <p className="text-xs text-pixel-text-secondary">
                    Tip: Click the Copy button to copy any result to your clipboard.
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Privacy">
              <p className="text-sm text-pixel-text-secondary">
                All text processing happens in your browser. No data is sent to any server.
                Your text never leaves your device.
              </p>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
