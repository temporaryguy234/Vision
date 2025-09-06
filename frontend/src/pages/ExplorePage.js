import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Users, FileText, Clock, Target } from 'lucide-react';

const ExplorePage = () => {
  const stats = [
    { icon: Users, value: '10K+', label: 'Active Creators', color: 'text-orange-600' },
    { icon: FileText, value: '500+', label: 'Templates', color: 'text-blue-600' },
    { icon: Clock, value: '95%', label: 'Time Saved', color: 'text-green-600' },
    { icon: Target, value: '2 Min', label: 'Avg. Edit Time', color: 'text-purple-600' },
  ];

  const featuredTemplates = [
    {
      id: 1,
      title: 'Social Media Intro',
      category: 'Intros & Outros',
      preview: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=300&h=200&fit=crop',
      tags: ['Instagram', 'TikTok', 'Modern']
    },
    {
      id: 2,
      title: 'Data Visualization',
      category: 'Charts & Maps',
      preview: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=200&fit=crop',
      tags: ['Charts', 'Analytics', 'Business']
    },
    {
      id: 3,
      title: 'Logo Animation',
      category: 'Animated Icons',
      preview: 'https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=300&h=200&fit=crop',
      tags: ['Logo', 'Branding', 'Professional']
    },
    {
      id: 4,
      title: 'Quote Typography',
      category: 'Titles & Quotes',
      preview: 'https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=300&h=200&fit=crop',
      tags: ['Typography', 'Motivational', 'Social']
    },
    {
      id: 5,
      title: 'Product Showcase',
      category: 'Ads & Promos',
      preview: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=200&fit=crop',
      tags: ['Product', 'Marketing', 'E-commerce']
    },
    {
      id: 6,
      title: 'World Map Visualization',
      category: 'Charts & Maps',
      preview: 'https://images.unsplash.com/photo-1597149961283-62c2e52b98d6?w=300&h=200&fit=crop',
      tags: ['Maps', 'Global', 'Data']
    }
  ];

  return (
    <div className="min-h-full">
      {/* Hero Section */}
      <section className="px-8 py-8">
        <div className="max-w-7xl mx-auto text-center">
          {/* New Badge */}
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20 mb-6">
            <span className="w-2 h-2 bg-orange-500 rounded-full mr-2 animate-pulse"></span>
            <span className="text-sm font-medium text-orange-600">New: Natural Language Editing</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-5">
            Your Motion Graphics
            <br />
            <span className="bg-gradient-to-r from-orange-500 to-red-500 bg-clip-text text-transparent">
              Template Library
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-lg text-gray-600 mb-6 max-w-3xl mx-auto leading-relaxed">
            Browse and customize professional templates for YouTube, TikTok, and
            Instagram in minutes. No design experience required.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
            <Link
              to="/templates"
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 transform hover:scale-105"
            >
              Browse Templates
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <button className="inline-flex items-center px-8 py-4 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-colors">
              Watch Demo
            </button>
          </div>
        </div>
      </section>

      {/* Stats Section - Compact */}
      <section className="px-8 py-8 bg-white/30 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={index} className="text-center">
                  <div className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-gray-50 to-white rounded-xl shadow-md mb-2">
                    <Icon className={`w-5 h-5 ${stat.color}`} />
                  </div>
                  <div className="text-xl font-bold text-gray-900 mb-1">{stat.value}</div>
                  <div className="text-sm text-gray-600">{stat.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Featured Templates Section */}
      <section className="px-8 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Featured Templates</h2>
            <p className="text-gray-600">Handpicked templates to get you started</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredTemplates.map((template) => (
              <Link
                key={template.id}
                to={`/editor/${template.id}`}
                className="group bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden hover:scale-105"
              >
                <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
                  <img
                    src={template.preview}
                    alt={template.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
                <div className="p-6">
                  <div className="text-sm text-orange-600 font-medium mb-2">{template.category}</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">{template.title}</h3>
                  <div className="flex flex-wrap gap-2">
                    {template.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </Link>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link
              to="/templates"
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-colors"
            >
              View All Templates
              <ArrowRight className="ml-2 w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ExplorePage;