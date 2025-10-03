// API service for Soul Mirror backend

const API_BASE = import.meta.env.VITE_API_BASE || '';
const TEST_API_BASE = import.meta.env.VITE_TEST_API_BASE || '';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  }

  async getStatus() {
    return this.request('/api/status');
  }

  async getNotes() {
    return this.request('/api/notes');
  }

  async getTools() {
    return this.request('/api/tools');
  }

  async processInput(input) {
    return this.request(`/api/process?input=${encodeURIComponent(input)}`);
  }

  async processInputPost(input) {
    return this.request('/api/process', {
      method: 'POST',
      body: JSON.stringify({ input }),
    });
  }

  async testRequest(endpoint, options = {}) {
    const url = `${TEST_API_BASE}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Test API error: ${response.status}`);
    }

    return response.json();
  }

  async getTestScenarios() {
    return this.testRequest('/api/scenarios');
  }

  async runAllTests() {
    return this.testRequest('/api/run-all');
  }

  async runScenario(scenarioName) {
    return this.testRequest(`/api/run-scenario?scenario_name=${encodeURIComponent(scenarioName)}`);
  }

  async resetConversation() {
    return this.request('/api/reset-conversation');
  }

  async getConversationHistory() {
    return this.request('/api/conversation-history');
  }

  async createDefaultNoteGroups() {
    return this.request('/api/admin/create-default-note-groups');
  }
}

export default new ApiService();
