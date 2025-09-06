import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Calendar, Clock, MoreVertical, Trash2, Edit, Copy } from 'lucide-react';

const MyProjectsPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('recent');

  const projects = [
    {
      id: 1,
      title: 'Summer Campaign Video',
      template: 'Social Media Intro',
      thumbnail: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=300&h=200&fit=crop',
      lastModified: '2 hours ago',
      created: '2024-01-15',
      duration: '15s',
      status: 'Draft'
    },
    {
      id: 2,
      title: 'Q4 Sales Report',
      template: 'Data Visualization',
      thumbnail: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=200&fit=crop',
      lastModified: '1 day ago',
      created: '2024-01-14',
      duration: '30s',
      status: 'Completed'
    },
    {
      id: 3,
      title: 'Brand Logo Animation',
      template: 'Logo Reveal',
      thumbnail: 'https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=300&h=200&fit=crop',
      lastModified: '3 days ago',
      created: '2024-01-12',
      duration: '8s',
      status: 'In Progress'
    },
    {
      id: 4,
      title: 'Product Launch Teaser',
      template: 'Product Showcase',
      thumbnail: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=200&fit=crop',
      lastModified: '1 week ago',
      created: '2024-01-08',
      duration: '12s',
      status: 'Completed'
    },
    {
      id: 5,
      title: 'Motivational Quote Card',
      template: 'Typography Animation',
      thumbnail: 'https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=300&h=200&fit=crop',
      lastModified: '2 weeks ago',
      created: '2024-01-01',
      duration: '6s',
      status: 'Draft'
    }
  ];

  const filteredProjects = projects.filter(project =>
    project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.template.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-600';
      case 'In Progress':
        return 'bg-blue-100 text-blue-600';
      case 'Draft':
        return 'bg-gray-100 text-gray-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">My Projects</h1>
            <p className="text-gray-600">Manage and organize your motion graphics projects</p>
          </div>
          
          <Link
            to="/templates"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 mt-4 md:mt-0"
          >
            <Plus className="w-5 h-5 mr-2" />
            New Project
          </Link>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
            />
          </div>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
          >
            <option value="recent">Most Recent</option>
            <option value="name">Name A-Z</option>
            <option value="created">Date Created</option>
            <option value="status">Status</option>
          </select>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group"
            >
              {/* Thumbnail */}
              <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
                <img
                  src={project.thumbnail}
                  alt={project.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="absolute bottom-4 left-4 text-white">
                    <span className="text-sm font-medium">{project.duration}</span>
                  </div>
                  <div className="absolute top-4 right-4">
                    <button className="p-2 bg-white/20 backdrop-blur-sm rounded-lg text-white hover:bg-white/30 transition-colors">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{project.title}</h3>
                    <p className="text-sm text-gray-600">{project.template}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                    {project.status}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {project.lastModified}
                  </div>
                  <div className="flex items-center">
                    <Calendar className="w-4 h-4 mr-1" />
                    {project.created}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between">
                  <Link
                    to={`/editor/${project.id}`}
                    className="flex items-center px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit
                  </Link>
                  
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                      <Copy className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredProjects.length === 0 && (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FolderOpen className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
            <p className="text-gray-600 mb-6">
              {searchQuery ? 'Try adjusting your search terms' : 'Create your first motion graphics project'}
            </p>
            <Link
              to="/templates"
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200"
            >
              <Plus className="w-5 h-5 mr-2" />
              Start New Project
            </Link>
          </div>
        )}

        {/* Stats */}
        <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">{projects.length}</div>
            <div className="text-gray-600">Total Projects</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-green-600 mb-1">
              {projects.filter(p => p.status === 'Completed').length}
            </div>
            <div className="text-gray-600">Completed</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {projects.filter(p => p.status === 'In Progress').length}
            </div>
            <div className="text-gray-600">In Progress</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-gray-600 mb-1">
              {projects.filter(p => p.status === 'Draft').length}
            </div>
            <div className="text-gray-600">Drafts</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyProjectsPage;