import React, { useState } from 'react';
import { Search, Bell, User, Globe, Menu, X } from 'lucide-react';

const TopBar = ({ sidebarOpen, setSidebarOpen }) => {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header className="bg-white/70 backdrop-blur-xl border-b border-gray-200/50 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Menu toggle and search */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100/50 transition-colors"
          >
            {sidebarOpen ? (
              <X className="w-5 h-5 text-gray-600" />
            ) : (
              <Menu className="w-5 h-5 text-gray-600" />
            )}
          </button>

          {/* Search Bar */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search templates, projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-80 pl-10 pr-3 py-2 border border-gray-200/50 rounded-xl bg-white/50 backdrop-blur-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300 transition-colors"
            />
          </div>
        </div>

        {/* Right side - Language switcher, notifications, profile */}
        <div className="flex items-center space-x-3">
          {/* Language Switcher */}
          <button className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100/50 transition-colors">
            <Globe className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">EN</span>
          </button>

          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-gray-100/50 transition-colors">
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-orange-500 rounded-full flex items-center justify-center">
              <span className="text-xs font-bold text-white">2</span>
            </span>
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-medium text-gray-900">Creative User</p>
              <p className="text-xs text-gray-500">Pro Plan</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopBar;