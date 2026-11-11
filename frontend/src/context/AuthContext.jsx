import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('leadshark_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('leadshark_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
          localStorage.setItem('leadshark_user', JSON.stringify(res.data));
        } catch (err) {
          logout();
        }
      }
      setLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token } = res.data;
    localStorage.setItem('leadshark_token', access_token);
    setToken(access_token);

    // Fetch user details
    const userRes = await api.get('/auth/me', {
      headers: { Authorization: `Bearer ${access_token}` }
    });
    setUser(userRes.data);
    localStorage.setItem('leadshark_user', JSON.stringify(userRes.data));
    return userRes.data;
  };

  const logout = () => {
    localStorage.removeItem('leadshark_token');
    localStorage.removeItem('leadshark_user');
    setToken(null);
    setUser(null);
  };

  const role = user?.role || 'guest';
  const isAdmin = role === 'admin';
  const isReviewer = role === 'reviewer' || isAdmin;
  const isSales = role === 'sales' || isAdmin;

  return (
    <AuthContext.Provider value={{ user, token, role, isAdmin, isReviewer, isSales, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

