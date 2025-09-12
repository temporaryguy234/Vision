import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Users, FileText, Clock, Target, Play, Crown } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';
import LottieRenderer from '../components/editor/LottieRenderer';
import LoginModal from '../components/auth/LoginModal';
import RegisterModal from '../components/auth/RegisterModal';

const HomePage = () => {
  const [featuredTemplates, setFeaturedTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  
  const { user } = useAuth();

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
    { icon: Users, value: '10K+', label: 'Active Creators', color: 'text-orange-600' },
    { icon: FileText, value: '500+', label: 'Templates', color: 'text-blue-600' },
    { icon: Clock, value: '95%', label: 'Time Saved', color: 'text-green-600' },
    { icon: Target, value: '2 Min', label: 'Avg. Edit Time', color: 'text-purple-600' },
  ];

  return (
    <div className="min-h-full">
      {/* Hero Section */}
      <section className="px-8 py-8">
        <div className="max-w-7xl mx-auto text-center">
          {/* New Badge */}
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20 mb-6">
            <span className="w-2 h-2 bg-orange-500 rounded-full mr-2 animate-pulse"></span>
            <span className="text-sm font-medium text-orange-600">New: AI-Powered Natural Language Editing</span>
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
            Create stunning motion graphics for YouTube, TikTok, and Instagram in minutes. 
            Use natural language to edit animations - no design experience required.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
            {user ? (
              <Link
                to="/library"
                className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 transform hover:scale-105"
              >
                Browse Templates
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
            ) : (
              <button
                onClick={() => setShowRegister(true)}
                className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 transform hover:scale-105"
              >
                Get Started Free
                <ArrowRight className="ml-2 w-5 h-5" />
              </button>
            )}
            
            <button className="inline-flex items-center px-8 py-4 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-colors">
              <Play className="w-5 h-5 mr-2" />
              Watch Demo
            </button>
          </div>

          {/* User Status */}
          {user && (
            <div className="inline-flex items-center px-4 py-2 bg-white border border-gray-200 rounded-full shadow-sm">
              <Crown className="w-4 h-4 text-orange-500 mr-2" />
              <span className="text-sm font-medium text-gray-900">
                Welcome back, {user.full_name}! You have {user.credits_remaining} credits remaining.
              </span>
            </div>
          )}
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
              featuredTemplates.map((template) => {
                const [hovered, setHovered] = [false, () => {}];
                const videoRef = { current: null };
                return (
                  <Link
                    key={template.id}
                    to={user ? `/t/${template.id}` : '#'}
                    onClick={!user ? (e) => {
                      e.preventDefault();
                      setShowLogin(true);
                    } : undefined}
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
                      
                      {!user && (
                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <div className="bg-white text-gray-900 px-4 py-2 rounded-lg font-medium">
                            Sign in to edit
                          </div>
                        </div>
                      )}
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
                );
              })
            )}
          </div>

          <div className="text-center mt-12">
            <Link
              to="/library"
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-colors"
            >
              View All Templates
              <ArrowRight className="ml-2 w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      {!user && (
        <section className="px-8 py-12 bg-gradient-to-r from-gray-50 to-gray-100">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Simple, Transparent Pricing</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Free Plan */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <div className="text-center">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Free</h3>
                  <div className="text-3xl font-bold text-gray-900 mb-4">$0</div>
                  <ul className="text-sm text-gray-600 space-y-2 mb-6">
                    <li>5 exports per month</li>
                    <li>720p maximum</li>
                    <li>Watermark included</li>
                  </ul>
                  <button
                    onClick={() => setShowRegister(true)}
                    className="w-full py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Get Started
                  </button>
                </div>
              </div>

              {/* Mid Plan */}
              <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-blue-500 relative">
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </span>
                </div>
                <div className="text-center">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Creator</h3>
                  <div className="text-3xl font-bold text-gray-900 mb-4">$19.99</div>
                  <ul className="text-sm text-gray-600 space-y-2 mb-6">
                    <li>50 exports per month</li>
                    <li>1080p maximum</li>
                    <li>No watermark</li>
                  </ul>
                  <button
                    onClick={() => setShowRegister(true)}
                    className="w-full py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                  >
                    Start Free Trial
                  </button>
                </div>
              </div>

              {/* Pro Plan */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Crown className="w-5 h-5 text-purple-500 mr-2" />
                    <h3 className="text-xl font-bold text-gray-900">Professional</h3>
                  </div>
                  <div className="text-3xl font-bold text-gray-900 mb-4">$39.99</div>
                  <ul className="text-sm text-gray-600 space-y-2 mb-6">
                    <li>100 exports per month</li>
                    <li>4K maximum</li>
                    <li>Advanced AI features</li>
                  </ul>
                  <button
                    onClick={() => setShowRegister(true)}
                    className="w-full py-2 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg hover:shadow-lg"
                  >
                    Start Free Trial
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      <LoginModal
        isOpen={showLogin}
        onClose={() => setShowLogin(false)}
        onSwitchToRegister={() => {
          setShowLogin(false);
          setShowRegister(true);
        }}
      />

      <RegisterModal
        isOpen={showRegister}
        onClose={() => setShowRegister(false)}
        onSwitchToLogin={() => {
          setShowRegister(false);
          setShowLogin(true);
        }}
      />
    </div>
  );
};

export default HomePage;