'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { PixelCheckbox } from '@/components/ui/PixelCheckbox';
import { AlignLeft, Copy, Check, RotateCcw } from 'lucide-react';

export default function FormatterPage() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [copied, setCopied] = useState(false);

  const [options, setOptions] = useState({
    trim: true,
    removeDuplicateLines: false,
    removeEmptyLines: false,
    addLineNumbers: false,
    removeExtraSpaces: false,
    removePunctuation: false
  });

  const formatText = () => {
    let result = inputText;

    if (options.trim) {
      result = result.split('\n').map(line => line.trim()).join('\n');
    }

    if (options.removeExtraSpaces) {
      result = result.split('\n').map(line =>
        line.replace(/\s+/g, ' ')
      ).join('\n');
    }

    if (options.removePunctuation) {
      result = result.replace(/[^\w\s\n]/g, '');
    }

    if (options.removeEmptyLines) {
      result = result.split('\n').filter(line => line.trim() !== '').join('\n');
    }

    if (options.removeDuplicateLines) {
      const lines = result.split('\n');
      const uniqueLines = [...new Set(lines)];
      result = uniqueLines.join('\n');
    }

    if (options.addLineNumbers) {
      result = result.split('\n').map((line, index) =>
        `${index + 1}. ${line}`
      ).join('\n');
    }

    setOutputText(result);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(outputText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setInputText('');
    setOutputText('');
    setOptions({
      trim: true,
      removeDuplicateLines: false,
      removeEmptyLines: false,
      addLineNumbers: false,
      removeExtraSpaces: false,
      removePunctuation: false
    });
  };

  const loadSample = () => {
    setInputText(`  Hello World!
    This is a sample text.

  This is a sample text.
    With   extra   spaces
And some punctuation!!!

  Empty lines above
`);
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <AlignLeft size={32} />
            Text Formatter
          </h1>
          <p className="text-pixel-text-secondary">
            Format and clean your text with various options. All processing is done locally.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <PixelCard title="Input Text">
              <PixelTextarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type or paste your text here..."
                rows={10}
                className="w-full"
              />
              <div className="mt-4 flex gap-2">
                <PixelButton onClick={formatText}>
                  Format Text
                </PixelButton>
                <PixelButton variant="secondary" onClick={loadSample}>
                  Load Sample
                </PixelButton>
                <PixelButton variant="secondary" onClick={handleReset}>
                  <RotateCcw size={16} />
                  Reset
                </PixelButton>
              </div>
            </PixelCard>

            <PixelCard title="Output Text">
              <PixelTextarea
                value={outputText}
                onChange={(e) => setOutputText(e.target.value)}
                placeholder="Formatted text will appear here..."
                rows={10}
                className="w-full"
                readOnly
              />
              {outputText && (
                <div className="mt-4 flex gap-2">
                  <PixelButton variant="secondary" onClick={handleCopy}>
                    {copied ? (
                      <>
                        <Check size={16} />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy size={16} />
                        Copy to Clipboard
                      </>
                    )}
                  </PixelButton>
                  <div className="text-sm text-pixel-text-secondary flex items-center">
                    {outputText.split('\n').length} lines, {outputText.length} characters
                  </div>
                </div>
              )}
            </PixelCard>
          </div>

          <div className="space-y-6">
            <PixelCard title="Formatting Options">
              <div className="space-y-3">
                <PixelCheckbox
                  checked={options.trim}
                  onChange={(e) => setOptions({...options, trim: e.target.checked})}
                  label="Trim Lines"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Remove leading and trailing whitespace
                </p>

                <PixelCheckbox
                  checked={options.removeExtraSpaces}
                  onChange={(e) => setOptions({...options, removeExtraSpaces: e.target.checked})}
                  label="Remove Extra Spaces"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Replace multiple spaces with single space
                </p>

                <PixelCheckbox
                  checked={options.removeEmptyLines}
                  onChange={(e) => setOptions({...options, removeEmptyLines: e.target.checked})}
                  label="Remove Empty Lines"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Delete all blank lines
                </p>

                <PixelCheckbox
                  checked={options.removeDuplicateLines}
                  onChange={(e) => setOptions({...options, removeDuplicateLines: e.target.checked})}
                  label="Remove Duplicate Lines"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Keep only unique lines
                </p>

                <PixelCheckbox
                  checked={options.removePunctuation}
                  onChange={(e) => setOptions({...options, removePunctuation: e.target.checked})}
                  label="Remove Punctuation"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Remove all punctuation marks
                </p>

                <PixelCheckbox
                  checked={options.addLineNumbers}
                  onChange={(e) => setOptions({...options, addLineNumbers: e.target.checked})}
                  label="Add Line Numbers"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Prefix each line with number
                </p>
              </div>
            </PixelCard>

            <PixelCard title="Usage Tips">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>1. Paste or type your text in the input box</p>
                <p>2. Select formatting options</p>
                <p>3. Click "Format Text" to process</p>
                <p>4. Copy the formatted result</p>
                <div className="pt-2 border-t border-pixel-border mt-3">
                  <p className="text-xs">
                    Tip: Options are applied in the order shown. Try different combinations!
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Privacy">
              <p className="text-sm text-pixel-text-secondary">
                All formatting happens in your browser. No data is sent to any server.
              </p>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
