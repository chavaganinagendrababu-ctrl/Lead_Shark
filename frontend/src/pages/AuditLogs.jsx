import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Search, 
  Filter, 
  Shield, 
  ChevronLeft, 
  ChevronRight,
  User,
  Clock,
  Terminal
} from 'lucide-react';
import api from '../services/api';
import { DashboardLayout } from '../layouts/DashboardLayout';

const ACTIONS = [
  'All',
  'LOGIN_SUCCESS',
  'LOGIN_FAILED',
  'LEAD_CREATE',
  'LEAD_UPDATE',
  'LEAD_DELETE',
  'CSV_IMPORT',
  'CAMPAIGN_CREATE',
  'CAMPAIGN_APPROVED',
  'CAMPAIGN_REJECTED',
  'CAMPAIGN_UPDATE',
  'SUPPRESSION_ADD',
  'UNSUBSCRIBE'
];

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size] = useState(20);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('All');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        size,
        search: search || undefined,
        action: actionFilter !== 'All' ? actionFilter : undefined
      };
      const res = await api.get('/audit-logs', { params });
      setLogs(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error('Failed to load audit logs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, actionFilter]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  const getActionColor = (action) => {
    if (action.includes('LOGIN')) return 'bg-purple-100 text-purple-800 border-purple-200';
    if (action.includes('CREATE') || action.includes('APPROVED')) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (action.includes('DELETE') || action.includes('REJECTED')) return 'bg-rose-100 text-rose-800 border-rose-200';
    if (action.includes('SUPPRESSION') || action.includes('UNSUBSCRIBE')) return 'bg-amber-100 text-amber-800 border-amber-200';
    return 'bg-blue-100 text-blue-800 border-blue-200';
  };

  const totalPages = Math.ceil(total / size) || 1;

  return (
    <DashboardLayout
      title="Security & Compliance Audit Logs"
      subtitle="Immutable audit trail of authentication events, lead mutations, approvals, and suppressions"
    >
      {/* Header controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <form onSubmit={handleSearch} className="flex-1 flex items-center gap-2 max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search by actor email, action, details..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
          <button type="submit" className="px-3 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg text-xs font-semibold">
            Search
          </button>
        </form>

        <div className="flex items-center gap-3">
          <select
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-700 text-xs font-medium focus:outline-none"
          >
            {ACTIONS.map(a => <option key={a} value={a}>Action: {a}</option>)}
          </select>
          <span className="text-xs font-semibold text-slate-500 whitespace-nowrap">
            {total} Audit Records
          </span>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Target Object</th>
                <th className="py-3 px-4">Operational Details</th>
                <th className="py-3 px-4">IP Address</th>
                <th className="py-3 px-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">Loading audit records...</td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">No audit log records found matching query.</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getActionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-slate-800">{log.actor_email}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-[11px] font-bold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
                        {log.object_type} {log.object_id ? `#${log.object_id}` : ''}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-700 max-w-sm truncate">
                      {log.details || '—'}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {log.ip_address || '127.0.0.1'}
                    </td>
                    <td className="py-3 px-4 text-slate-500 whitespace-nowrap text-[11px]">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-3.5 border-t border-slate-200 bg-slate-50/50 flex items-center justify-between text-xs">
          <p className="text-slate-500">
            Page <span className="font-bold text-slate-800">{page}</span> of <span className="font-bold text-slate-800">{totalPages}</span>
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded border border-slate-200 bg-white text-slate-600 disabled:opacity-40 hover:bg-slate-50"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 rounded border border-slate-200 bg-white text-slate-600 disabled:opacity-40 hover:bg-slate-50"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

