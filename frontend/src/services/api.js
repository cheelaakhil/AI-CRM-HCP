/**
 * Axios API instance configured for the FastAPI backend.
 */
import axios from 'axios';

const isProd = import.meta.env.PROD;
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || (isProd ? '/api' : 'http://localhost:8000/api'),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s — agent calls may take time
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
