'use client';

import { useState, useEffect } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelInput } from '@/components/ui/PixelInput';
import { PixelLoading } from '@/components/ui/PixelLoading';
import { PixelTextarea } from '@/components/ui/PixelTextarea';
import { Settings as SettingsIcon, Key, Save, Trash2, Plus, CheckCircle, XCircle, Youtube } from 'lucide-react';

interface APIKeyStatus {
  configured: boolean;
  keys_count: number;
  keys: string[];
}

export default function SettingsPage() {
  const [apiKeys, setApiKeys] = useState<string[]>(['']);
  const [keyStatus, setKeyStatus] = useState<APIKeyStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadKeyStatus();
  }, []);

  const loadKeyStatus = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/settings/youtube-keys/status`);
      const data = await response.json();

      if (data.code === 200) {
        setKeyStatus(data.data);
        if (data.data.keys_count > 0) {
          // Load masked keys for display
          setApiKeys(data.data.keys.map((key: string) => key));
        }
      }
    } catch (error) {
      console.error('Error loading key status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddKey = () => {
    setApiKeys([...apiKeys, '']);
  };

  const handleRemoveKey = (index: number) => {
    const newKeys = apiKeys.filter((_, i) => i !== index);
    setApiKeys(newKeys.length === 0 ? [''] : newKeys);
  };

  const handleKeyChange = (index: number, value: string) => {
    const newKeys = [...apiKeys];
    newKeys[index] = value;
    setApiKeys(newKeys);
  };

  const handleSave = async () => {
    // Filter out empty keys
    const validKeys = apiKeys.filter(key => key.trim() !== '' && !key.startsWith('***'));

    if (validKeys.length === 0) {
      setMessage('Please enter at least one valid API key');
      setMessageType('error');
      return;
    }

    setIsSaving(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE}/api/settings/youtube-keys`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_keys: validKeys,
          per_key_budget: 9800
        }),
      });

      const data = await response.json();

      if (data.code === 200) {
        setMessage(`Successfully saved ${validKeys.length} API key(s)!`);
        setMessageType('success');
        await loadKeyStatus();
      } else {
        setMessage(data.message || 'Failed to save API keys');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Network error. Please try again.');
      setMessageType('error');
      console.error('Save error:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Are you sure you want to clear all API keys? This will disable YouTube features.')) {
      return;
    }

    setIsSaving(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE}/api/settings/youtube-keys`, {
        method: 'DELETE',
      });

      const data = await response.json();

      if (data.code === 200) {
        setMessage('All API keys cleared');
        setMessageType('success');
        setApiKeys(['']);
        await loadKeyStatus();
      } else {
        setMessage('Failed to clear API keys');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Network error. Please try again.');
      setMessageType('error');
      console.error('Clear error:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <div>
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <SettingsIcon className="w-12 h-12 text-primary" />
              <h1 className="font-pixel text-3xl text-primary">Settings</h1>
            </div>
            <p className="text-gray-400 font-body">
              Configure application settings and API keys
            </p>
          </div>

          {/* YouTube API Keys Section */}
          <PixelCard className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <Youtube className="w-6 h-6 text-primary" />
              <h2 className="font-pixel text-xl text-primary">YouTube API Keys</h2>
            </div>

            {/* Status Display */}
            {keyStatus && (
              <div className="mb-6 p-4 bg-dark/50 rounded pixel-border border border-gray-700">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500 font-body mb-1">Status</p>
                    <div className="flex items-center gap-2">
                      {keyStatus.configured ? (
                        <>
                          <CheckCircle className="w-4 h-4 text-success" />
                          <span className="font-pixel text-sm text-success">Configured</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-4 h-4 text-danger" />
                          <span className="font-pixel text-sm text-danger">Not Configured</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 font-body mb-1">Keys Count</p>
                    <p className="font-pixel text-sm text-secondary">{keyStatus.keys_count}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Instructions */}
            <div className="mb-6 p-4 bg-accent/10 border-2 border-accent rounded pixel-border">
              <p className="text-sm text-gray-300 font-body mb-2">
                <strong>How to get YouTube API keys:</strong>
              </p>
              <ol className="text-xs text-gray-400 font-body space-y-1 ml-4">
                <li>1. Visit <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">Google Cloud Console</a></li>
                <li>2. Create a new project or select existing one</li>
                <li>3. Enable "YouTube Data API v3"</li>
                <li>4. Create credentials (API Key)</li>
                <li>5. Copy and paste the key(s) below</li>
              </ol>
              <p className="text-xs text-gray-400 font-body mt-2">
                💡 <strong>Tip:</strong> Add multiple keys to automatically rotate when quota is exceeded
              </p>
            </div>

            {/* API Keys Input */}
            <div className="space-y-4 mb-6">
              {isLoading ? (
                <PixelLoading text="Loading settings..." />
              ) : (
                <>
                  {apiKeys.map((key, index) => (
                    <div key={index} className="flex gap-2">
                      <div className="flex-grow">
                        <PixelInput
                          type="text"
                          value={key}
                          onChange={(e) => handleKeyChange(index, e.target.value)}
                          placeholder={`API Key #${index + 1} (e.g., AIzaSyXXXXXXXXXXXXXXXXXX)`}
                          className="w-full font-mono text-sm"
                        />
                      </div>
                      {apiKeys.length > 1 && (
                        <PixelButton
                          onClick={() => handleRemoveKey(index)}
                          variant="danger"
                          size="sm"
                          icon={<Trash2 className="w-4 h-4" />}
                        >
                          Remove
                        </PixelButton>
                      )}
                    </div>
                  ))}

                  <PixelButton
                    onClick={handleAddKey}
                    variant="secondary"
                    size="sm"
                    icon={<Plus className="w-4 h-4" />}
                    className="w-full"
                  >
                    Add Another Key
                  </PixelButton>
                </>
              )}
            </div>

            {/* Message Display */}
            {message && (
              <div className={`mb-6 p-4 rounded pixel-border border-2 ${
                messageType === 'success'
                  ? 'bg-success/20 border-success text-success'
                  : 'bg-danger/20 border-danger text-danger'
              }`}>
                <p className="font-body text-sm">{message}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4">
              <PixelButton
                onClick={handleSave}
                loading={isSaving}
                icon={<Save className="w-4 h-4" />}
                className="flex-grow"
              >
                Save API Keys
              </PixelButton>

              {keyStatus && keyStatus.configured && (
                <PixelButton
                  onClick={handleClearAll}
                  variant="danger"
                  disabled={isSaving}
                  icon={<Trash2 className="w-4 h-4" />}
                >
                  Clear All
                </PixelButton>
              )}
            </div>
          </PixelCard>

          {/* Additional Info */}
          <PixelCard hoverable={false}>
            <h3 className="font-pixel text-sm text-primary mb-3">About API Keys</h3>
            <div className="space-y-2 text-xs text-gray-400 font-body">
              <p>
                <strong>Daily Quota:</strong> Each Google account has 10,000 units/day
              </p>
              <p>
                <strong>Search Cost:</strong> ~100 units per search
              </p>
              <p>
                <strong>Multiple Keys:</strong> System automatically rotates to next key when one is exhausted
              </p>
              <p>
                <strong>Security:</strong> Keys are stored encrypted and only partial keys are displayed
              </p>
            </div>
          </PixelCard>
        </div>
      </div>
    </MainLayout>
  );
}
