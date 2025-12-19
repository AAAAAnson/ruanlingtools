'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout/MainLayout';
import { PixelCard } from '@/components/ui/PixelCard';
import { PixelButton } from '@/components/ui/PixelButton';
import { PixelInput } from '@/components/ui/PixelInput';
import { PixelLoading } from '@/components/ui/PixelLoading';
import { PixelSelect } from '@/components/ui/PixelSelect';
import { Search, Download, ExternalLink, MessageSquare, ThumbsUp, Award, Users, Calendar, Settings as SettingsIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface RedditPost {
  id: string;
  title: string;
  url: string;
  author: string;
  subreddit: string;
  subreddit_subscribers: number;
  created_time: string;
  score: number;
  upvote_ratio: number;
  num_comments: number;
  num_awards: number;
  is_text_post: boolean;
  is_video: boolean;
  post_content: string;
  domain: string;
  link_flair_text: string;
  over_18: boolean;
}

interface SearchResults {
  keyword: string;
  subreddit: string;
  posts: RedditPost[];
  total: number;
  filters: {
    min_comments: number;
    min_score: number;
    time_range_years: number;
    exclude_promoted: boolean;
  };
  timestamp: string;
}

export default function RedditPage() {
  const router = useRouter();
  const [keyword, setKeyword] = useState('');
  const [subreddit, setSubreddit] = useState('all');
  const [limit, setLimit] = useState('100');
  const [minComments, setMinComments] = useState('0');
  const [minScore, setMinScore] = useState('0');
  const [timeRange, setTimeRange] = useState('3');
  const [isSearching, setIsSearching] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [results, setResults] = useState<SearchResults | null>(null);
  const [error, setError] = useState('');
  const [apiConfigured, setApiConfigured] = useState(true);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Check API configuration on mount
  useState(() => {
    checkApiConfig();
  });

  const checkApiConfig = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/reddit/config`);
      const data = await response.json();
      if (data.code === 200) {
        setApiConfigured(data.data.api_configured);
      }
    } catch (err) {
      console.error('Failed to check API config:', err);
    }
  };

  const handleSearch = async () => {
    if (!keyword.trim()) {
      setError('Please enter a search keyword');
      return;
    }

    if (!apiConfigured) {
      setError('Reddit API not configured. Please configure in Settings.');
      return;
    }

    setIsSearching(true);
    setError('');
    setResults(null);

    try {
      const response = await fetch(`${API_BASE}/api/reddit/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keyword: keyword.trim(),
          subreddit: subreddit || 'all',
          limit: parseInt(limit) || 100,
          min_comments: parseInt(minComments) || 0,
          min_score: parseInt(minScore) || 0,
          time_range_years: parseInt(timeRange) || 3,
        }),
      });

      const data = await response.json();

      if (data.code === 200) {
        setResults(data.data);
        if (data.data.total === 0) {
          setError('No posts found for this keyword. Try adjusting your search criteria.');
        }
      } else {
        setError(data.message || 'Failed to search Reddit');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleExport = async () => {
    if (!results) return;

    setIsExporting(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/api/reddit/search/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keyword: keyword.trim(),
          subreddit: subreddit || 'all',
          limit: parseInt(limit) || 100,
          min_comments: parseInt(minComments) || 0,
          min_score: parseInt(minScore) || 0,
          time_range_years: parseInt(timeRange) || 3,
        }),
      });

      if (response.ok) {
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `reddit_search_${keyword}_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        setError('Failed to export results');
      }
    } catch (err) {
      setError('Export error. Please try again.');
      console.error('Export error:', err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const timeAgo = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 30) return `${diffDays}d ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
    return `${Math.floor(diffDays / 365)}y ago`;
  };

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <svg className="w-12 h-12 text-primary" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
            </svg>
            <h1 className="font-pixel text-3xl text-primary">Reddit Keyword Search</h1>
            <PixelButton
              onClick={() => router.push('/settings')}
              variant="secondary"
              size="sm"
              icon={<SettingsIcon className="w-4 h-4" />}
            >
              Settings
            </PixelButton>
          </div>
          <p className="text-gray-400 font-body">
            Search Reddit posts by keyword and export to Excel
          </p>
        </div>

        {/* API Not Configured Warning */}
        {!apiConfigured && (
          <div className="mb-6 p-4 bg-yellow-500/20 border-2 border-yellow-500 rounded pixel-border">
            <div className="flex items-center gap-3">
              <span className="text-2xl">⚠️</span>
              <div className="flex-grow">
                <p className="font-pixel text-sm text-yellow-300">Reddit API Not Configured</p>
                <p className="text-xs text-gray-300 mt-1">
                  Please configure your Reddit API credentials in Settings to use this feature.
                </p>
              </div>
              <PixelButton
                onClick={() => router.push('/settings')}
                variant="primary"
                size="sm"
              >
                Go to Settings
              </PixelButton>
            </div>
          </div>
        )}

        {/* Search Form */}
        <PixelCard className="mb-8">
          <div className="space-y-6">
            {/* Keyword Input */}
            <div>
              <label className="block text-sm font-pixel mb-2 text-gray-300">
                🔍 Search Keyword
              </label>
              <PixelInput
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., AI technology, cryptocurrency, programming..."
                className="w-full"
              />
            </div>

            {/* Subreddit */}
            <div>
              <label className="block text-sm font-pixel mb-2 text-gray-300">
                📍 Subreddit
              </label>
              <PixelInput
                type="text"
                value={subreddit}
                onChange={(e) => setSubreddit(e.target.value)}
                placeholder="all (for site-wide search) or specific subreddit name"
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                💡 Use "all" for site-wide search, or enter a specific subreddit name (e.g., "programming")
              </p>
            </div>

            {/* Search Parameters Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-pixel mb-2 text-gray-300">
                  📊 Max Results
                </label>
                <PixelInput
                  type="number"
                  value={limit}
                  onChange={(e) => setLimit(e.target.value)}
                  placeholder="100"
                  min="1"
                  max="500"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-pixel mb-2 text-gray-300">
                  💬 Min Comments
                </label>
                <PixelInput
                  type="number"
                  value={minComments}
                  onChange={(e) => setMinComments(e.target.value)}
                  placeholder="0"
                  min="0"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-pixel mb-2 text-gray-300">
                  👍 Min Score
                </label>
                <PixelInput
                  type="number"
                  value={minScore}
                  onChange={(e) => setMinScore(e.target.value)}
                  placeholder="0"
                  min="0"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-pixel mb-2 text-gray-300">
                  📅 Time Range
                </label>
                <PixelSelect
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="w-full"
                >
                  <option value="1">Last 1 year</option>
                  <option value="2">Last 2 years</option>
                  <option value="3">Last 3 years</option>
                  <option value="5">Last 5 years</option>
                  <option value="10">Last 10 years</option>
                </PixelSelect>
              </div>
            </div>

            {/* Info Box */}
            <div className="p-4 bg-blue-500/10 border-2 border-blue-500/30 rounded pixel-border">
              <p className="text-xs text-gray-300">
                <strong className="text-blue-400">ℹ️ Note:</strong> Promoted and sponsored posts are automatically filtered out.
                Search is performed site-wide by default, sorted by relevance.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <PixelButton
                onClick={handleSearch}
                loading={isSearching}
                icon={<Search className="w-4 h-4" />}
                className="flex-grow"
                size="lg"
                disabled={!apiConfigured}
              >
                Search Reddit
              </PixelButton>
              {results && results.total > 0 && (
                <PixelButton
                  onClick={handleExport}
                  loading={isExporting}
                  variant="success"
                  icon={<Download className="w-4 h-4" />}
                  size="lg"
                >
                  Export to Excel
                </PixelButton>
              )}
            </div>

            {/* Error Message */}
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
            <PixelLoading text="Searching Reddit..." />
          </div>
        )}

        {/* Results */}
        {results && results.total > 0 && (
          <div>
            {/* Stats Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <PixelCard hoverable={false}>
                <div className="flex items-center gap-3">
                  <MessageSquare className="w-8 h-8 text-primary" />
                  <div>
                    <p className="text-2xl font-pixel text-primary">{results.total}</p>
                    <p className="text-sm text-gray-400 font-body">Posts Found</p>
                  </div>
                </div>
              </PixelCard>

              <PixelCard hoverable={false}>
                <div className="flex items-center gap-3">
                  <Search className="w-8 h-8 text-secondary" />
                  <div>
                    <p className="text-2xl font-pixel text-secondary">{results.keyword}</p>
                    <p className="text-sm text-gray-400 font-body">Search Keyword</p>
                  </div>
                </div>
              </PixelCard>

              <PixelCard hoverable={false}>
                <div className="flex items-center gap-3">
                  <Calendar className="w-8 h-8 text-accent" />
                  <div>
                    <p className="text-2xl font-pixel text-accent">{results.filters.time_range_years}y</p>
                    <p className="text-sm text-gray-400 font-body">Time Range</p>
                  </div>
                </div>
              </PixelCard>
            </div>

            {/* Posts List */}
            <div className="space-y-4">
              <h2 className="font-pixel text-xl text-primary mb-4">Search Results</h2>

              {results.posts.map((post, index) => (
                <motion.div
                  key={post.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <PixelCard hoverable>
                    <div className="space-y-3">
                      {/* Post Header */}
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-grow min-w-0">
                          <a
                            href={post.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-pixel text-lg text-primary hover:text-secondary transition-colors line-clamp-2 block"
                          >
                            {post.title}
                          </a>
                          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              r/{post.subreddit}
                            </span>
                            <span>•</span>
                            <span>u/{post.author}</span>
                            <span>•</span>
                            <span>{timeAgo(post.created_time)}</span>
                            {post.over_18 && (
                              <>
                                <span>•</span>
                                <span className="text-red-400">NSFW</span>
                              </>
                            )}
                          </div>
                        </div>
                        <a
                          href={post.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:text-secondary transition-colors flex-shrink-0"
                        >
                          <ExternalLink className="w-5 h-5" />
                        </a>
                      </div>

                      {/* Post Content Preview */}
                      {post.is_text_post && post.post_content && (
                        <p className="text-sm text-gray-400 line-clamp-2 font-body">
                          {post.post_content}
                        </p>
                      )}

                      {/* Post Stats */}
                      <div className="flex items-center gap-6 pt-3 border-t-2 border-gray-700">
                        <div className="flex items-center gap-2">
                          <ThumbsUp className="w-4 h-4 text-secondary" />
                          <span className="font-pixel text-sm text-secondary">
                            {formatNumber(post.score)}
                          </span>
                          <span className="text-xs text-gray-500">
                            ({post.upvote_ratio}% upvoted)
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MessageSquare className="w-4 h-4 text-accent" />
                          <span className="font-pixel text-sm text-accent">
                            {formatNumber(post.num_comments)}
                          </span>
                        </div>
                        {post.num_awards > 0 && (
                          <div className="flex items-center gap-2">
                            <Award className="w-4 h-4 text-yellow-500" />
                            <span className="font-pixel text-sm text-yellow-500">
                              {post.num_awards}
                            </span>
                          </div>
                        )}
                        {post.link_flair_text && (
                          <span className="px-2 py-1 text-xs font-pixel bg-primary/20 text-primary rounded">
                            {post.link_flair_text}
                          </span>
                        )}
                        <div className="ml-auto text-xs text-gray-500">
                          {post.is_text_post ? '📝 Text' : post.is_video ? '🎥 Video' : '🔗 Link'}
                        </div>
                      </div>
                    </div>
                  </PixelCard>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
