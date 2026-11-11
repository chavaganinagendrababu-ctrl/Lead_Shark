import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercept requests to attach auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('leadshark_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercept responses for auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // If unauthorized and not already on login, clear and redirect
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/unsubscribe')) {
        localStorage.removeItem('leadshark_token');
        localStorage.removeItem('leadshark_user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

