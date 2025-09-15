import React, { useState, useEffect, useRef } from 'react';
import { Search, Filter, Play, Edit, Download } from 'lucide-react';
import { apiService } from '../services/api';

const LibraryPage = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [hoveredId, setHoveredId] = useState(null);

  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'Intros & Outros', label: 'Intros & Outros' },
    { value: 'Lower Thirds', label: 'Lower Thirds' },
    { value: 'Titles & Quotes', label: 'Titles & Quotes' },
    { value: 'Charts & Maps', label: 'Charts & Maps' },
    { value: 'Social Media Posts', label: 'Social Media Posts' },
    { value: 'Ads & Promos', label: 'Ads & Promos' },
    { value: 'Overlays', label: 'Overlays' },
    { value: 'Animated Icons', label: 'Animated Icons' },
    { value: 'Miscellaneous', label: 'Miscellaneous' }
  ];

  useEffect(() => {
    loadTemplates();
  }, [selectedCategory, searchTerm]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await apiService.get(`/templates?${params.toString()}`);
      setTemplates(response);
      
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadTemplates();
  };

  // Lightweight hover animation renderer using lottie-web
  const HoverAnimation = ({ fileUrl, show }) => {
    const containerRef = useRef(null);
    const animRef = useRef(null);
    useEffect(() => {
      const backendBase = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      async function load() {
        if (!show || !containerRef.current) return;
        try {
          let data;
          if (fileUrl?.startsWith('/uploads/')) {
            const filePath = fileUrl.replace('/uploads/', '');
            const resp = await fetch(`${backendBase}/api/lottie/${filePath}`);
            if (!resp.ok) throw new Error('Failed to load lottie');
            data = await resp.json();
          } else if (fileUrl) {
            const resp = await fetch(`${backendBase}/api/lottie/resolve?url=${encodeURIComponent(fileUrl)}`);
            if (!resp.ok) throw new Error('Failed to resolve lottie');
            data = await resp.json();
          } else {
            return;
          }
          const lottieWeb = await import('lottie-web');
          if (animRef.current) {
            animRef.current.destroy();
            animRef.current = null;
          }
          animRef.current = lottieWeb.loadAnimation({
            container: containerRef.current,
            renderer: 'canvas',
            loop: true,
            autoplay: true,
            animationData: data
          });
        } catch (e) {
          // swallow hover preview errors
        }
      }
      load();
      return () => {
        if (animRef.current) {
          animRef.current.destroy();
          animRef.current = null;
        }
      };
    }, [fileUrl, show]);
    return (
      <div
        ref={containerRef}
        className="absolute inset-0 hidden group-hover:block"
        aria-hidden
      />
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Template Library</h1>
          <p className="text-gray-600">Browse and edit motion graphics templates</p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
            
            {/* Search Input */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
              />
            </div>
            
            {/* Category Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="pl-10 pr-8 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300 bg-white min-w-48"
              >
                {categories.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Search Button */}
            <button
              type="submit"
              className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200"
            >
              Search
            </button>
          </form>
        </div>

        {/* Templates Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="aspect-video bg-gray-200 animate-pulse"></div>
                <div className="p-4">
                  <div className="h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-2/3"></div>
                </div>
              </div>
            ))}
          </div>
        ) : templates.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📱</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No templates found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your search or category filter</p>
            <a
              href="/upload"
              className="inline-flex items-center px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
            >
              Upload Templates
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {templates.map((template) => (
              <div key={template.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
                
                {/* Preview */}
                <div className="aspect-video bg-gradient-to-br from-orange-100 to-red-100 relative group"
                     onMouseEnter={() => setHoveredId(template.id)}
                     onMouseLeave={() => setHoveredId(null)}>
                  {template.preview_url ? (
                    <img
                      src={template.preview_url}
                      alt={template.title || template.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Play className="w-12 h-12 text-orange-500" />
                    </div>
                  )}

                  {/* Hover playback overlay */}
                  <HoverAnimation fileUrl={template.file_url} show={hoveredId === template.id} />
                  
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <a
                        href={`/t/${template.id}`}
                        className="inline-flex items-center px-4 py-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Edit Template
                      </a>
                    </div>
                  </div>
                </div>
                
                {/* Info */}
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 mb-1 truncate">
                    {template.title || template.name}
                  </h3>
                  
                  {template.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {template.description}
                    </p>
                  )}
                  
                  {/* Tags */}
                  {template.tags && template.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {template.tags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  {/* Category */}
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500 capitalize">
                      {template.category || 'Miscellaneous'}
                    </span>
                    
                    <div className="flex items-center space-x-2">
                      <a
                        href={`/t/${template.id}`}
                        className="p-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                        title="Edit Template"
                      >
                        <Edit className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
      </div>
    </div>
  );
};

export default LibraryPage;