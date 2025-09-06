import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Compass, 
  FileText, 
  FolderOpen, 
  Download, 
  Palette, 
  Upload,
  Menu,
  X
} from 'lucide-react';

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();
  
  const menuItems = [
    { icon: Compass, label: 'Explore', path: '/explore' },
    { icon: FileText, label: 'Templates', path: '/templates' },
    { icon: FolderOpen, label: 'My Projects', path: '/my-projects' },
    { icon: Download, label: 'Exports', path: '/exports' },
    { icon: Palette, label: 'Brand Kits', path: '/brand-kits' },
    { icon: Upload, label: 'Import', path: '/import' },
  ];

  return (
    <>
      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full bg-white/80 backdrop-blur-xl border-r border-gray-200/50 shadow-xl transition-all duration-300 z-40 ${
        open ? 'w-64' : 'w-16'
      }`}>
        {/* Logo */}
        <div className="p-6 border-b border-gray-200/50">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
            </div>
            {open && (
              <div className="ml-3">
                <h1 className="text-xl font-bold text-gray-900">MotionEdit</h1>
                <p className="text-xs text-gray-500">Create & Edit</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || (item.path === '/explore' && location.pathname === '/');
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-3 mb-1 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? 'bg-gradient-to-r from-orange-500/10 to-red-500/10 text-orange-600 shadow-sm'
                    : 'text-gray-600 hover:bg-gray-100/50 hover:text-gray-900'
                }`}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-orange-600' : 'text-gray-500'}`} />
                {open && (
                  <span className="ml-3 font-medium">{item.label}</span>
                )}
                {!open && (
                  <div className="absolute left-16 bg-gray-900 text-white px-2 py-1 rounded-md text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                    {item.label}
                  </div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Pro Tip at bottom */}
        {open && (
          <div className="absolute bottom-6 left-3 right-3">
            <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200/50 rounded-xl p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">💡</span>
                  </div>
                </div>
                <div className="ml-3">
                  <h4 className="text-sm font-semibold text-gray-900">Pro Tip</h4>
                  <p className="text-xs text-gray-600 mt-1">
                    Use natural language commands in the editor to quickly modify your templates!
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Sidebar;