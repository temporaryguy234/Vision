import React, { useState, useEffect } from 'react';
import { Search, Download, Play, Eye, Star, Filter } from 'lucide-react';
import { apiService } from '../services/api';

const LottieFilesBrowser = ({ onImport }) => {
  const [animations, setAnimations] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [importing, setImporting] = useState({});

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [animationsData, categoriesData] = await Promise.all([
        apiService.searchLottieFilesAnimations(),
        apiService.getLottieFilesCategories()
      ]);
      
      setAnimations(animationsData.results || []);
      setCategories(categoriesData || []);
    } catch (error) {
      console.error('Failed to load LottieFiles data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      setLoading(true);
      const results = await apiService.searchLottieFilesAnimations({
        query: searchQuery,
        category: selectedCategory
      });
      setAnimations(results.results || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImportAnimation = async (animationId) => {
    try {
      setImporting(prev => ({ ...prev, [animationId]: true }));
      
      const result = await apiService.importLottieFilesAnimation(animationId);
      
      if (onImport) {
        onImport(result);
      }
      
      // Show success message
      alert(`Successfully imported "${result.template_title}"!`);
      
    } catch (error) {
      console.error('Import failed:', error);
      alert('Import failed. Please try again.');
    } finally {
      setImporting(prev => ({ ...prev, [animationId]: false }));
    }
  };

  const formatDuration = (duration) => {
    if (!duration) return 'N/A';
    return `${duration.toFixed(1)}s`;
  };

  if (loading && animations.length === 0) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading animations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">LottieFiles Library</h2>
          <p className="text-gray-600">Browse and import high-quality Lottie animations</p>
        </div>
        <div className="flex items-center space-x-2">
          <Star className="w-5 h-5 text-yellow-500" />
          <span className="text-sm text-gray-600">Curated Collection</span>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search animations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
            />
          </div>
          
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="pl-10 pr-8 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300 bg-white"
            >
              <option value="">All Categories</option>
              {categories.map((category) => (
                <option key={category.slug} value={category.slug}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
          
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => {
            setSelectedCategory('');
            handleSearch();
          }}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            selectedCategory === '' 
              ? 'bg-orange-500 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All
        </button>
        {categories.slice(0, 6).map((category) => (
          <button
            key={category.slug}
            onClick={() => {
              setSelectedCategory(category.slug);
              setTimeout(handleSearch, 100);
            }}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === category.slug
                ? 'bg-orange-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {category.name}
          </button>
        ))}
      </div>

      {/* Animations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {animations.map((animation) => (
          <div key={animation.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
            {/* Animation Preview */}
            <div className="relative aspect-square bg-gray-50 flex items-center justify-center group">
              {animation.thumbnail_url ? (
                <img
                  src={animation.thumbnail_url}
                  alt={animation.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              
              <div className="w-full h-full bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center">
                <Play className="w-12 h-12 text-orange-500" />
              </div>
              
              {/* Overlay */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex space-x-2">
                  <button className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors">
                    <Eye className="w-4 h-4 text-gray-700" />
                  </button>
                  <button className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors">
                    <Play className="w-4 h-4 text-gray-700" />
                  </button>
                </div>
              </div>
            </div>

            {/* Animation Info */}
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 mb-1 truncate">{animation.name}</h3>
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">{animation.description}</p>
              
              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {animation.tags.slice(0, 3).map((tag, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Meta Info */}
              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                <span className="capitalize">{animation.category}</span>
                <span>{formatDuration(animation.duration)}</span>
              </div>

              {/* Import Button */}
              <button
                onClick={() => handleImportAnimation(animation.id)}
                disabled={importing[animation.id]}
                className="w-full flex items-center justify-center px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white text-sm font-medium rounded-lg hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {importing[animation.id] ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                    Importing...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Import Animation
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {animations.length === 0 && !loading && (
        <div className="text-center py-12">
          <Play className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No animations found</h3>
          <p className="text-gray-600 mb-4">Try adjusting your search or category filter</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('');
              loadInitialData();
            }}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
          >
            Show All Animations
          </button>
        </div>
      )}
    </div>
  );
};

export default LottieFilesBrowser;