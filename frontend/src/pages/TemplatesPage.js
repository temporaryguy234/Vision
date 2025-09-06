import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, Grid, List } from 'lucide-react';

const TemplatesPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [viewMode, setViewMode] = useState('grid');

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

  const templates = [
    {
      id: 1,
      title: 'Modern Social Intro',
      category: 'Intros & Outros',
      preview: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop',
      tags: ['Instagram', 'TikTok', 'Modern', 'Trendy'],
      duration: '5s',
      isPublic: true
    },
    {
      id: 2,
      title: 'Data Chart Animation',
      category: 'Charts & Maps',
      preview: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop',
      tags: ['Charts', 'Analytics', 'Business', 'Professional'],
      duration: '8s',
      isPublic: true
    },
    {
      id: 3,
      title: 'Logo Reveal',
      category: 'Animated Icons',
      preview: 'https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=400&h=300&fit=crop',
      tags: ['Logo', 'Branding', 'Corporate', 'Clean'],
      duration: '3s',
      isPublic: true
    },
    {
      id: 4,
      title: 'Inspirational Quote',
      category: 'Titles & Quotes',
      preview: 'https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=400&h=300&fit=crop',
      tags: ['Typography', 'Motivational', 'Social', 'Elegant'],
      duration: '6s',
      isPublic: true
    },
    {
      id: 5,
      title: 'Product Showcase',
      category: 'Ads & Promos',
      preview: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400&h=300&fit=crop',
      tags: ['Product', 'Marketing', 'E-commerce', 'Sales'],
      duration: '10s',
      isPublic: true
    },
    {
      id: 6,
      title: 'World Map Data',
      category: 'Charts & Maps',
      preview: 'https://images.unsplash.com/photo-1597149961283-62c2e52b98d6?w=400&h=300&fit=crop',
      tags: ['Maps', 'Global', 'Data', 'Infographic'],
      duration: '7s',
      isPublic: true
    },
    {
      id: 7,
      title: 'Lower Third News',
      category: 'Lower Thirds',
      preview: 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=300&fit=crop',
      tags: ['News', 'Professional', 'Broadcast', 'Clean'],
      duration: '4s',
      isPublic: true
    },
    {
      id: 8,
      title: 'Social Media Story',
      category: 'Social Media Posts',
      preview: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=300&fit=crop',
      tags: ['Stories', 'Instagram', 'Mobile', 'Vertical'],
      duration: '15s',
      isPublic: true
    }
  ];

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === 'All' || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

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
          {filteredTemplates.map((template) => (
            <Link
              key={template.id}
              to={`/editor/${template.id}`}
              className="group bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden hover:scale-105 template-card"
            >
              <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
                <img
                  src={template.preview}
                  alt={template.title}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="absolute bottom-4 left-4 text-white">
                    <span className="text-sm font-medium">{template.duration}</span>
                  </div>
                </div>
              </div>
              <div className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-orange-600 font-medium">{template.category}</span>
                  {template.isPublic && (
                    <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full">Public</span>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">{template.title}</h3>
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
              </div>
            </Link>
          ))}
        </div>

        {/* Results Info */}
        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Showing {filteredTemplates.length} of {templates.length} templates
          </p>
        </div>
      </div>
    </div>
  );
};

export default TemplatesPage;