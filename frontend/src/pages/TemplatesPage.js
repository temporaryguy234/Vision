import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, Grid, List } from 'lucide-react';
import { apiService } from '../services/api';
import LottieRenderer from '../components/editor/LottieRenderer';

const TemplatesPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [viewMode, setViewMode] = useState('grid');
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

  const categories = [
    'All',
    'Intros & Outros',
    'Lower Thirds',
    'Titles & Quotes',
    'Charts & Maps',
    'Social Media Posts',
    'Ads & Promos',
    'Overlays',
    'Animated Icons',
    'Miscellaneous'
  ];

  useEffect(() => {
    const fetchTemplates = async () => {
      setLoading(true);
      try {
        const params = {};
        if (selectedCategory !== 'All') {
          params.category = selectedCategory;
        }
        if (searchQuery) {
          params.search = searchQuery;
        }
        
        const templatesData = await apiService.getTemplates(params);
        setTemplates(templatesData);
      } catch (error) {
        console.error('Error fetching templates:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, [selectedCategory, searchQuery]);

  const filteredTemplates = templates;

  const TemplateCard = ({ template }) => {
    const [hovered, setHovered] = useState(false);
    const videoRef = useRef(null);

    useEffect(() => {
      const v = videoRef.current;
      if (!v) return;
      try {
        if (hovered) {
          v.play().catch(() => {});
        } else {
          v.pause();
          v.currentTime = 0;
        }
      } catch (_) {}
    }, [hovered]);

    return (
      <Link
        key={template.id}
        to={`/t/${template.id}`}
        className="group bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden hover:scale-105 template-card"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
          {/* Base thumbnail image */}
          {template.preview_image_url || template.preview_url ? (
            <img
              src={template.preview_image_url || template.preview_url}
              alt={template.title}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
              onError={(e) => { e.currentTarget.style.display = 'none'; }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-500">No preview</div>
          )}

          {/* Hover animated preview: prefer video if available */}
          {template.preview_video_url ? (
            <video
              ref={videoRef}
              src={template.preview_video_url}
              className="absolute inset-0 w-full h-full object-cover opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              muted
              loop
              playsInline
              preload="metadata"
            />
          ) : template.file_url ? (
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none flex items-center justify-center">
              <LottieRenderer
                sourceUrl={template.file_url}
                isPlaying={hovered}
                autoplay={false}
                loop={true}
                speed={1.0}
                className="w-full h-full"
              />
            </div>
          ) : null}

          <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="absolute bottom-4 left-4 text-white">
              {template.duration && (
                <span className="text-sm font-medium">{template.duration}</span>
              )}
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-orange-600 font-medium">{template.category}</span>
            {template.is_public && (
              <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full">Public</span>
            )}
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">{template.title}</h3>
          {Array.isArray(template.tags) && template.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {template.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                >
                  {tag}
                </span>
              ))}
              {template.tags.length > 3 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                  +{template.tags.length - 3}
                </span>
              )}
            </div>
          )}
        </div>
      </Link>
    );
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Templates</h1>
          <p className="text-gray-600">Choose from our collection of professional motion graphics templates</p>
        </div>

        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
            />
          </div>

          {/* Categories and View Toggle */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            {/* Category Pills */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    selectedCategory === category
                      ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>

            {/* View Toggle */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-orange-100 text-orange-600' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-orange-100 text-orange-600' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Templates Grid */}
        <div className={`grid gap-6 ${
          viewMode === 'grid' 
            ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
            : 'grid-cols-1'
        }`}>
          {loading ? (
            // Loading skeletons
            Array.from({ length: 8 }).map((_, index) => (
              <div key={index} className="bg-white rounded-2xl shadow-lg overflow-hidden animate-pulse">
                <div className="aspect-video bg-gray-200"></div>
                <div className="p-6">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-6 bg-gray-200 rounded mb-3"></div>
                  <div className="flex gap-2">
                    <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                    <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            filteredTemplates.map((template) => (
              <TemplateCard key={template.id} template={template} />
            ))
          )}
        </div>

        {/* Results Info */}
        <div className="mt-8 text-center">
          <p className="text-gray-600">
            {loading ? 'Loading templates...' : `Showing ${filteredTemplates.length} templates`}
          </p>
        </div>
      </div>
    </div>
  );
};

export default TemplatesPage;