class HistoryManager {
  constructor(maxHistory = 50) {
    this.maxHistory = maxHistory;
    this.history = [];
    this.currentIndex = -1;
    this.initialState = null;
  }
  
  // Initialize with the starting state
  initialize(initialState) {
    this.initialState = JSON.parse(JSON.stringify(initialState));
    this.history = [];
    this.currentIndex = -1;
  }
  
  // Add a new action to history
  addAction(action) {
    // Remove any actions after current index (when undoing then making new changes)
    this.history = this.history.slice(0, this.currentIndex + 1);
    
    // Add the new action
    const historyEntry = {
      ...action,
      id: Date.now() + Math.random(), // Unique ID
      timestamp: action.timestamp || Date.now()
    };
    
    this.history.push(historyEntry);
    
    // Trim history if it exceeds max length
    if (this.history.length > this.maxHistory) {
      this.history = this.history.slice(-this.maxHistory);
    }
    
    this.currentIndex = this.history.length - 1;
  }
  
  // Check if undo is possible
  canUndo() {
    return this.currentIndex >= 0;
  }
  
  // Check if redo is possible
  canRedo() {
    return this.currentIndex < this.history.length - 1;
  }
  
  // Undo the last action
  undo() {
    if (!this.canUndo()) {
      return null;
    }
    
    const action = this.history[this.currentIndex];
    this.currentIndex--;
    
    // Return the old state to revert to
    return action.oldState;
  }
  
  // Redo the next action
  redo() {
    if (!this.canRedo()) {
      return null;
    }
    
    this.currentIndex++;
    const action = this.history[this.currentIndex];
    
    // Return the new state to apply
    return action.newState;
  }
  
  // Get current state by replaying all actions up to current index
  getCurrentState() {
    if (this.currentIndex < 0) {
      return this.initialState;
    }
    
    return this.history[this.currentIndex].newState;
  }
  
  // Get history summary for debugging
  getHistorySummary() {
    return this.history.map((action, index) => ({
      index,
      type: action.type,
      elementId: action.elementId,
      property: action.property,
      timestamp: new Date(action.timestamp).toLocaleTimeString(),
      isCurrent: index === this.currentIndex
    }));
  }
  
  // Clear all history
  clear() {
    this.history = [];
    this.currentIndex = -1;
  }
  
  // Get action description for UI
  getActionDescription(action) {
    switch (action.type) {
      case 'transform':
        return `Move ${action.elementId}`;
      
      case 'property':
        return `Change ${action.property} of ${action.elementId}`;
      
      case 'canvas':
        return `Change canvas ${action.property}`;
      
      case 'align':
        return `Align ${action.elements?.length || 1} element(s) ${action.alignment}`;
      
      case 'brand-kit':
        return `Apply brand kit to ${action.elements?.length || 1} element(s)`;
      
      default:
        return `${action.type} action`;
    }
  }
  
  // Get the last N actions for display
  getRecentActions(count = 10) {
    const recentActions = this.history.slice(-count);
    return recentActions.map(action => ({
      id: action.id,
      description: this.getActionDescription(action),
      timestamp: action.timestamp,
      type: action.type
    }));
  }
  
  // Save history to localStorage (for persistence across page reloads)
  saveToStorage(projectId) {
    try {
      const historyData = {
        history: this.history,
        currentIndex: this.currentIndex,
        initialState: this.initialState,
        timestamp: Date.now()
      };
      
      localStorage.setItem(`editor_history_${projectId}`, JSON.stringify(historyData));
    } catch (error) {
      console.warn('Failed to save history to storage:', error);
    }
  }
  
  // Load history from localStorage
  loadFromStorage(projectId) {
    try {
      const stored = localStorage.getItem(`editor_history_${projectId}`);
      if (!stored) return false;
      
      const historyData = JSON.parse(stored);
      
      // Check if the stored history is recent (within 24 hours)
      const age = Date.now() - historyData.timestamp;
      if (age > 24 * 60 * 60 * 1000) {
        localStorage.removeItem(`editor_history_${projectId}`);
        return false;
      }
      
      this.history = historyData.history || [];
      this.currentIndex = historyData.currentIndex || -1;
      this.initialState = historyData.initialState;
      
      return true;
    } catch (error) {
      console.warn('Failed to load history from storage:', error);
      return false;
    }
  }
  
  // Clean up old stored histories
  static cleanupStorage() {
    try {
      const keys = Object.keys(localStorage);
      const historyKeys = keys.filter(key => key.startsWith('editor_history_'));
      
      historyKeys.forEach(key => {
        try {
          const stored = localStorage.getItem(key);
          const historyData = JSON.parse(stored);
          const age = Date.now() - historyData.timestamp;
          
          // Remove histories older than 7 days
          if (age > 7 * 24 * 60 * 60 * 1000) {
            localStorage.removeItem(key);
          }
        } catch (error) {
          // Remove corrupted entries
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.warn('Failed to cleanup storage:', error);
    }
  }
}

export default HistoryManager;