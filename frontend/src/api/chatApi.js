import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ChatAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async sendMessage(message, conversationHistory = [], sessionId = null) {
    try {
      const response = await this.client.post('/api/chat', {
        message,
        conversation_history: conversationHistory,
        session_id: sessionId,
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw new Error(
        error.response?.data?.detail || 'Failed to send message. Please try again.'
      );
    }
  }

  async checkHealth() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      return { status: 'unhealthy' };
    }
  }

  async clearSession(sessionId) {
    try {
      await this.client.delete(`/api/chat/${sessionId}`);
      return true;
    } catch (error) {
      console.error('Error clearing session:', error);
      return false;
    }
  }
}

export const chatAPI = new ChatAPI();

