'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelInput } from '@/components/ui/PixelInput';
import { PixelCheckbox } from '@/components/ui/PixelCheckbox';
import { PixelLoading } from '@/components/ui/PixelLoading';
import { Search, Youtube, Users, Eye, ThumbsUp, MessageSquare, ExternalLink, TrendingUp, Settings as SettingsIcon, Download, Database, Zap, History } from 'lucide-react';
import { motion } from 'framer-motion';

interface Video {
  video_id: string;
  title: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  engagement_rate: number;
  thumbnail: string;
  url: string;
}

interface Channel {
  channel_id: string;
  channel_title: string;
  channel_url: string;
  custom_url: string;
  description: string;
  thumbnail: string;
  country: string;
  subscriber_count: number;
  subscriber_count_formatted: string;
  total_video_count: number;
  total_view_count: number;
  keyword_videos_count: number;
  keyword_total_views: number;
  keyword_avg_views: number;
  keyword_avg_engagement: number;
  latest_videos: Video[];
}

interface SearchResults {
  keyword: string;
  channels: Channel[];
  total_channels: number;
  total_videos: number;
  timestamp: string;
}

export default function YouTubePage() {
  const router = useRouter();
  const [keyword, setKeyword] = useState('');
  const [minSubscribers, setMinSubscribers] = useState('10000');
  const [maxResults, setMaxResults] = useState('20');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<SearchResults | null>(null);
  const [error, setError] = useState('');
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);

  // Analysis options
  const [analysisMode, setAnalysisMode] = useState<'full' | 'db-only'>('full');
  const [getLatestVideos, setGetLatestVideos] = useState(true);

  // Advanced filters
  const [publishedAfter, setPublishedAfter] = useState('');
  const [publishedBefore, setPublishedBefore] = useState('');
  const [orderBy, setOrderBy] = useState('relevance');

  const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';

  const handleSearch = async () => {
    if (!keyword.trim()) {
      setError('Please enter a search keyword');
      return;
    }

    setIsSearching(true);
    setError('');
    setResults(null);
    setSelectedChannel(null);

    try {
      const requestBody: any = {
        keyword: keyword.trim(),
        max_results: parseInt(maxResults) || 20,
        min_subscribers: parseInt(minSubscribers) || 10000,
        db_only: analysisMode === 'db-only',
        get_latest_videos: getLatestVideos,
        order_by: orderBy,
      };

      // Add time range filters if provided
      if (publishedAfter) {
        requestBody.published_after = new Date(publishedAfter).toISOString();
      }
      if (publishedBefore) {
        requestBody.published_before = new Date(publishedBefore).toISOString();
      }

      const response = await fetch(`${API_BASE}/api/youtube/kol-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();

      if (data.code === 200) {
        setResults(data.data);
        if (data.data.total_channels === 0) {
          setError('No KOLs found for this keyword. Try adjusting your search criteria.');
        }
      } else {
        setError(data.message || 'Failed to search KOLs');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleExport = () => {
    if (!results) return;

    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `kol-search-${results.keyword}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000000) return `${(num / 1000000000).toFixed(1)}B`;
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        <div>
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Youtube className="w-12 h-12 text-primary" />
              <h1 className="font-pixel text-3xl text-primary">YouTube KOL Search</h1>
              <div className="flex gap-2">
                <PixelButton
                  onClick={() => window.open(`${API_BASE}/api/youtube/history`, '_blank')}
                  variant="accent"
                  size="sm"
                  icon={<History className="w-4 h-4" />}
                >
                  History
                </PixelButton>
                <PixelButton
                  onClick={() => router.push('/settings')}
                  variant="secondary"
                  size="sm"
                  icon={<SettingsIcon className="w-4 h-4" />}
                >
                  Settings
                </PixelButton>
              </div>
            </div>
            <p className="text-gray-400 font-body">
              Discover influential YouTube channels and analyze their performance
            </p>
          </div>

          {/* Search Form */}
          <PixelCard className="mb-8">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-pixel mb-2 text-gray-300">
                  Search Keyword
                </label>
                <PixelInput
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g., AI technology, Gaming, Cooking..."
                  className="w-full"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-pixel mb-2 text-gray-300">
                    Min Subscribers
                  </label>
                  <PixelInput
                    type="number"
                    value={minSubscribers}
                    onChange={(e) => setMinSubscribers(e.target.value)}
                    placeholder="10000"
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-pixel mb-2 text-gray-300">
                    Max Results
                  </label>
                  <PixelInput
                    type="number"
                    value={maxResults}
                    onChange={(e) => setMaxResults(e.target.value)}
                    placeholder="20"
                    min="1"
                    max="50"
                    className="w-full"
                  />
                </div>
              </div>

              {/* Time Range Filters */}
              <div className="border-t-2 border-gray-700 pt-4">
                <label className="block text-sm font-pixel mb-3 text-gray-300">
                  📅 Time Range (Optional)
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500 font-body mb-1">
                      Published After
                    </label>
                    <PixelInput
                      type="date"
                      value={publishedAfter}
                      onChange={(e) => setPublishedAfter(e.target.value)}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-gray-500 font-body mb-1">
                      Published Before
                    </label>
                    <PixelInput
                      type="date"
                      value={publishedBefore}
                      onChange={(e) => setPublishedBefore(e.target.value)}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-gray-500 font-body mb-1">
                      Sort By
                    </label>
                    <select
                      value={orderBy}
                      onChange={(e) => setOrderBy(e.target.value)}
                      className="w-full px-3 py-2 bg-dark border-2 border-gray-700 rounded pixel-border text-gray-300 font-body text-sm focus:border-primary focus:outline-none"
                    >
                      <option value="relevance">Relevance</option>
                      <option value="date">Date (Newest)</option>
                      <option value="viewCount">View Count</option>
                      <option value="rating">Rating</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Analysis Mode */}
              <div className="border-t-2 border-gray-700 pt-4">
                <label className="block text-sm font-pixel mb-3 text-gray-300">
                  🎯 Analysis Mode
                </label>
                <div className="space-y-3">
                  <div
                    onClick={() => setAnalysisMode('full')}
                    className={`p-4 rounded pixel-border border-2 cursor-pointer transition-all ${
                      analysisMode === 'full'
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-700 bg-dark/50 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Zap className={`w-5 h-5 ${analysisMode === 'full' ? 'text-primary' : 'text-gray-500'}`} />
                      <div className="flex-grow">
                        <p className={`font-pixel text-sm ${analysisMode === 'full' ? 'text-primary' : 'text-gray-300'}`}>
                          Full Analysis
                        </p>
                        <p className="text-xs text-gray-500 font-body mt-1">
                          Crawl fresh data from YouTube (consumes API quota)
                        </p>
                      </div>
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        analysisMode === 'full'
                          ? 'border-primary bg-primary'
                          : 'border-gray-600'
                      }`}>
                        {analysisMode === 'full' && (
                          <div className="w-full h-full rounded-full bg-white scale-50"></div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div
                    onClick={() => setAnalysisMode('db-only')}
                    className={`p-4 rounded pixel-border border-2 cursor-pointer transition-all ${
                      analysisMode === 'db-only'
                        ? 'border-secondary bg-secondary/10'
                        : 'border-gray-700 bg-dark/50 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Database className={`w-5 h-5 ${analysisMode === 'db-only' ? 'text-secondary' : 'text-gray-500'}`} />
                      <div className="flex-grow">
                        <p className={`font-pixel text-sm ${analysisMode === 'db-only' ? 'text-secondary' : 'text-gray-300'}`}>
                          Database Only
                        </p>
                        <p className="text-xs text-gray-500 font-body mt-1">
                          Fast analysis using cached data (no API consumption)
                        </p>
                      </div>
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        analysisMode === 'db-only'
                          ? 'border-secondary bg-secondary'
                          : 'border-gray-600'
                      }`}>
                        {analysisMode === 'db-only' && (
                          <div className="w-full h-full rounded-full bg-white scale-50"></div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Advanced Options */}
              <div className="border-t-2 border-gray-700 pt-4">
                <label className="block text-sm font-pixel mb-3 text-gray-300">
                  ⚙️ Advanced Options
                </label>
                <div className="p-4 rounded pixel-border border-2 border-gray-700 bg-dark/50">
                  <PixelCheckbox
                    checked={getLatestVideos}
                    onChange={(e) => setGetLatestVideos(e.target.checked)}
                    label="Fetch latest 10 videos for each channel (requires API quota)"
                  />
                  <p className="text-xs text-gray-500 font-body mt-2 ml-6">
                    💡 Recommended for fresh performance metrics, but uses more API quota
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <PixelButton
                  onClick={handleSearch}
                  loading={isSearching}
                  icon={<Search className="w-4 h-4" />}
                  className="flex-grow"
                  size="lg"
                >
                  {analysisMode === 'db-only' ? 'Analyze from Database' : 'Start Analysis'}
                </PixelButton>
                {results && (
                  <PixelButton
                    onClick={handleExport}
                    variant="success"
                    icon={<Download className="w-4 h-4" />}
                    size="lg"
                  >
                    Export
                  </PixelButton>
                )}
              </div>

              {error && (
                <div className="p-4 bg-danger/20 border-2 border-danger text-danger rounded pixel-border">
                  <p className="font-body text-sm">{error}</p>
                </div>
              )}
            </div>
          </PixelCard>

          {/* Loading */}
          {isSearching && (
            <div className="flex justify-center">
              <PixelLoading text="Searching for KOLs..." />
            </div>
          )}

          {/* Results */}
          {results && results.total_channels > 0 && (
            <div>
              {/* Stats Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <PixelCard hoverable={false}>
                  <div className="flex items-center gap-3">
                    <Users className="w-8 h-8 text-primary" />
                    <div>
                      <p className="text-2xl font-pixel text-primary">{results.total_channels}</p>
                      <p className="text-sm text-gray-400 font-body">Channels Found</p>
                    </div>
                  </div>
                </PixelCard>

                <PixelCard hoverable={false}>
                  <div className="flex items-center gap-3">
                    <Youtube className="w-8 h-8 text-secondary" />
                    <div>
                      <p className="text-2xl font-pixel text-secondary">{results.total_videos}</p>
                      <p className="text-sm text-gray-400 font-body">Videos Analyzed</p>
                    </div>
                  </div>
                </PixelCard>

                <PixelCard hoverable={false}>
                  <div className="flex items-center gap-3">
                    <TrendingUp className="w-8 h-8 text-accent" />
                    <div>
                      <p className="text-2xl font-pixel text-accent">{results.keyword}</p>
                      <p className="text-sm text-gray-400 font-body">Search Keyword</p>
                    </div>
                  </div>
                </PixelCard>
              </div>

              {/* Channels List */}
              <div className="space-y-4">
                <h2 className="font-pixel text-xl text-primary mb-4">Top KOL Channels</h2>

                {results.channels.map((channel, index) => (
                  <PixelCard
                    key={channel.channel_id}
                    onClick={() => setSelectedChannel(
                      selectedChannel?.channel_id === channel.channel_id ? null : channel
                    )}
                    className="cursor-pointer"
                  >
                    <div className="flex flex-col md:flex-row gap-4">
                      {/* Channel Thumbnail */}
                      <div className="flex-shrink-0">
                        <img
                          src={channel.thumbnail || '/placeholder-channel.png'}
                          alt={channel.channel_title}
                          className="w-24 h-24 rounded-full pixel-border border-2 border-primary"
                        />
                      </div>

                      {/* Channel Info */}
                      <div className="flex-grow">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="font-pixel text-lg text-primary mb-1">
                              #{index + 1} {channel.channel_title}
                            </h3>
                            <p className="text-sm text-gray-400 font-body line-clamp-2">
                              {channel.description || 'No description available'}
                            </p>
                          </div>
                          <a
                            href={channel.channel_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-primary hover:text-secondary transition-colors"
                          >
                            <ExternalLink className="w-5 h-5" />
                          </a>
                        </div>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                          <div>
                            <p className="text-xs text-gray-500 font-body mb-1">Subscribers</p>
                            <p className="font-pixel text-sm text-secondary">
                              {channel.subscriber_count_formatted}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500 font-body mb-1">Total Videos</p>
                            <p className="font-pixel text-sm text-accent">
                              {formatNumber(channel.total_video_count)}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500 font-body mb-1">Avg Views</p>
                            <p className="font-pixel text-sm text-success">
                              {formatNumber(channel.keyword_avg_views)}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500 font-body mb-1">Engagement</p>
                            <p className="font-pixel text-sm text-primary">
                              {channel.keyword_avg_engagement.toFixed(2)}%
                            </p>
                          </div>
                        </div>

                        {/* Latest Videos (Expandable) */}
                        {selectedChannel?.channel_id === channel.channel_id && channel.latest_videos.length > 0 && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2, ease: 'easeOut' }}
                            className="mt-4 pt-4 border-t-2 border-gray-700 overflow-hidden"
                          >
                            <h4 className="font-pixel text-sm text-primary mb-3">Latest Videos</h4>
                            <div className="space-y-2">
                              {channel.latest_videos.map((video) => (
                                <div
                                  key={video.video_id}
                                  className="flex gap-3 p-2 bg-dark/50 rounded pixel-border border border-gray-700 hover:border-primary transition-colors"
                                >
                                  <img
                                    src={video.thumbnail || '/placeholder-video.png'}
                                    alt={video.title}
                                    className="w-20 h-12 object-cover rounded"
                                  />
                                  <div className="flex-grow min-w-0">
                                    <a
                                      href={video.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      onClick={(e) => e.stopPropagation()}
                                      className="text-sm text-gray-300 hover:text-primary transition-colors font-body line-clamp-1"
                                    >
                                      {video.title}
                                    </a>
                                    <div className="flex gap-4 mt-1 text-xs text-gray-500">
                                      <span className="flex items-center gap-1">
                                        <Eye className="w-3 h-3" />
                                        {formatNumber(video.view_count)}
                                      </span>
                                      <span className="flex items-center gap-1">
                                        <ThumbsUp className="w-3 h-3" />
                                        {formatNumber(video.like_count)}
                                      </span>
                                      <span className="flex items-center gap-1">
                                        <MessageSquare className="w-3 h-3" />
                                        {formatNumber(video.comment_count)}
                                      </span>
                                      <span className="text-primary">
                                        {video.engagement_rate.toFixed(2)}%
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}
                      </div>
                    </div>
                  </PixelCard>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
