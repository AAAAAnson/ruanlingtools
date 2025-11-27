'use client';

import { useState, useEffect } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { Settings, Key, Trash2, Youtube, Check, X } from 'lucide-react';
import { motion } from 'framer-motion';

interface KeyInfo {
  id: string;
  masked_key: string;
  index: number;
}

export default function SettingsPage() {
  const [keys, setKeys] = useState<KeyInfo[]>([]);
  const [keysText, setKeysText] = useState('');
  const [adding, setAdding] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

  useEffect(() => {
    fetchKeys();
  }, []);

  const fetchKeys = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/settings/youtube/keys/detailed`);
      const data = await res.json();

      if (data.code === 200) {
        setKeys(data.data.keys || []);
      }
    } catch (error) {
      console.error('Failed to fetch keys:', error);
    }
  };

  const handleBatchAdd = async () => {
    const lines = keysText.split('\n').map(k => k.trim()).filter(k => k.length > 0);

    if (lines.length === 0) {
      setMessage('Please enter at least one API key');
      setMessageType('error');
      return;
    }

    setAdding(true);
    setMessage('');

    try {
      const res = await fetch(`${API_BASE}/api/settings/youtube/keys/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_keys: lines })
      });

      const data = await res.json();

      if (data.code === 200) {
        setMessage(`Successfully added ${data.data.added_count} key(s)!`);
        setMessageType('success');
        setKeysText('');
        fetchKeys();
      } else {
        setMessage(data.message || 'Failed to add keys');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Batch add error:', error);
      setMessage('Network error. Please try again.');
      setMessageType('error');
    } finally {
      setAdding(false);
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key?')) {
      return;
    }

    setDeleting(keyId);

    try {
      const res = await fetch(`${API_BASE}/api/settings/youtube/keys/${keyId}`, {
        method: 'DELETE'
      });

      const data = await res.json();

      if (data.code === 200) {
        fetchKeys();
        setMessage('Key deleted successfully');
        setMessageType('success');
      } else {
        setMessage(data.message || 'Failed to delete key');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Delete error:', error);
      setMessage('Network error. Please try again.');
      setMessageType('error');
    } finally {
      setDeleting(null);
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Settings className="w-12 h-12 text-primary" />
            <h1 className="text-4xl font-bold pixel-text">Settings</h1>
          </div>
          <p className="text-gray-400">
            Manage YouTube API Keys
          </p>
        </motion.div>

        {/* Current Keys */}
        <PixelCard className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Key className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">API Keys</h2>
            <span className="ml-auto text-sm text-gray-400">{keys.length} key(s)</span>
          </div>

          {keys.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Youtube className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No API keys configured</p>
              <p className="text-sm mt-1">Add keys below to start using YouTube features</p>
            </div>
          ) : (
            <div className="space-y-2">
              {keys.map((key) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between p-3 bg-gray-800/50 rounded border border-gray-700"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-500">#{key.index}</span>
                    <code className="text-sm font-mono text-primary">{key.masked_key}</code>
                  </div>
                  <button
                    onClick={() => handleDeleteKey(key.id)}
                    disabled={deleting === key.id}
                    className="text-red-500 hover:text-red-400 disabled:opacity-50 transition-colors"
                    title="Delete key"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </PixelCard>

        {/* Add Keys */}
        <PixelCard>
          <div className="flex items-center gap-2 mb-4">
            <Key className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">Add API Keys</h2>
          </div>

          <p className="text-sm text-gray-400 mb-4">
            Paste one API key per line. Keys will be automatically deduplicated.
          </p>

          <PixelTextarea
            value={keysText}
            onChange={(e) => setKeysText(e.target.value)}
            placeholder="AIzaSy... (one key per line)"
            rows={8}
            disabled={adding}
            className="mb-4"
          />

          {message && (
            <div className={`mb-4 p-3 rounded border-2 flex items-center gap-2 ${
              messageType === 'success'
                ? 'bg-green-500/10 border-green-500 text-green-500'
                : 'bg-red-500/10 border-red-500 text-red-500'
            }`}>
              {messageType === 'success' ? (
                <Check className="w-4 h-4" />
              ) : (
                <X className="w-4 h-4" />
              )}
              <span className="text-sm">{message}</span>
            </div>
          )}

          <div className="flex gap-3">
            <PixelButton
              onClick={handleBatchAdd}
              loading={adding}
              disabled={adding || keysText.trim().length === 0}
              className="flex-1"
            >
              {adding ? 'Adding Keys...' : 'Add Keys'}
            </PixelButton>
            <PixelButton
              onClick={() => setKeysText('')}
              disabled={adding || keysText.length === 0}
              variant="secondary"
            >
              Clear
            </PixelButton>
          </div>

          <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded text-sm text-gray-400">
            <strong className="text-blue-400">Note:</strong> YouTube API keys should start with &quot;AIza&quot; and be 39 characters long.
            Get your keys from the{' '}
            <a
              href="https://console.cloud.google.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 underline hover:text-blue-300"
            >
              Google Cloud Console
            </a>.
          </div>
        </PixelCard>
      </div>
    </MainLayout>
  );
}
