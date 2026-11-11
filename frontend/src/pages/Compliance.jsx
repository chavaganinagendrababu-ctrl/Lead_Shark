import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Search, 
  Plus, 
  Ban, 
  Trash2, 
  Send, 
  AlertCircle,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import api from '../services/api';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { useAuth } from '../context/AuthContext';

const REASONS = [
  'unsubscribed',
  'hard_bounce',
  'spam_complaint',
  'manual_suppression',
  'data_deletion'
];

export const Compliance = () => {
  const { isReviewer, isAdmin } = useAuth();
  const [suppressions, setSuppressions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Unsubscribe Simulator
  const [testEmail, setTestEmail] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [testingUnsub, setTestingUnsub] = useState(false);

  const [formData, setFormData] = useState({
    email: '',
    reason: 'manual_suppression',
    notes: 'Manually suppressed by compliance team'
  });

  const fetchSuppressions = async () => {
    try {
      setLoading(true);
      const res = await api.get('/suppression', {
        params: { search: search || undefined }
      });
      setSuppressions(res.data);
    } catch (err) {
      console.error('Failed to load suppression records', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppressions();
  }, [search]);

  const handleAddSuppression = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setActionLoading(true);
    try {
      await api.post('/suppression', formData);
      setShowAddModal(false);
      setFormData({
        email: '',
        reason: 'manual_suppression',
        notes: ''
      });
      fetchSuppressions();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to add suppression entry');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSimulateUnsubscribe = async (e) => {
    e.preventDefault();
    if (!testEmail) return;
    setTestingUnsub(true);
    setTestResult(null);
    try {
      // Direct post to unsubscribe test route or add suppression
      const res = await api.post('/suppression', {
        email: testEmail,
        reason: 'unsubscribed',
        notes: 'Simulated 1-click unsubscribe opt-out test'
      });
      setTestResult({
        success: true,
        message: `Successfully placed ${testEmail} on Global Suppression List! All future imports and campaigns will strictly block this address.`
      });
      fetchSuppressions();
    } catch (err) {
      setTestResult({
        success: false,
        message: err.response?.data?.detail || 'Simulated opt-out failed.'
      });
    } finally {
      setTestingUnsub(false);
    }
  };

  const getReasonBadge = (reason) => {
    switch (reason) {
      case 'unsubscribed':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 uppercase">Unsubscribed</span>;
      case 'hard_bounce':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200 uppercase">Hard Bounce</span>;
      case 'spam_complaint':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200 uppercase">Spam Complaint</span>;
      case 'data_deletion':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-50 text-red-800 border border-red-300 uppercase">GDPR Deletion</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-300 uppercase">Manual</span>;
    }
  };

  return (
    <DashboardLayout
      title="Compliance & Global Suppression"
      subtitle="Universal opt-out registry, anti-spam enforcement, and GDPR Article 17 erasure protection"
    >
      {/* Overview Card */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldAlert className="w-5 h-5 text-rose-600" />
            <h2 className="text-base font-bold text-slate-800">Universal Suppression Filter</h2>
          </div>
          <p className="text-xs text-slate-500 max-w-2xl leading-relaxed">
            Emails and domains on this list are permanently blocked across all discovery pipelines, CSV imports, and campaign audiences. Deletion requests never silently remove suppression protection.
          </p>
        </div>

        {isReviewer && (
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-navy-800 hover:bg-navy-900 rounded-lg shadow-sm transition shrink-0"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add to Suppression List</span>
          </button>
        )}
      </div>

      {/* Simulator Section */}
      <div className="bg-gradient-to-r from-slate-900 to-navy-950 p-6 rounded-2xl border border-slate-800 text-white shadow-lg">
        <h3 className="text-sm font-bold flex items-center gap-2 text-cyan-400 mb-1">
          <Ban className="w-4 h-4" />
          <span>Interactive Unsubscribe & Opt-Out Testing Simulator</span>
        </h3>
        <p className="text-xs text-slate-300 mb-4 max-w-xl">
          Simulate a recipient clicking their signed one-click opt-out token to verify that suppression engages immediately across the entire database.
        </p>

        <form onSubmit={handleSimulateUnsubscribe} className="flex flex-col sm:flex-row items-center gap-3 max-w-lg mb-3">
          <input
            type="email"
            required
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            placeholder="recipient@testcompany.com"
            className="w-full sm:flex-1 px-3.5 py-2 text-xs bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
          <button
            type="submit"
            disabled={testingUnsub}
            className="w-full sm:w-auto px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold transition disabled:opacity-50"
          >
            {testingUnsub ? 'Suppressing...' : 'Simulate Opt-Out'}
          </button>
        </form>

        {testResult && (
          <div className={`p-3 rounded-lg text-xs flex items-center gap-2 max-w-lg ${testResult.success ? 'bg-emerald-950/80 text-emerald-200 border border-emerald-800' : 'bg-rose-950/80 text-rose-200 border border-rose-800'}`}>
            {testResult.success ? <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />}
            <span>{testResult.message}</span>
          </div>
        )}
      </div>

      {/* Suppression List Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative max-w-sm w-full">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search email, domain, or reason..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 rounded-full text-slate-700">
            {suppressions.length} Suppressed Records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">Suppressed Target</th>
                <th className="py-3 px-4">Reason Category</th>
                <th className="py-3 px-4">Compliance Notes</th>
                <th className="py-3 px-4">Added By</th>
                <th className="py-3 px-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-400">Loading suppression list...</td>
                </tr>
              ) : suppressions.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-400">
                    No suppression records found.
                  </td>
                </tr>
              ) : (
                suppressions.map((entry) => (
                  <tr key={entry.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 px-4">
                      <p className="font-mono font-bold text-slate-900">{entry.email}</p>
                      {entry.domain && <p className="text-[10px] text-slate-400">Domain: {entry.domain}</p>}
                    </td>
                    <td className="py-3 px-4">
                      {getReasonBadge(entry.reason)}
                    </td>
                    <td className="py-3 px-4 text-slate-600 max-w-xs truncate">
                      {entry.notes || '—'}
                    </td>
                    <td className="py-3 px-4 text-slate-500 text-[11px]">
                      {entry.added_by || 'system'}
                    </td>
                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                      {new Date(entry.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Suppression Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-200">
            <h3 className="text-base font-bold text-slate-900 mb-1">Add to Global Suppression</h3>
            <p className="text-xs text-slate-500 mb-4">
              Enter target email address to permanently suppress from all outbound activity.
            </p>

            {errorMsg && (
              <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleAddSuppression} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Email *</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="contact@suppressme.com"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Reason</label>
                <select
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500 capitalize"
                >
                  {REASONS.map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Notes / Legal Reference</label>
                <input
                  type="text"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="e.g. Recipient request via customer service ticket #8812"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div className="pt-3 flex justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-semibold transition"
                >
                  {actionLoading ? 'Saving...' : 'Add to Suppression'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};

