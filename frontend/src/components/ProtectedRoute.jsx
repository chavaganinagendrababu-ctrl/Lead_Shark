import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, token, loading, role } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-300 font-medium text-sm">Authenticating Lead Shark...</p>
        </div>
      </div>
    );
  }

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(role) && role !== 'admin') {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8 max-w-md text-center">
          <h2 className="text-xl font-bold text-red-600 mb-2">Access Restricted</h2>
          <p className="text-slate-600 text-sm mb-4">
            Your assigned role (<span className="font-semibold text-slate-800 uppercase">{role}</span>) does not have authorization to view this module.
          </p>
          <a href="/" className="inline-block px-4 py-2 bg-navy-800 text-white rounded-lg text-sm font-medium hover:bg-navy-900 transition">
            Return to Dashboard
          </a>
        </div>
      </div>
    );
  }

  return children;
};

