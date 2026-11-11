import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, 
  CheckCircle2, 
  Clock, 
  Send, 
  ShieldAlert, 
  ArrowUpRight, 
  Building2, 
  Compass, 
  RefreshCw,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';
import api from '../services/api';
import { DashboardLayout } from '../layouts/DashboardLayout';

export const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    try {
      setRefreshing(true);
      const res = await api.get('/dashboard/stats');
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load dashboard metrics', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <DashboardLayout title="Dashboard" subtitle="Operational metrics & compliance status">
        <div className="h-96 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </DashboardLayout>
    );
  }

  const kpis = [
    { label: 'Total Leads Staged', value: stats?.total_leads || 0, icon: Users, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Verified Clean Emails', value: stats?.verified_leads || 0, icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { label: 'Pending Compliance Review', value: stats?.pending_review || 0, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
    { label: 'Approved for Outreach', value: stats?.approved_leads || 0, icon: TrendingUp, color: 'text-cyan-600', bg: 'bg-cyan-50' },
    { label: 'Active Campaigns', value: stats?.active_campaigns || 0, icon: Send, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { label: 'Global Suppressed', value: stats?.suppressed_leads || 0, icon: ShieldAlert, color: 'text-rose-600', bg: 'bg-rose-50' },
  ];

  return (
    <DashboardLayout 
      title="Platform Overview" 
      subtitle="Real-time compliance status, audience readiness, and activity streams"
    >
      {/* Top action row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h2 className="text-base font-bold text-slate-800">Operational Readiness</h2>
          <p className="text-xs text-slate-500">All data fetched directly from live PostgreSQL/SQLite database.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchStats}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Sync Stats</span>
          </button>
          <Link
            to="/leads"
            className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-white bg-navy-800 hover:bg-navy-900 rounded-lg shadow-sm transition"
          >
            <Users className="w-3.5 h-3.5" />
            <span>Manage Leads</span>
          </Link>
          <Link
            to="/discovery"
            className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-white bg-cyan-600 hover:bg-cyan-500 rounded-lg shadow-sm transition"
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Discovery Engine</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-semibold text-slate-500 leading-tight">{kpi.label}</span>
                <div className={`p-1.5 rounded-lg ${kpi.bg} ${kpi.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <p className="text-2xl font-bold text-slate-900">{kpi.value}</p>
            </div>
          );
        })}
      </div>

      {/* Main Grid: Sector distribution & Regional readiness */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sector Distribution */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Sector Segmentation</h3>
              <p className="text-xs text-slate-500">Categorized by Rule-based / RAG Lead Classifier</p>
            </div>
            <Link to="/leads" className="text-xs font-semibold text-cyan-600 hover:text-cyan-700 flex items-center gap-1">
              <span>View all</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3.5">
            {stats?.sector_distribution?.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No leads classified yet.</p>
            ) : (
              stats?.sector_distribution?.map((item) => {
                const total = stats.total_leads || 1;
                const percentage = Math.round((item.count / total) * 100);
                return (
                  <div key={item.sector}>
                    <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                      <span>{item.sector}</span>
                      <span className="font-semibold text-slate-900">{item.count} leads ({percentage}%)</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full transition-all duration-500" 
                        style={{ width: `${Math.max(percentage, 4)}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Regional Footprint */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-1">Regional Distribution</h3>
          <p className="text-xs text-slate-500 mb-4">Geographic audience concentration</p>

          <div className="space-y-3">
            {stats?.region_distribution?.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No regional data recorded.</p>
            ) : (
              stats?.region_distribution?.map((reg) => (
                <div key={reg.region} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-xs font-medium text-slate-700">{reg.region}</span>
                  <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                    {reg.count}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Two columns: Recent Leads & Recent Audit Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Leads */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Recent Lead Influx</h3>
              <p className="text-xs text-slate-500">Latest discovered & uploaded contacts</p>
            </div>
            <Link to="/leads" className="text-xs font-semibold text-cyan-600 hover:text-cyan-700">
              Go to Leads Table
            </Link>
          </div>

          <div className="divide-y divide-slate-100">
            {stats?.recent_leads?.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No leads available.</p>
            ) : (
              stats?.recent_leads?.map((lead) => (
                <div key={lead.id} className="py-3 flex items-center justify-between">
                  <div className="overflow-hidden pr-3">
                    <p className="text-xs font-bold text-slate-900 truncate">{lead.contact_name}</p>
                    <p className="text-[11px] text-slate-500 truncate">{lead.company_name} • {lead.email}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      {lead.sector}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      lead.email_verification_status === 'valid'
                        ? 'bg-emerald-100 text-emerald-800'
                        : lead.email_verification_status === 'invalid'
                        ? 'bg-rose-100 text-rose-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}>
                      {lead.email_verification_status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Activity Audit */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Compliance Audit Trail</h3>
              <p className="text-xs text-slate-500">Immutable ledger of platform operations</p>
            </div>
            <Link to="/audit-logs" className="text-xs font-semibold text-cyan-600 hover:text-cyan-700">
              Full Logs
            </Link>
          </div>

          <div className="space-y-3">
            {stats?.recent_activities?.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No activity entries recorded.</p>
            ) : (
              stats?.recent_activities?.slice(0, 5).map((act) => (
                <div key={act.id} className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex items-start justify-between gap-3">
                  <div className="overflow-hidden">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-navy-100 text-navy-800 font-mono">
                        {act.action}
                      </span>
                      <span className="text-[11px] text-slate-600 font-medium truncate">{act.actor}</span>
                    </div>
                    <p className="text-xs text-slate-700 mt-1 truncate">{act.details || 'Operational action logged'}</p>
                  </div>
                  <span className="text-[10px] text-slate-400 shrink-0 whitespace-nowrap">
                    {new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

