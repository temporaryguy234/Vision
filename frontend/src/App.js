import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Upload, 
  Folder, 
  Edit, 
  Download, 
  Palette,
  Search,
  User,
  Globe,
  Settings
} from 'lucide-react';

import { apiService } from './services/api';
import LottieRenderer from './components/editor/LottieRenderer';

// Import pages
import LibraryPage from './pages/LibraryPage';
import UploadPage from './pages/UploadPage';
import EditorPage from './pages/EditorPage';
import ExplorePage from './pages/ExplorePage';
import MyProjectsPage from './pages/MyProjectsPage';
import ExportsPage from './pages/ExportsPage';
import BrandKitsPage from './pages/BrandKitsPage';

// Navigation Component
const Sidebar = () => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Explore', href: '/', icon: Home },
    { name: 'Library', href: '/library', icon: Folder },
    { name: 'Upload', href: '/upload', icon: Upload },
    { name: 'My Projects', href: '/projects', icon: Edit },
    { name: 'Exports', href: '/exports', icon: Download },
    { name: 'Brand Kits', href: '/brand-kits', icon: Palette },
  ];

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="flex items-center px-6 py-4 border-b border-gray-200">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
            <Edit className="w-5 h-5 text-white" />
          </div>
          <span className="ml-3 text-xl font-bold text-gray-900">MotionEdit</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="mt-6 px-3">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-orange-50 text-orange-700 border-r-2 border-orange-500'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <item.icon
                  className={`mr-3 h-5 w-5 ${
                    isActive ? 'text-orange-500' : 'text-gray-400 group-hover:text-gray-500'
                  }`}
                />
                {item.name}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Bottom section */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-gray-600" />
            </div>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-900">Demo User</p>
            <p className="text-xs text-gray-500">demo@example.com</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Top Bar Component
const TopBar = () => {
  return (
    <div className="fixed top-0 left-64 right-0 z-40 bg-white border-b border-gray-200 h-16">
      <div className="flex items-center justify-between h-full px-6">
        {/* Search */}
        <div className="flex-1 max-w-lg">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search templates..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
            <Globe className="w-5 h-5" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

// Main Layout Component
const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <TopBar />
      <main className="pl-64 pt-16">
        {children}
      </main>
    </div>
  );
};

// Home/Explore Page - Matching expected design
const HomePage = () => {
  const [featuredTemplates, setFeaturedTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const templatesData = await apiService.get('/templates?limit=6');
        setFeaturedTemplates(templatesData.slice(0, 6));
      } catch (error) {
        console.error('Error fetching templates:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  const stats = [
    { icon: User, value: '10K+', label: 'Active Creators', color: 'text-orange-600' },
    { icon: Folder, value: '500+', label: 'Templates', color: 'text-blue-600' },
    { icon: Globe, value: '95%', label: 'Time Saved', color: 'text-green-600' },
    { icon: Settings, value: '2 Min', label: 'Avg. Edit Time', color: 'text-purple-600' },
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
              to="/library"
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 transform hover:scale-105"
            >
              Browse Templates
              <span className="ml-2">→</span>
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
            {loading ? (
              // Loading skeletons
              Array.from({ length: 6 }).map((_, index) => (
                <div key={index} className="bg-white rounded-2xl shadow-lg overflow-hidden animate-pulse">
                  <div className="aspect-video bg-gray-200"></div>
                  <div className="p-6">
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-6 bg-gray-200 rounded mb-3"></div>
                    <div className="flex gap-2">
                      <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                      <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                      <div className="h-6 bg-gray-200 rounded-full w-18"></div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              featuredTemplates.map((template) => (
                <Link
                  key={template.id}
                  to={`/t/${template.id}`}
                  className="group bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden hover:scale-105"
                >
                  <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
                    {template.preview_image_url ? (
                      <img
                        src={template.preview_image_url}
                        alt={template.title}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                      />
                    ) : template.file_url ? (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <LottieRenderer
                          sourceUrl={template.file_url}
                          isPlaying={true}
                          autoplay={true}
                          loop={true}
                          speed={1.0}
                          className="w-full h-full"
                        />
                      </div>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <div className="w-24 h-24 bg-orange-200 rounded-lg flex items-center justify-center">
                          <span className="text-2xl">🎬</span>
                        </div>
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  </div>
                  <div className="p-6">
                    <div className="text-sm text-orange-600 font-medium mb-2">{template.category}</div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">{template.title}</h3>
                    <div className="flex flex-wrap gap-2">
                      {template.tags && template.tags.length > 0 ? (
                        template.tags.slice(0, 3).map((tag, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full"
                          >
                            {tag}
                          </span>
                        ))
                      ) : (
                        <span className="px-3 py-1 bg-orange-100 text-orange-600 text-sm rounded-full">
                          Lottie
                        </span>
                      )}
                    </div>
                  </div>
                </Link>
              ))
            )}
          </div>

          <div className="text-center mt-12">
            <Link
              to="/library"
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-colors"
            >
              View All Templates
              <span className="ml-2">→</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Template Editor Route */}
          <Route path="/t/:templateId" element={<EditorPage />} />
          
          {/* Main App Routes with Layout */}
          <Route path="/*" element={
            <Layout>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/library" element={<LibraryPage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/projects" element={<MyProjectsPage />} />
                <Route path="/exports" element={<ExportsPage />} />
                <Route path="/brand-kits" element={<BrandKitsPage />} />
                <Route path="/explore" element={<ExplorePage />} />
              </Routes>
            </Layout>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;