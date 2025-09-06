import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  RotateCw, 
  Download, 
  Save,
  Type,
  Image,
  BarChart3,
  MapPin,
  Layers,
  Settings
} from 'lucide-react';
import { apiService } from '../services/api';

const EditorPage = () => {
  const { templateId } = useParams();
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeTab, setActiveTab] = useState('Content');
  const [selectedElement, setSelectedElement] = useState(null);
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  const [template, setTemplate] = useState(null);
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  const tabs = ['Content', 'Style', 'Animation'];

  useEffect(() => {
    const loadTemplate = async () => {
      if (templateId) {
        try {
          const templateData = await apiService.getTemplate(templateId);
          setTemplate(templateData);
          
          // Create a project from template if it doesn't exist
          const projectData = {
            title: `Project from ${templateData.title}`,
            template_id: templateId,
            template_title: templateData.title,
            thumbnail: templateData.preview,
            status: 'Draft',
            duration: templateData.duration,
            user_id: 'current_user', // In real app, get from auth
            project_data: templateData.template_data || {}
          };
          
          const createdProject = await apiService.createProject(projectData);
          setProject(createdProject);
        } catch (error) {
          console.error('Error loading template:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    loadTemplate();
  }, [templateId]);

  const elements = template?.template_data?.elements || [
    { id: 'title', type: 'text', name: 'Main Title', content: 'Your Amazing Project' },
    { id: 'subtitle', type: 'text', name: 'Subtitle', content: 'Professional Motion Graphics' },
    { id: 'logo', type: 'image', name: 'Logo', content: 'company-logo.png' },
    { id: 'background', type: 'shape', name: 'Background', content: 'Rectangle Shape' },
  ];

  const runCommand = async () => {
    if (!command.trim() || !project) return;
    
    try {
      // Call the backend API for natural language command parsing
      const commandData = {
        command: command.trim(),
        element_id: selectedElement,
        project_id: project.id
      };
      
      const result = await apiService.parseCommand(commandData);
      
      const newCommand = {
        id: Date.now(),
        command: command,
        timestamp: new Date().toLocaleTimeString(),
        success: result.success,
        message: result.message,
        changes: result.changes || {}
      };
      
      setCommandHistory([...commandHistory, newCommand]);
      setCommand('');
      
      // If successful, you could update the UI here based on the changes
      if (result.success) {
        console.log('Command executed successfully:', result.message);
        // Here you could update the template preview based on the changes
      }
    } catch (error) {
      console.error('Error executing command:', error);
      const errorCommand = {
        id: Date.now(),
        command: command,
        timestamp: new Date().toLocaleTimeString(),
        success: false,
        message: 'Error executing command'
      };
      setCommandHistory([...commandHistory, errorCommand]);
      setCommand('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      runCommand();
    }
  };

  return (
    <div className="h-full flex">
      {/* Main Editor Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Toolbar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-lg font-semibold text-gray-900">Template Editor</h2>
              <span className="text-sm text-gray-500">#{templateId}</span>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex items-center px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
              >
                {isPlaying ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                {isPlaying ? 'Pause' : 'Play'}
              </button>
              
              <button className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                <Save className="w-4 h-4 mr-2" />
                Save
              </button>
              
              <button className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Canvas Area */}
        <div className="flex-1 bg-gray-100 p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-black rounded-lg aspect-video relative overflow-hidden shadow-2xl">
              {/* Preview Canvas */}
              <div className="w-full h-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
                <div className="text-center text-white">
                  <h1 className="text-4xl font-bold mb-4">Your Amazing Project</h1>
                  <p className="text-xl opacity-90">Professional Motion Graphics</p>
                  
                  {/* Mock logo */}
                  <div className="mt-8 w-16 h-16 bg-white/20 rounded-full mx-auto flex items-center justify-center">
                    <span className="text-2xl">🚀</span>
                  </div>
                </div>
              </div>
              
              {/* Selection indicators */}
              {selectedElement && (
                <div className="absolute inset-4 border-2 border-orange-500 rounded pointer-events-none">
                  <div className="absolute -top-8 left-0 bg-orange-500 text-white px-2 py-1 text-xs rounded">
                    Selected: {elements.find(e => e.id === selectedElement)?.name}
                  </div>
                </div>
              )}
            </div>

            {/* Timeline */}
            <div className="mt-6 bg-white rounded-lg p-4 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Timeline</h3>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-gray-600 hover:text-gray-900">
                    <RotateCcw className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-600 hover:text-gray-900">
                    <RotateCw className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="h-16 bg-gray-50 rounded border-2 border-dashed border-gray-200 flex items-center justify-center">
                <span className="text-gray-500 text-sm">Timeline visualization (5 seconds)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
        {/* Natural Language Commands */}
        <div className="p-6 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-4">Command</h3>
          <div className="space-y-3">
            <input
              type="text"
              placeholder="Type a command..."
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
            />
            <button
              onClick={runCommand}
              className="w-full bg-orange-500 text-white py-2 rounded-lg hover:bg-orange-600 transition-colors"
            >
              Run
            </button>
          </div>
          
          {/* Command History */}
          {commandHistory.length > 0 && (
            <div className="mt-4 space-y-2 max-h-32 overflow-y-auto">
              {commandHistory.slice(-3).map((cmd) => (
                <div key={cmd.id} className={`text-xs p-2 rounded ${
                  cmd.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}>
                  <div className={`font-medium ${
                    cmd.success ? 'text-green-900' : 'text-red-900'
                  }`}>{cmd.command}</div>
                  <div className={`${
                    cmd.success ? 'text-green-600' : 'text-red-600'
                  }`}>{cmd.message}</div>
                  <div className="text-gray-500">{cmd.timestamp}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Properties Panel */}
        <div className="flex-1 flex flex-col">
          {/* Tabs */}
          <div className="flex border-b border-gray-200">
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-3 px-4 text-sm font-medium ${
                  activeTab === tab
                    ? 'text-orange-600 border-b-2 border-orange-500 bg-orange-50/50'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Elements List */}
          <div className="p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Elements</h4>
            <div className="space-y-2">
              {elements.map((element) => {
                const getIcon = (type) => {
                  switch (type) {
                    case 'text': return Type;
                    case 'image': return Image;
                    case 'chart': return BarChart3;
                    case 'map': return MapPin;
                    case 'shape': return Layers;
                    default: return Settings;
                  }
                };
                
                const Icon = getIcon(element.type);
                
                return (
                  <button
                    key={element.id}
                    onClick={() => setSelectedElement(element.id)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedElement === element.id
                        ? 'bg-orange-100 border border-orange-200'
                        : 'hover:bg-gray-50 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center">
                      <Icon className={`w-4 h-4 mr-3 ${
                        selectedElement === element.id ? 'text-orange-600' : 'text-gray-500'
                      }`} />
                      <div>
                        <div className="font-medium text-gray-900">{element.name}</div>
                        <div className="text-sm text-gray-500">{element.content}</div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Properties for selected element */}
          {selectedElement && (
            <div className="border-t border-gray-200 p-6">
              <h4 className="font-semibold text-gray-900 mb-4">Properties</h4>
              
              {activeTab === 'Content' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Text Content</label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                      defaultValue="Your Amazing Project"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Font Size</label>
                    <input
                      type="range"
                      min="12"
                      max="72"
                      className="w-full"
                    />
                  </div>
                </div>
              )}
              
              {activeTab === 'Style' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Color</label>
                    <input
                      type="color"
                      className="w-full h-10 border border-gray-200 rounded-lg"
                      defaultValue="#ffffff"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Opacity</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      className="w-full"
                    />
                  </div>
                </div>
              )}
              
              {activeTab === 'Animation' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Animation Type</label>
                    <select className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20">
                      <option>Fade In</option>
                      <option>Slide In</option>
                      <option>Scale In</option>
                      <option>Bounce In</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Duration (seconds)</label>
                    <input
                      type="number"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                      defaultValue="1"
                      min="0.1"
                      max="10"
                      step="0.1"
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EditorPage;