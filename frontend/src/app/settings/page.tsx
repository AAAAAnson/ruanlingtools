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

/**
 * API密钥汇总统计组件
 */
const ApiKeysSummary: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchSummary = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/settings/youtube/keys/detailed`);
      const data = await res.json();

      if (data.code === 200) {
        setSummary(data.data.summary);
      }
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading || !summary) {
    return <div className="text-sm text-gray-500">Loading summary...</div>;
  }

  return (
    <PixelCard className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
      <h3 className="text-lg font-bold mb-4 font-pixel">📊 API Keys Overview</h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {summary.total_keys}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Total Keys</div>
        </div>

        <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {summary.total_used.toLocaleString()}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Quota Used</div>
        </div>

        <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {summary.total_remaining.toLocaleString()}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Quota Remaining</div>
        </div>

        <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {summary.usage_percent.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Usage Rate</div>
        </div>
      </div>
    </PixelCard>
  );
};

/**
 * 批量添加API密钥组件 (手动输入)
 */
const BatchAddKeys: React.FC<{ onKeysAdded: () => void }> = ({ onKeysAdded }) => {
  const [keysText, setKeysText] = useState('');
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleBatchAdd = async () => {
    const keys = keysText
      .split('\n')
      .map(k => k.trim())
      .filter(k => k.length > 0);

    if (keys.length === 0) {
      setMessage('Please enter at least one API key');
      setMessageType('error');
      return;
    }

    setAdding(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE}/api/settings/youtube/keys/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_keys: keys })
      });

      const data = await response.json();

      if (data.code === 200) {
        setMessage(`Successfully added ${data.data.added_count} API key(s)!`);
        setMessageType('success');
        setKeysText('');
        onKeysAdded();
      } else {
        setMessage(data.message || 'Failed to add keys');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Network error. Please try again.');
      setMessageType('error');
      console.error('Batch add error:', error);
    } finally {
      setAdding(false);
    }
  };

  return (
    <PixelCard className="p-6">
      <h3 className="text-lg font-bold mb-4 font-pixel">➕ Batch Add Keys (Manual)</h3>

      <div className="mb-4 p-4 bg-green-500/10 border-2 border-green-500 rounded pixel-border">
        <p className="text-sm text-gray-300 font-body mb-2">
          <strong>Add multiple keys at once:</strong>
        </p>
        <p className="text-xs text-gray-400 font-body">
          Paste one API key per line. The system will validate and add them to your pool.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-body text-gray-300 mb-2">
            API Keys (one per line):
          </label>
          <PixelTextarea
            value={keysText}
            onChange={(e) => setKeysText(e.target.value)}
            placeholder="AIzaSyXXXXXXXXXXXXXXXXXX&#10;AIzaSyYYYYYYYYYYYYYYYYYY&#10;AIzaSyZZZZZZZZZZZZZZZZZZ"
            rows={6}
            className="w-full font-mono text-sm"
          />
          <p className="text-xs text-gray-500 mt-1">
            {keysText.split('\n').filter(k => k.trim()).length} key(s) entered
          </p>
        </div>

        {message && (
          <div className={`p-4 rounded pixel-border border-2 ${
            messageType === 'success'
              ? 'bg-success/20 border-success text-success'
              : 'bg-danger/20 border-danger text-danger'
          }`}>
            <p className="font-body text-sm">{message}</p>
          </div>
        )}

        <PixelButton
          onClick={handleBatchAdd}
          loading={adding}
          icon={<Plus className="w-4 h-4" />}
          className="w-full"
        >
          {adding ? 'Adding...' : 'Add Keys'}
        </PixelButton>
      </div>
    </PixelCard>
  );
};

/**
 * API密钥列表组件 (显示详细状态)
 */
const ApiKeysList: React.FC = () => {
  const [keys, setKeys] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchKeys = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/settings/youtube/keys/detailed`);
      const data = await res.json();

      if (data.code === 200) {
        setKeys(data.data.keys);
      }
    } catch (error) {
      console.error('Failed to fetch keys:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleDelete = async (keyId: string) => {
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
        await fetchKeys();
      } else {
        alert('Failed to delete key: ' + data.message);
      }
    } catch (error) {
      alert('Network error. Please try again.');
      console.error('Delete error:', error);
    } finally {
      setDeleting(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-500';
      case 'quota_exceeded':
        return 'text-orange-500';
      case 'invalid':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      active: 'bg-green-500/20 border-green-500 text-green-500',
      quota_exceeded: 'bg-orange-500/20 border-orange-500 text-orange-500',
      invalid: 'bg-red-500/20 border-red-500 text-red-500'
    };

    return colors[status as keyof typeof colors] || 'bg-gray-500/20 border-gray-500 text-gray-500';
  };

  if (loading) {
    return <PixelLoading text="Loading API keys..." />;
  }

  if (keys.length === 0) {
    return (
      <PixelCard className="p-6 text-center">
        <p className="text-gray-400 font-body">No API keys configured yet.</p>
        <p className="text-xs text-gray-500 font-body mt-2">
          Use the batch generate or batch add features above to add keys.
        </p>
      </PixelCard>
    );
  }

  return (
    <PixelCard className="p-6">
      <h3 className="text-lg font-bold mb-4 font-pixel">📋 API Keys List ({keys.length})</h3>

      <div className="space-y-3">
        {keys.map((key, index) => (
          <div
            key={key.id || index}
            className="p-4 bg-dark/30 rounded pixel-border border border-gray-700 hover:border-primary transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-grow">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-mono text-sm text-gray-300">
                    {key.masked_key || '****...****'}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded border ${getStatusBadge(key.status)}`}>
                    {key.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-4 text-xs">
                  <div>
                    <span className="text-gray-500">Used:</span>{' '}
                    <span className="text-orange-400 font-bold">
                      {key.quota_used?.toLocaleString() || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Remaining:</span>{' '}
                    <span className="text-green-400 font-bold">
                      {key.quota_remaining?.toLocaleString() || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Budget:</span>{' '}
                    <span className="text-blue-400 font-bold">
                      {key.daily_budget?.toLocaleString() || 10000}
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      (key.quota_used / key.daily_budget) > 0.8
                        ? 'bg-red-500'
                        : (key.quota_used / key.daily_budget) > 0.5
                        ? 'bg-orange-500'
                        : 'bg-green-500'
                    }`}
                    style={{
                      width: `${Math.min((key.quota_used / key.daily_budget) * 100, 100)}%`
                    }}
                  />
                </div>

                {key.last_used && (
                  <p className="text-xs text-gray-500 mt-2">
                    Last used: {new Date(key.last_used).toLocaleString()}
                  </p>
                )}
              </div>

              <PixelButton
                onClick={() => handleDelete(key.id)}
                variant="danger"
                size="sm"
                icon={<Trash2 className="w-3 h-3" />}
                loading={deleting === key.id}
                disabled={deleting !== null}
              >
                Delete
              </PixelButton>
            </div>
          </div>
        ))}
      </div>
    </PixelCard>
  );
};

export default function SettingsPage() {
  const [apiKeys, setApiKeys] = useState<string[]>(['']);
  const [keyStatus, setKeyStatus] = useState<APIKeyStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');

  // Reddit API states
  const [redditClientId, setRedditClientId] = useState('');
  const [redditClientSecret, setRedditClientSecret] = useState('');
  const [redditUserAgent, setRedditUserAgent] = useState('');
  const [redditSaving, setRedditSaving] = useState(false);
  const [redditMessage, setRedditMessage] = useState('');
  const [redditMessageType, setRedditMessageType] = useState<'success' | 'error' | ''>('');
  const [redditConfigured, setRedditConfigured] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadKeyStatus();
    loadRedditConfig();
  }, []);

  const handleKeysAdded = () => {
    window.location.reload();
  };

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

  const loadRedditConfig = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/reddit/config`);
      const data = await response.json();

      if (data.code === 200) {
        setRedditConfigured(data.data.api_configured);
      }
    } catch (error) {
      console.error('Error loading Reddit config:', error);
    }
  };

  const handleSaveReddit = async () => {
    if (!redditClientId.trim() || !redditClientSecret.trim() || !redditUserAgent.trim()) {
      setRedditMessage('Please fill in all Reddit API credentials');
      setRedditMessageType('error');
      return;
    }

    setRedditSaving(true);
    setRedditMessage('');

    try {
      const response = await fetch(`${API_BASE}/api/settings/reddit`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_id: redditClientId.trim(),
          client_secret: redditClientSecret.trim(),
          user_agent: redditUserAgent.trim(),
        }),
      });

      const data = await response.json();

      if (data.code === 200) {
        setRedditMessage('Reddit API credentials saved successfully!');
        setRedditMessageType('success');
        setRedditConfigured(true);
      } else {
        setRedditMessage(data.message || 'Failed to save Reddit credentials');
        setRedditMessageType('error');
      }
    } catch (error) {
      setRedditMessage('Network error. Please try again.');
      setRedditMessageType('error');
      console.error('Save Reddit error:', error);
    } finally {
      setRedditSaving(false);
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

          {/* YouTube API Keys Section - Enhanced */}
          <PixelCard className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <Youtube className="w-6 h-6 text-primary" />
              <h2 className="font-pixel text-xl text-primary">YouTube API Keys</h2>
            </div>

            {/* YouTube API Keys - 增强版 */}
            <div className="space-y-6">
              {/* 顶部汇总统计 */}
              <ApiKeysSummary />

              {/* 批量添加区域 */}
              <BatchAddKeys onKeysAdded={handleKeysAdded} />

              {/* API密钥列表 */}
              <ApiKeysList />
            </div>
          </PixelCard>

          {/* Reddit API Configuration */}
          <PixelCard className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <svg className="w-6 h-6 text-primary" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
              </svg>
              <h2 className="font-pixel text-xl text-primary">Reddit API Configuration</h2>
              {redditConfigured && (
                <span className="ml-auto text-xs px-3 py-1 bg-green-500/20 border border-green-500 text-green-500 rounded">
                  ✓ Configured
                </span>
              )}
            </div>

            <div className="space-y-4">
              {/* Info Box */}
              <div className="p-4 bg-blue-500/10 border-2 border-blue-500/30 rounded pixel-border">
                <p className="text-sm text-gray-300 mb-2">
                  <strong>📝 How to get Reddit API credentials:</strong>
                </p>
                <ol className="text-xs text-gray-400 space-y-1 ml-4 list-decimal">
                  <li>Visit <a href="https://www.reddit.com/prefs/apps" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">reddit.com/prefs/apps</a></li>
                  <li>Click "create app" or "create another app"</li>
                  <li>Select "script" as the app type</li>
                  <li>Fill in name and description</li>
                  <li>Set redirect uri to: <code className="bg-gray-800 px-1 py-0.5 rounded">http://localhost:8080</code></li>
                  <li>Click "create app"</li>
                  <li>Copy the client ID (under app name) and client secret</li>
                </ol>
              </div>

              {/* Client ID */}
              <div>
                <label className="block text-sm font-pixel mb-2 text-gray-300">
                  Client ID
                </label>
                <PixelInput
                  type="text"
                  value={redditClientId}
                  onChange={(e) => setRedditClientId(e.target.value)}
                  placeholder="your_client_id"
                  className="w-full font-mono"
                />
              </div>

              {/* Client Secret */}
              <div>
                <label className="block text-sm font-pixel mb-2 text-gray-300">
                  Client Secret
                </label>
                <PixelInput
                  type="password"
                  value={redditClientSecret}
                  onChange={(e) => setRedditClientSecret(e.target.value)}
                  placeholder="your_client_secret"
                  className="w-full font-mono"
                />
              </div>

              {/* User Agent */}
              <div>
                <label className="block text-sm font-pixel mb-2 text-gray-300">
                  User Agent
                </label>
                <PixelInput
                  type="text"
                  value={redditUserAgent}
                  onChange={(e) => setRedditUserAgent(e.target.value)}
                  placeholder="platform:app_id:v1.0 (by /u/your_username)"
                  className="w-full font-mono"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Format: platform:app_id:version (by /u/username)
                  <br />
                  Example: linux:ruanlingtools:v1.0 (by /u/myusername)
                </p>
              </div>

              {/* Message */}
              {redditMessage && (
                <div className={`p-4 rounded pixel-border border-2 ${
                  redditMessageType === 'success'
                    ? 'bg-success/20 border-success text-success'
                    : 'bg-danger/20 border-danger text-danger'
                }`}>
                  <p className="font-body text-sm">{redditMessage}</p>
                </div>
              )}

              {/* Save Button */}
              <PixelButton
                onClick={handleSaveReddit}
                loading={redditSaving}
                icon={<Save className="w-4 h-4" />}
                className="w-full"
                size="lg"
              >
                Save Reddit Credentials
              </PixelButton>
            </div>
          </PixelCard>

          {/* Additional Info */}
          <PixelCard hoverable={false}>
            <h3 className="font-pixel text-sm text-primary mb-3">About API Keys</h3>
            <div className="space-y-2 text-xs text-gray-400 font-body">
              <p>
                <strong>YouTube Daily Quota:</strong> Each Google account has 10,000 units/day
              </p>
              <p>
                <strong>Search Cost:</strong> ~100 units per search
              </p>
              <p>
                <strong>Multiple Keys:</strong> System automatically rotates to next key when one is exhausted
              </p>
              <p>
                <strong>Reddit API:</strong> Free for personal use with reasonable rate limits
              </p>
              <p>
                <strong>Security:</strong> All credentials are stored securely on the server
              </p>
            </div>
          </PixelCard>
        </div>
      </div>
    </MainLayout>
  );
}
