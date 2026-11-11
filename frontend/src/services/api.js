import axios from 'axios';

const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (!envUrl) {
    return '/api';
  }
  let url = envUrl.trim().replace(/\/+$/, '');
  // If the user specified an absolute backend URL without the /api suffix, append it automatically
  if ((url.startsWith('http://') || url.startsWith('https://')) && !url.endsWith('/api')) {
    url = `${url}/api`;
  }
  return url;
};

const api = axios.create({
  baseURL: getBaseUrl(),
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

