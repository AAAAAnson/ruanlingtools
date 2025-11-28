'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelInput } from '@/components/ui/PixelInput';
import { PixelLoading } from '@/components/ui/PixelLoading';
import { Search, Youtube, Users, Eye, ExternalLink, Settings as SettingsIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface Channel {
  channel_id: string;
  title: string;
  description: string;
  thumbnail: string;
  custom_url: string;
  subscriber_count: number;
  video_count: number;
  view_count: number;
  avg_views_per_video: number;
  url: string;
}

interface SearchResult {
  keyword: string;
  channels: Channel[];
  total_channels: number;
}

export default function YouTubePage() {
  const router = useRouter();
  const [keyword, setKeyword] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<SearchResult | null>(null);
  const [error, setError] = useState('');

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

  const handleSearch = async () => {
    if (!keyword.trim()) {
      setError('Please enter a search keyword');
      return;
    }

    setSearching(true);
    setError('');
    setResults(null);

    try {
      const res = await fetch(`${API_BASE}/youtube/kol-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: keyword.trim(),
          max_results: 20,
          min_subscribers: 10000
        })
      });

      const data = await res.json();

      if (data.code === 200) {
        setResults(data.data);
        if (data.data.total_channels === 0) {
          setError('No channels found for this keyword');
        }
      } else if (data.code === 503) {
        setError('Please configure YouTube API keys in Settings');
      } else {
        setError(data.message || 'Search failed');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Network error. Please try again.');
    } finally {
      setSearching(false);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Youtube className="w-12 h-12 text-red-500" />
            <h1 className="text-4xl font-bold pixel-text">YouTube KOL Search</h1>
          </div>
          <p className="text-gray-400">
            Search for influential YouTube channels by keyword
          </p>
        </motion.div>

        {/* Search Section */}
        <PixelCard className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Search className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">Search KOLs</h2>
            <button
              onClick={() => router.push('/settings')}
              className="ml-auto text-gray-400 hover:text-primary transition-colors"
              title="Manage API Keys"
            >
              <SettingsIcon className="w-5 h-5" />
            </button>
          </div>

          <div className="flex gap-3">
            <div className="flex-1">
              <PixelInput
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Enter search keyword (e.g., AI technology, Gaming)"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !searching) {
                    handleSearch();
                  }
                }}
                disabled={searching}
              />
            </div>
            <PixelButton
              onClick={handleSearch}
              loading={searching}
              disabled={searching}
              icon={<Search className="w-4 h-4" />}
            >
              Search
            </PixelButton>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-500/10 border-2 border-red-500 text-red-500 text-sm">
              {error}
            </div>
          )}
        </PixelCard>

        {/* Loading */}
        {searching && (
          <div className="text-center py-12">
            <PixelLoading />
            <p className="mt-4 text-gray-400">Searching YouTube channels...</p>
          </div>
        )}

        {/* Results */}
        {results && results.total_channels > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">
                Found {results.total_channels} Channel{results.total_channels > 1 ? 's' : ''}
              </h2>
              <span className="text-gray-400">Keyword: &quot;{results.keyword}&quot;</span>
            </div>

            {results.channels.map((channel, index) => (
              <motion.div
                key={channel.channel_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <PixelCard hoverable>
                  <div className="flex gap-4">
                    {/* Thumbnail */}
                    <div className="flex-shrink-0">
                      <img
                        src={channel.thumbnail}
                        alt={channel.title}
                        className="w-24 h-24 rounded-lg object-cover"
                      />
                    </div>

                    {/* Channel Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h3 className="text-xl font-bold text-white truncate">
                          {channel.title}
                        </h3>
                        <a
                          href={channel.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-shrink-0 text-primary hover:text-primary-light transition-colors"
                          title="Open YouTube Channel"
                        >
                          <ExternalLink className="w-5 h-5" />
                        </a>
                      </div>

                      <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                        {channel.description || 'No description available'}
                      </p>

                      {/* Statistics */}
                      <div className="grid grid-cols-3 gap-4">
                        <div className="flex items-center gap-2">
                          <Users className="w-4 h-4 text-primary" />
                          <div>
                            <div className="text-sm text-gray-400">Subscribers</div>
                            <div className="font-bold">{formatNumber(channel.subscriber_count)}</div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Youtube className="w-4 h-4 text-primary" />
                          <div>
                            <div className="text-sm text-gray-400">Videos</div>
                            <div className="font-bold">{formatNumber(channel.video_count)}</div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Eye className="w-4 h-4 text-primary" />
                          <div>
                            <div className="text-sm text-gray-400">Avg Views</div>
                            <div className="font-bold">{formatNumber(channel.avg_views_per_video)}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </PixelCard>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* No Results Message */}
        {results && results.total_channels === 0 && (
          <PixelCard>
            <div className="text-center py-12">
              <Youtube className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-xl text-gray-400">
                No channels found for &quot;{results.keyword}&quot;
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Try a different keyword or lower the minimum subscriber filter
              </p>
            </div>
          </PixelCard>
        )}
      </div>
    </MainLayout>
  );
}
