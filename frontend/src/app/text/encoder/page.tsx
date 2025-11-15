'use client';

import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { PixelSelect } from '@/components/ui/PixelSelect';
import { Code2, Copy, Check, ArrowRightLeft } from 'lucide-react';

type EncodingType = 'base64' | 'url' | 'html' | 'hex' | 'binary';

export default function EncoderPage() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [mode, setMode] = useState<'encode' | 'decode'>('encode');
  const [encodingType, setEncodingType] = useState<EncodingType>('base64');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  const encode = (text: string, type: EncodingType): string => {
    try {
      setError('');
      switch (type) {
        case 'base64':
          return btoa(unescape(encodeURIComponent(text)));
        case 'url':
          return encodeURIComponent(text);
        case 'html':
          return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
        case 'hex':
          return text
            .split('')
            .map(c => c.charCodeAt(0).toString(16).padStart(2, '0'))
            .join('');
        case 'binary':
          return text
            .split('')
            .map(c => c.charCodeAt(0).toString(2).padStart(8, '0'))
            .join(' ');
        default:
          return text;
      }
    } catch (err) {
      setError('Encoding failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
      return '';
    }
  };

  const decode = (text: string, type: EncodingType): string => {
    try {
      setError('');
      switch (type) {
        case 'base64':
          return decodeURIComponent(escape(atob(text)));
        case 'url':
          return decodeURIComponent(text);
        case 'html':
          const textarea = document.createElement('textarea');
          textarea.innerHTML = text;
          return textarea.value;
        case 'hex':
          return text
            .replace(/\s/g, '')
            .match(/.{1,2}/g)
            ?.map(byte => String.fromCharCode(parseInt(byte, 16)))
            .join('') || '';
        case 'binary':
          return text
            .split(' ')
            .map(byte => String.fromCharCode(parseInt(byte, 2)))
            .join('');
        default:
          return text;
      }
    } catch (err) {
      setError('Decoding failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
      return '';
    }
  };

  const handleProcess = () => {
    const result = mode === 'encode'
      ? encode(inputText, encodingType)
      : decode(inputText, encodingType);
    setOutputText(result);
  };

  const handleSwap = () => {
    setInputText(outputText);
    setOutputText(inputText);
    setMode(mode === 'encode' ? 'decode' : 'encode');
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(outputText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const loadSample = () => {
    if (encodingType === 'base64') {
      setInputText('Hello World! 你好世界！');
    } else if (encodingType === 'url') {
      setInputText('Hello World! https://example.com?foo=bar&baz=qux');
    } else if (encodingType === 'html') {
      setInputText('Hello <b>World</b> & "Friends"');
    } else if (encodingType === 'hex') {
      setInputText('Hello World!');
    } else if (encodingType === 'binary') {
      setInputText('ABC');
    }
  };

  const encodingOptions = [
    { value: 'base64', label: 'Base64', description: 'Encode binary data in ASCII format' },
    { value: 'url', label: 'URL Encode', description: 'Encode special characters for URLs' },
    { value: 'html', label: 'HTML Entities', description: 'Encode HTML special characters' },
    { value: 'hex', label: 'Hexadecimal', description: 'Convert to hexadecimal format' },
    { value: 'binary', label: 'Binary', description: 'Convert to binary format' }
  ];

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-pixel mb-4 text-pixel-primary flex items-center gap-3">
            <Code2 size={32} />
            Text Encoder / Decoder
          </h1>
          <p className="text-pixel-text-secondary">
            Encode and decode text in various formats. All processing is done locally.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <PixelCard title="Settings">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Encoding Type</label>
                  <PixelSelect
                    value={encodingType}
                    onChange={(e) => setEncodingType(e.target.value as EncodingType)}
                  >
                    {encodingOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </PixelSelect>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Mode</label>
                  <PixelSelect
                    value={mode}
                    onChange={(e) => setMode(e.target.value as 'encode' | 'decode')}
                  >
                    <option value="encode">Encode</option>
                    <option value="decode">Decode</option>
                  </PixelSelect>
                </div>
              </div>
              <p className="text-sm text-pixel-text-secondary mt-3">
                {encodingOptions.find(opt => opt.value === encodingType)?.description}
              </p>
            </PixelCard>

            <PixelCard title={mode === 'encode' ? 'Input Text (Plain)' : 'Input Text (Encoded)'}>
              <PixelTextarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={mode === 'encode' ? 'Enter text to encode...' : 'Enter encoded text to decode...'}
                rows={8}
                className="w-full"
              />
              <div className="mt-4 flex gap-2">
                <PixelButton onClick={handleProcess}>
                  {mode === 'encode' ? 'Encode' : 'Decode'}
                </PixelButton>
                <PixelButton variant="secondary" onClick={loadSample}>
                  Load Sample
                </PixelButton>
                <PixelButton variant="secondary" onClick={handleSwap}>
                  <ArrowRightLeft size={16} />
                  Swap
                </PixelButton>
              </div>
            </PixelCard>

            <PixelCard title={mode === 'encode' ? 'Output Text (Encoded)' : 'Output Text (Plain)'}>
              {error && (
                <div className="mb-3 pixel-border p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm">
                  {error}
                </div>
              )}
              <PixelTextarea
                value={outputText}
                onChange={(e) => setOutputText(e.target.value)}
                placeholder={mode === 'encode' ? 'Encoded text will appear here...' : 'Decoded text will appear here...'}
                rows={8}
                className="w-full"
                readOnly
              />
              {outputText && !error && (
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
                    {outputText.length} characters
                  </div>
                </div>
              )}
            </PixelCard>
          </div>

          <div className="space-y-6">
            <PixelCard title="Encoding Types">
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium mb-1">Base64</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Encodes binary data using 64 ASCII characters. Commonly used for email and data transfer.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">URL Encode</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Encodes special characters for safe use in URLs. Spaces become %20.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">HTML Entities</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Converts special characters to HTML entities. {"<"} becomes &lt;
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Hexadecimal</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Converts each character to its hexadecimal representation.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Binary</h4>
                  <p className="text-pixel-text-secondary text-xs">
                    Converts each character to 8-bit binary format.
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Usage Tips">
              <div className="space-y-2 text-sm text-pixel-text-secondary">
                <p>1. Select encoding type</p>
                <p>2. Choose encode or decode mode</p>
                <p>3. Enter your text</p>
                <p>4. Click process button</p>
                <p>5. Use Swap to quickly reverse</p>
                <div className="pt-2 border-t border-pixel-border mt-3">
                  <p className="text-xs">
                    Tip: Use "Load Sample" to see example text for each encoding type.
                  </p>
                </div>
              </div>
            </PixelCard>

            <PixelCard title="Privacy">
              <p className="text-sm text-pixel-text-secondary">
                All encoding/decoding happens in your browser. No data is transmitted to any server.
              </p>
            </PixelCard>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
