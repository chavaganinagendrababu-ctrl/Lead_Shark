import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  PieChart, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  ShieldCheck, 
  Send, 
  Users,
  Info
} from 'lucide-react';
import api from '../services/api';
import { DashboardLayout } from '../layouts/DashboardLayout';

export const Analytics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/dashboard/stats');
        setStats(res.data);
      } catch (err) {
        console.error('Failed to load analytics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <DashboardLayout title="Analytics & Reporting" subtitle="Database metrics & compliance health">
        <div className="py-24 text-center text-slate-400">Loading intelligence data...</div>
      </DashboardLayout>
    );
  }

  const total = stats?.total_leads || 0;
  const verified = stats?.verified_leads || 0;
  const invalid = stats?.invalid_emails || 0;
  const pending = stats?.pending_review || 0;

  return (
    <DashboardLayout
      title="Analytics & Verification Reports"
      subtitle="Strict empirical database metrics; zero fabricated delivery or open rates"
    >
      {/* Empirical Data Banner */}
      <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-900 flex items-start gap-3">
        <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-bold">Empirical Database Truth Policy</p>
          <p className="text-blue-700 mt-0.5">
            Because Version 1 maintains email sending in Safe Mode, delivery rates, open rates, and replies are strictly reported as <span className="font-semibold">N/A (Sending Inactive)</span> to prevent fraudulent reporting.
          </p>
        </div>
      </div>

      {/* Primary Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500">Total Leads Ingested</span>
          <p className="text-3xl font-extrabold text-slate-900 mt-1">{total}</p>
          <p className="text-[11px] text-slate-400 mt-2">Across manual and CSV pipelines</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500">Verified Active Mailboxes</span>
          <p className="text-3xl font-extrabold text-emerald-600 mt-1">{verified}</p>
          <p className="text-[11px] text-emerald-700 mt-2">
            {total > 0 ? `${Math.round((verified / total) * 100)}% verification rate` : '0%'}
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500">Invalid / Disposable Flagged</span>
          <p className="text-3xl font-extrabold text-rose-600 mt-1">{invalid}</p>
          <p className="text-[11px] text-rose-700 mt-2">Prevented from contacting</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500">Global Suppressed Addresses</span>
          <p className="text-3xl font-extrabold text-purple-600 mt-1">{stats?.suppressed_leads || 0}</p>
          <p className="text-[11px] text-purple-700 mt-2">Zero-contact enforcement</p>
        </div>
      </div>

      {/* Grid: Verification Funnel & Sector Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Verification Status Breakdown */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-1">Email Verification Integrity Funnel</h3>
          <p className="text-xs text-slate-500 mb-5">DNS MX record confirmation and RFC syntax audits</p>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Valid (Deliverable MX Confirmed)</span>
                </span>
                <span className="font-bold text-slate-900">{verified} ({total > 0 ? Math.round((verified / total) * 100) : 0}%)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-emerald-500 h-2.5 rounded-full" style={{ width: `${total > 0 ? (verified / total) * 100 : 0}%` }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Pending Initial MX Check</span>
                </span>
                <span className="font-bold text-slate-900">{pending} ({total > 0 ? Math.round((pending / total) * 100) : 0}%)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-amber-400 h-2.5 rounded-full" style={{ width: `${total > 0 ? (pending / total) * 100 : 0}%` }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                <span className="flex items-center gap-1.5">
                  <XCircle className="w-3.5 h-3.5 text-rose-600" />
                  <span>Invalid / Disposable Rejections</span>
                </span>
                <span className="font-bold text-slate-900">{invalid} ({total > 0 ? Math.round((invalid / total) * 100) : 0}%)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-rose-500 h-2.5 rounded-full" style={{ width: `${total > 0 ? (invalid / total) * 100 : 0}%` }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Campaign Portfolio Overview */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-1">Campaign Approval Health</h3>
          <p className="text-xs text-slate-500 mb-5">Four-eyes approval pipeline status</p>

          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs font-semibold text-slate-500">Total Authored</span>
              <p className="text-2xl font-bold text-slate-800 mt-1">{stats?.total_campaigns || 0}</p>
            </div>
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
              <span className="text-xs font-semibold text-emerald-700">Approved by Reviewer</span>
              <p className="text-2xl font-bold text-emerald-800 mt-1">{stats?.active_campaigns || 0}</p>
            </div>
          </div>

          <div className="mt-6 p-4 rounded-xl bg-slate-50 border border-slate-100">
            <div className="flex items-center justify-between text-xs text-slate-600 mb-2">
              <span>Sending Infrastructure Status</span>
              <span className="font-bold text-amber-700 px-2 py-0.5 rounded bg-amber-100">Safe Mode (Simulated)</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Real SMTP/SendGrid dispatch is purposely locked pending enterprise MX warmup and domain DKIM/SPF alignment.
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};
