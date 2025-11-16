'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { PixelCheckbox } from '@/components/ui/PixelCheckbox';
import { PixelSelect } from '@/components/ui/PixelSelect';
import { ArrowUpDown, Copy, Check, RotateCcw } from 'lucide-react';

type SortType = 'alphabetical' | 'numerical' | 'length' | 'random';

export default function SorterPage() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [sortType, setSortType] = useState<SortType>('alphabetical');
  const [options, setOptions] = useState({
    reverse: false,
    caseSensitive: false,
    removeEmptyLines: true,
    removeDuplicates: false
  });
  const [copied, setCopied] = useState(false);

  const sortLines = () => {
    let lines = inputText.split('\n');

    if (options.removeEmptyLines) {
      lines = lines.filter(line => line.trim() !== '');
    }

    if (options.removeDuplicates) {
      lines = [...new Set(lines)];
    }

    switch (sortType) {
      case 'alphabetical':
        lines.sort((a, b) => {
          const lineA = options.caseSensitive ? a : a.toLowerCase();
          const lineB = options.caseSensitive ? b : b.toLowerCase();
          return lineA.localeCompare(lineB);
        });
        break;

      case 'numerical':
        lines.sort((a, b) => {
          const numA = parseFloat(a) || 0;
          const numB = parseFloat(b) || 0;
          return numA - numB;
        });
        break;

      case 'length':
        lines.sort((a, b) => a.length - b.length);
        break;

      case 'random':
        lines.sort(() => Math.random() - 0.5);
        break;
    }

    if (options.reverse) {
      lines.reverse();
    }

    setOutputText(lines.join('\n'));
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(outputText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setInputText('');
    setOutputText('');
    setSortType('alphabetical');
    setOptions({
      reverse: false,
      caseSensitive: false,
      removeEmptyLines: true,
      removeDuplicates: false
    });
  };

  const loadSample = () => {
    if (sortType === 'alphabetical') {
      setInputText(`Zebra
Apple
Banana
apple
Cherry
Banana`);
    } else if (sortType === 'numerical') {
      setInputText(`10
2
100
5
20
1`);
    } else if (sortType === 'length') {
      setInputText(`Hello
World
A
JavaScript
React
To`);
    } else {
      setInputText(`Item 1
Item 2
Item 3
Item 4
Item 5`);
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <ArrowUpDown size={32} />
            Text Sorter
          </h1>
          <p className="text-pixel-text-secondary">
            Sort lines of text in various ways. All processing is done locally.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <PixelCard title="Input Text">
              <PixelTextarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter each line to sort (one per line)..."
                rows={12}
                className="w-full"
              />
              <div className="mt-4 flex gap-2">
                <PixelButton onClick={sortLines}>
                  Sort Lines
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

            <PixelCard title="Sorted Output">
              <PixelTextarea
                value={outputText}
                onChange={(e) => setOutputText(e.target.value)}
                placeholder="Sorted lines will appear here..."
                rows={12}
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
                        Copy
                      </>
                    )}
                  </PixelButton>
                  <div className="text-sm text-pixel-text-secondary flex items-center">
                    {outputText.split('\n').length} lines sorted
                  </div>
                </div>
              )}
            </PixelCard>
          </div>

          <div className="space-y-6">
            <PixelCard title="Sort Settings">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Sort Type</label>
                  <PixelSelect
                    value={sortType}
                    onChange={(e) => setSortType(e.target.value as SortType)}
                    options={[
                      { value: 'alphabetical', label: 'Alphabetical (A-Z)' },
                      { value: 'numerical', label: 'Numerical (0-9)' },
                      { value: 'length', label: 'By Length (Short-Long)' },
                      { value: 'random', label: 'Random Shuffle' }
                    ]}
                  />
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Options">
              <div className="space-y-3">
                <PixelCheckbox
                  checked={options.reverse}
                  onChange={(checked) => setOptions({...options, reverse: checked})}
                  label="Reverse Order"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Sort in descending order (Z-A, 9-0, etc.)
                </p>

                {sortType === 'alphabetical' && (
                  <>
                    <PixelCheckbox
                      checked={options.caseSensitive}
                      onChange={(checked) => setOptions({...options, caseSensitive: checked})}
                      label="Case Sensitive"
                    />
                    <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                      Treat uppercase and lowercase differently
                    </p>
                  </>
                )}

                <PixelCheckbox
                  checked={options.removeEmptyLines}
                  onChange={(checked) => setOptions({...options, removeEmptyLines: checked})}
                  label="Remove Empty Lines"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Skip blank lines when sorting
                </p>

                <PixelCheckbox
                  checked={options.removeDuplicates}
                  onChange={(checked) => setOptions({...options, removeDuplicates: checked})}
                  label="Remove Duplicates"
                />
                <p className="text-xs text-pixel-text-secondary ml-6 -mt-2">
                  Keep only unique lines
                </p>
              </div>
            </PixelCard>

            <PixelCard title="Sort Types">
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Alphabetical</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Sort lines alphabetically from A to Z (or Z to A if reversed)
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Numerical</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Sort lines by numeric value (extracts first number from each line)
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">By Length</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Sort lines by their length (shortest to longest)
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Random</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Randomly shuffle all lines (different each time)
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Usage Tips">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>• Each line is sorted independently</p>
                <p>• Empty lines can be removed automatically</p>
                <p>• Duplicate lines can be filtered</p>
                <p>• Use reverse option to flip the order</p>
                <div className="pt-2 border-t border-pixel-border mt-3">
                  <p className="text-xs">
                    Tip: Try "Load Sample" to see examples for each sort type!
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Privacy">
              <p className="text-sm text-pixel-text-secondary">
                All sorting happens in your browser. No data is sent to any server.
              </p>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
