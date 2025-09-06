import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';

// Components
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import ExplorePage from './pages/ExplorePage';
import TemplatesPage from './pages/TemplatesPage';
import EditorPage from './pages/EditorPage';
import MyProjectsPage from './pages/MyProjectsPage';
import ExportsPage from './pages/ExportsPage';
import BrandKitsPage from './pages/BrandKitsPage';
import ImportPage from './pages/ImportPage';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="App">
      <BrowserRouter>
        <div className="flex h-screen bg-gradient-to-br from-slate-50 to-blue-50">
          {/* Sidebar */}
          <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
          
          {/* Main Content */}
          <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
            {/* Top Bar */}
            <TopBar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
            
            {/* Page Content */}
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/" element={<ExplorePage />} />
                <Route path="/explore" element={<ExplorePage />} />
                <Route path="/templates" element={<TemplatesPage />} />
                <Route path="/editor" element={<EditorPage />} />
                <Route path="/editor/:templateId" element={<EditorPage />} />
                <Route path="/my-projects" element={<MyProjectsPage />} />
                <Route path="/exports" element={<ExportsPage />} />
                <Route path="/brand-kits" element={<BrandKitsPage />} />
                <Route path="/import" element={<ImportPage />} />
              </Routes>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;