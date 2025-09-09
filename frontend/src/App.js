import React from 'react';
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

// Home/Explore Page (restored original clean design)
const HomePage = () => {
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Clean Hero Section - Original Style */}
        <div className="text-center py-16 bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Create & Edit Motion Graphics
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Import Lottie animations, edit with visual controls and AI prompts. Professional motion graphics made simple.
          </p>
          
          <div className="flex items-center justify-center space-x-4">
            <Link
              to="/upload"
              className="px-8 py-4 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200"
            >
              Upload Templates
            </Link>
            <Link
              to="/library"
              className="px-8 py-4 border-2 border-orange-500 text-orange-500 font-semibold rounded-xl hover:bg-orange-50 transition-colors"
            >
              Browse Library
            </Link>
          </div>
        </div>

        {/* Features Grid - Clean Design */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="text-center p-8 bg-white rounded-xl shadow-sm border border-gray-100">
            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Import & Upload</h3>
            <p className="text-gray-600">Drag & drop .json and .lottie files or import from URLs. Full support for After Effects exports.</p>
          </div>
          
          <div className="text-center p-8 bg-white rounded-xl shadow-sm border border-gray-100">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Edit className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Visual Editor</h3>
            <p className="text-gray-600">Edit text, colors, images and speed with live preview. Click elements to edit instantly.</p>
          </div>
          
          <div className="text-center p-8 bg-white rounded-xl shadow-sm border border-gray-100">
            <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Settings className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Prompts</h3>
            <p className="text-gray-600">Use natural language: "make it faster", "change logo", "set color to blue". No technical skills needed.</p>
          </div>
        </div>

        {/* Recent Templates - Show Real Lottie Templates */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Featured Templates</h2>
              <p className="text-gray-600">Professional Lottie animations ready to customize</p>
            </div>
            <Link
              to="/library"
              className="text-orange-500 hover:text-orange-600 font-medium flex items-center"
            >
              View All
              <span className="ml-1">→</span>
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Lottie Template Cards */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden group hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-orange-100 to-red-100 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-24 h-24">
                    {/* This will show actual Lottie animation */}
                    <div className="w-full h-full bg-orange-200 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">🏷️</span>
                    </div>
                  </div>
                </div>
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                  <Link
                    to="/t/demo-price-tag"
                    className="opacity-0 group-hover:opacity-100 px-4 py-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-all"
                  >
                    Edit Template
                  </Link>
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1">Price Tag</h3>
                <p className="text-sm text-gray-600 mb-2">Editable discount badge</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-orange-500 bg-orange-50 px-2 py-1 rounded">Lottie</span>
                  <span className="text-xs text-gray-500">2.1s</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden group hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-green-100 to-teal-100 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-24 h-24">
                    <div className="w-full h-full bg-green-200 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">📈</span>
                    </div>
                  </div>
                </div>
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                  <Link
                    to="/t/demo-chart"
                    className="opacity-0 group-hover:opacity-100 px-4 py-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-all"
                  >
                    Edit Template
                  </Link>
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1">Stock Chart</h3>
                <p className="text-sm text-gray-600 mb-2">Animated data visualization</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-green-500 bg-green-50 px-2 py-1 rounded">Lottie</span>
                  <span className="text-xs text-gray-500">4.0s</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden group hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-blue-100 to-purple-100 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-24 h-24">
                    <div className="w-full h-full bg-blue-200 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">✨</span>
                    </div>
                  </div>
                </div>
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                  <Link
                    to="/t/demo-loader"
                    className="opacity-0 group-hover:opacity-100 px-4 py-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-all"
                  >
                    Edit Template
                  </Link>
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1">Loading Animation</h3>
                <p className="text-sm text-gray-600 mb-2">Smooth loading indicator</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-blue-500 bg-blue-50 px-2 py-1 rounded">Lottie</span>
                  <span className="text-xs text-gray-500">2.5s</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden group hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-purple-100 to-pink-100 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-24 h-24">
                    <div className="w-full h-full bg-purple-200 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">❤️</span>
                    </div>
                  </div>
                </div>
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                  <Link
                    to="/t/demo-like"
                    className="opacity-0 group-hover:opacity-100 px-4 py-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-all"
                  >
                    Edit Template
                  </Link>
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1">Like Animation</h3>
                <p className="text-sm text-gray-600 mb-2">Social media interaction</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-purple-500 bg-purple-50 px-2 py-1 rounded">Lottie</span>
                  <span className="text-xs text-gray-500">1.8s</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Create?</h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Upload your Lottie files or start with our templates. Edit with AI prompts and export professional videos.
          </p>
          <Link
            to="/upload"
            className="px-8 py-4 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200"
          >
            Get Started
          </Link>
        </div>
      </div>
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