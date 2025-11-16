'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { TextStats } from '@/components/features/TextStats';
import { BarChart3, RotateCcw } from 'lucide-react';

export default function StatisticsPage() {
  const [text, setText] = useState('');

  const loadSample = () => {
    setText(`Welcome to the Text Statistics Tool!

This is a sample text that demonstrates how the statistics analyzer works. It contains multiple paragraphs, sentences, and words.

The tool will count:
- Total characters (including spaces)
- Characters without spaces
- Total number of words
- Number of lines in the text
- Number of sentences (based on punctuation)
- Number of paragraphs

You can also see average metrics like average word length and average words per sentence. These metrics can be helpful for writers, students, and content creators who need to meet specific word count or character limit requirements.

Try typing your own text to see real-time statistics!`);
  };

  const handleReset = () => {
    setText('');
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <BarChart3 size={32} />
            Text Statistics
          </h1>
          <p className="text-pixel-text-secondary">
            Analyze your text and get detailed statistics. All analysis is done locally.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <PixelCard title="Input Text">
              <PixelTextarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type or paste your text here to see statistics..."
                rows={15}
                className="w-full"
              />
              <div className="mt-4 flex gap-2">
                <PixelButton onClick={loadSample}>
                  Load Sample Text
                </PixelButton>
                <PixelButton variant="secondary" onClick={handleReset}>
                  <RotateCcw size={16} />
                  Clear
                </PixelButton>
              </div>
            </PixelCard>

            {text && <TextStats text={text} />}

            {!text && (
              <PixelCard>
                <div className="text-center py-8 text-pixel-text-secondary">
                  <BarChart3 size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Enter some text above to see statistics</p>
                </div>
              </PixelCard>
            )}
          </div>

          <div className="space-y-6">
            <PixelCard title="What is analyzed?">
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Characters</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Total number of characters including spaces, punctuation, and special characters.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Characters (no spaces)</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Character count excluding all whitespace characters.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Words</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Number of words separated by whitespace. Hyphenated words count as one.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Lines</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Total number of lines in the text, including empty lines.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Sentences</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Number of sentences detected by punctuation marks (. ! ?).
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Paragraphs</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Text blocks separated by blank lines.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Averages</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Average word length and average words per sentence for readability analysis.
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Use Cases">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>• Check word count for essays and articles</p>
                <p>• Verify character limits for social media</p>
                <p>• Analyze text complexity and readability</p>
                <p>• Track writing progress</p>
                <p>• Optimize content for SEO</p>
                <p>• Prepare text for publishing</p>
                <div className="pt-2 border-t border-pixel-border mt-3">
                  <p className="text-xs">
                    Statistics update in real-time as you type!
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Privacy">
              <p className="text-sm text-pixel-text-secondary">
                All analysis happens in your browser. Your text is never sent to any server and is not stored.
              </p>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
