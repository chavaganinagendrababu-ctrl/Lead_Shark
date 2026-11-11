import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, ShieldCheck, Lock, Mail, ArrowRight, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Login = () => {
  const [email, setEmail] = useState('admin@leadshark.io');
  const [password, setPassword] = useState('AdminLeadShark2026!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email.trim(), password);
      navigate('/');
    } catch (err) {
      if (err.message && err.message.includes('Network Error')) {
        setError('Unable to reach backend server. If your Render backend is on the free tier, it takes ~30-50 seconds to wake up on first request. Please wait a moment and try again.');
      } else if (err.response?.status === 404 || err.response?.status === 405 || (typeof err.response?.data === 'string' && err.response?.data.includes('<!DOCTYPE html>'))) {
        setError('API endpoint unreachable. Please ensure VITE_API_BASE_URL is set in your Vercel project settings to your deployed Render URL (e.g. https://leadshark-backend.onrender.com) and that the project was redeployed.');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          setError(detail.map(d => d.msg || d).join(', '));
        } else if (typeof detail === 'string') {
          setError(detail);
        } else {
          setError('Invalid credentials');
        }
      } else {
        setError(err.message || 'Authentication failed. Please verify credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  const isVercelMissingEnv = typeof window !== 'undefined' &&
    window.location.hostname.endsWith('vercel.app') &&
    !import.meta.env.VITE_API_BASE_URL;

  const quickFill = (roleEmail, rolePass) => {
    setEmail(roleEmail);
    setPassword(rolePass);
    setError('');
  };

  return (
    <div className="min-h-screen bg-navy-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background glowing accents */}
      <div className="absolute top-0 -left-40 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-0 -right-40 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 text-center">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-600 to-blue-500 shadow-xl shadow-cyan-950/50 mb-4 border border-cyan-400/30">
          <Layers className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">
          LEAD <span className="text-cyan-400">SHARK</span>
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Enterprise Lead Discovery & Compliant Outreach Platform
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="bg-navy-900 py-8 px-6 shadow-2xl rounded-2xl sm:px-10 border border-slate-800">
          {isVercelMissingEnv && (
            <div className="mb-5 p-3.5 rounded-lg bg-amber-950/80 border border-amber-800/80 text-amber-200 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <span>
                <strong>Action Required in Vercel:</strong> Missing <code className="bg-amber-900/60 px-1 py-0.5 rounded text-white">VITE_API_BASE_URL</code> environment variable. Add it in Vercel Project Settings &gt; Environment Variables pointing to your Render backend URL, then click <strong>Redeploy</strong>.
              </span>
            </div>
          )}

          {error && (
            <div className="mb-5 p-3.5 rounded-lg bg-red-950/80 border border-red-800/80 text-red-200 text-sm flex items-start gap-2.5">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Work Email Address
              </label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-slate-500" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 bg-navy-950 border border-slate-700 rounded-lg text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                  placeholder="name@company.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-slate-500" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 bg-navy-950 border border-slate-700 rounded-lg text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg shadow-md text-sm font-semibold text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 transition disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <span>Sign In to Platform</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Development Quick Role Switcher */}
          <div className="mt-8 pt-6 border-t border-slate-800">
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider text-center mb-3">
              Fast Assessment Role Accounts
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => quickFill('admin@leadshark.io', 'AdminLeadShark2026!')}
                className="py-1.5 px-2 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-purple-300 border border-purple-800/40 transition text-center"
              >
                Admin
              </button>
              <button
                type="button"
                onClick={() => quickFill('reviewer@leadshark.io', 'ReviewerLeadShark2026!')}
                className="py-1.5 px-2 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-blue-300 border border-blue-800/40 transition text-center"
              >
                Reviewer
              </button>
              <button
                type="button"
                onClick={() => quickFill('sales@leadshark.io', 'SalesLeadShark2026!')}
                className="py-1.5 px-2 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-800/40 transition text-center"
              >
                Sales
              </button>
            </div>
            <p className="mt-3 text-[11px] text-slate-500 text-center leading-relaxed">
              Role permissions strictly enforced on both API and user interface.
            </p>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-500">
          <ShieldCheck className="w-4 h-4 text-cyan-500" />
          <span>CAN-SPAM & GDPR Compliant Architecture</span>
        </div>
      </div>
    </div>
  );
};

