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
      let errorMessage = `API error: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        }
      } catch {
        // If response is not JSON, keep the default error message
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  async getStatus() {
    return this.request('/status');
  }

  async getNotes() {
    return this.request('/notes');
  }

  async getTools() {
    return this.request('/tools');
  }

  async processInput(input) {
    return this.request(`/process?input=${encodeURIComponent(input)}`);
  }

  async processInputPost(input) {
    return this.request('/process', {
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
    return this.request('/reset-conversation');
  }

  async getConversationHistory() {
    return this.request('/conversation-history');
  }

  async createDefaultNoteGroups() {
    return this.request('/admin/create-default-note-groups');
  }

  async resetDatabase() {
    return this.request('/admin/database/reset');
  }

  async getRequests(limit = 100) {
    return this.request(`/requests?limit=${limit}`);
  }

  async getMemory(userId = 'default') {
    return this.request(`/memory?user_id=${userId}`);
  }

  async clearMemory(userId = 'default') {
    return this.request(`/memory?user_id=${userId}`, {
      method: 'DELETE',
    });
  }
}

export default new ApiService();
