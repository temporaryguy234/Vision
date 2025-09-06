import React, { useState } from 'react';
import { Plus, Palette, Type, Edit, Trash2, Copy, Download } from 'lucide-react';

const BrandKitsPage = () => {
  const [activeKit, setActiveKit] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const brandKits = [
    {
      id: 1,
      name: 'Corporate Blue',
      description: 'Professional and trustworthy brand colors',
      colors: ['#1E40AF', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE'],
      fonts: ['Inter', 'Roboto'],
      createdAt: '2024-01-15'
    },
    {
      id: 2,
      name: 'Sunset Gradient',
      description: 'Warm and energetic brand palette',
      colors: ['#EA580C', '#F97316', '#FB923C', '#FDBA74', '#FED7AA'],
      fonts: ['Poppins', 'Open Sans'],
      createdAt: '2024-01-14'
    },
    {
      id: 3,
      name: 'Nature Green',
      description: 'Fresh and organic color scheme',
      colors: ['#059669', '#10B981', '#34D399', '#6EE7B7', '#A7F3D0'],
      fonts: ['Nunito', 'Lato'],
      createdAt: '2024-01-12'
    },
    {
      id: 4,
      name: 'Royal Purple',
      description: 'Elegant and premium brand colors',
      colors: ['#7C3AED', '#8B5CF6', '#A78BFA', '#C4B5FD', '#DDD6FE'],
      fonts: ['Montserrat', 'Source Sans Pro'],
      createdAt: '2024-01-10'
    }
  ];

  const popularFonts = [
    'Inter', 'Roboto', 'Poppins', 'Open Sans', 'Nunito', 'Lato', 
    'Montserrat', 'Source Sans Pro', 'Ubuntu', 'Playfair Display'
  ];

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Brand Kits</h1>
            <p className="text-gray-600">Create and manage your brand color palettes and typography presets</p>
          </div>
          
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 mt-4 md:mt-0"
          >
            <Plus className="w-5 h-5 mr-2" />
            New Brand Kit
          </button>
        </div>

        {/* Brand Kits Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {brandKits.map((kit) => (
            <div
              key={kit.id}
              className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer"
              onClick={() => setActiveKit(kit)}
            >
              {/* Color Palette Preview */}
              <div className="h-24 flex">
                {kit.colors.map((color, index) => (
                  <div
                    key={index}
                    className="flex-1 transition-all duration-300 group-hover:scale-110"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
              
              {/* Content */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{kit.name}</h3>
                    <p className="text-sm text-gray-600">{kit.description}</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <span>{kit.colors.length} colors</span>
                  <span>{kit.fonts.length} fonts</span>
                  <span>{kit.createdAt}</span>
                </div>
                
                {/* Font Preview */}
                <div className="border-t border-gray-100 pt-4">
                  <div className="text-xs text-gray-500 mb-2">Typography</div>
                  <div className="space-y-1">
                    {kit.fonts.slice(0, 2).map((font, index) => (
                      <div
                        key={index}
                        className="text-sm"
                        style={{ fontFamily: font }}
                      >
                        {font}
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Actions */}
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                      <Copy className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <button className="text-sm text-orange-600 hover:text-orange-700 font-medium">
                    Apply to Project
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Color Palette Generator */}
        <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Palette Generator</h3>
              <p className="text-gray-600">Generate color palettes from trending color combinations</p>
            </div>
            <Palette className="w-8 h-8 text-orange-600" />
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Trending Palettes */}
            <div className="bg-white rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="h-8 flex rounded mb-3">
                <div className="flex-1 bg-blue-500"></div>
                <div className="flex-1 bg-blue-400"></div>
                <div className="flex-1 bg-blue-300"></div>
                <div className="flex-1 bg-blue-200"></div>
              </div>
              <div className="text-sm font-medium text-gray-900">Ocean Blues</div>
            </div>
            
            <div className="bg-white rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="h-8 flex rounded mb-3">
                <div className="flex-1 bg-pink-500"></div>
                <div className="flex-1 bg-pink-400"></div>
                <div className="flex-1 bg-pink-300"></div>
                <div className="flex-1 bg-pink-200"></div>
              </div>
              <div className="text-sm font-medium text-gray-900">Pink Dreams</div>
            </div>
            
            <div className="bg-white rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="h-8 flex rounded mb-3">
                <div className="flex-1 bg-yellow-500"></div>
                <div className="flex-1 bg-orange-500"></div>
                <div className="flex-1 bg-red-500"></div>
                <div className="flex-1 bg-red-400"></div>
              </div>
              <div className="text-sm font-medium text-gray-900">Sunset Fire</div>
            </div>
            
            <div className="bg-white rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="h-8 flex rounded mb-3">
                <div className="flex-1 bg-gray-800"></div>
                <div className="flex-1 bg-gray-600"></div>
                <div className="flex-1 bg-gray-400"></div>
                <div className="flex-1 bg-gray-200"></div>
              </div>
              <div className="text-sm font-medium text-gray-900">Monochrome</div>
            </div>
          </div>
        </div>

        {/* Popular Fonts Section */}
        <div className="mt-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Popular Typography</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {popularFonts.map((font, index) => (
              <div
                key={index}
                className="bg-white rounded-lg p-4 shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 hover:border-orange-300"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-lg font-medium text-gray-900" style={{ fontFamily: font }}>
                      {font}
                    </div>
                    <div className="text-sm text-gray-600 mt-1" style={{ fontFamily: font }}>
                      The quick brown fox jumps
                    </div>
                  </div>
                  <button className="p-2 text-gray-600 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors">
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Create Modal (simplified) */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Create New Brand Kit</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Kit Name</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                  placeholder="My Brand Kit"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                  rows={3}
                  placeholder="Describe your brand style..."
                />
              </div>
            </div>
            <div className="flex items-center justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                Cancel
              </button>
              <button className="px-6 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:shadow-lg transition-all">
                Create Kit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BrandKitsPage;