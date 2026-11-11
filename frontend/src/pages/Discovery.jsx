import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  Play, 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertCircle,
  Database,
  Building,
  Layers,
  ArrowRight
} from 'lucide-react';
import api from '../services/api';
import { DashboardLayout } from '../layouts/DashboardLayout';

export const Discovery = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningJob, setRunningJob] = useState(false);
  const [sectorFilter, setSectorFilter] = useState('All');

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await api.get('/discovery/jobs');
      setJobs(res.data);
    } catch (err) {
      console.error('Failed to load discovery jobs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleRunDiscovery = async () => {
    try {
      setRunningJob(true);
      const res = await api.post('/discovery/jobs', {
        source_type: 'mock_partner_api',
        source_name: 'Permitted Public B2B Registry (Demo Sample)',
        sector_filter: sectorFilter,
        records_to_discover: 4
      });
      alert(`Discovery Completed!\nStaged: ${res.data.total_imported} leads\nRejected/Suppressed: ${res.data.total_rejected}`);
      fetchJobs();
    } catch (err) {
      alert(err.response?.data?.detail || 'Discovery run failed');
    } finally {
      setRunningJob(false);
    }
  };

  return (
    <DashboardLayout
      title="Discovery Engine"
      subtitle="Permitted directory connectors, discovery job history, and automated provenance tagging"
    >
      {/* Top Banner & Run Trigger */}
      <div className="bg-gradient-to-r from-navy-950 via-navy-900 to-navy-800 rounded-2xl p-6 text-white border border-slate-800 shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-900/60 text-cyan-300 border border-cyan-700/50 text-[11px] font-bold mb-3">
            <Compass className="w-3.5 h-3.5 text-cyan-400" />
            <span>Permitted B2B Source Adapters</span>
          </div>
          <h2 className="text-xl font-bold tracking-tight mb-2">
            Automated Prospect Discovery Pipeline
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed mb-5">
            Collect qualified business profiles from permitted commercial registries. Every discovered lead automatically receives timestamped provenance records, lawful basis documentation, and is scrubbed against the Global Suppression List.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleRunDiscovery}
              disabled={runningJob}
              className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-cyan-950/40 transition disabled:opacity-50"
            >
              {runningJob ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Running Ingestion...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Execute Discovery Job (Demo Registry)</span>
                </>
              )}
            </button>
            <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Strict compliance: Zero scraping, zero login bypassing.</span>
            </div>
          </div>
        </div>
      </div>

      {/* Discovery Pipeline Architecture Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center font-bold mb-3">
            1
          </div>
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1">Permitted API Connectors</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Standardized integration interfaces designed for Companies House, Dun & Bradstreet, and authorized CRM endpoints.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-8 h-8 rounded-lg bg-cyan-50 text-cyan-700 flex items-center justify-center font-bold mb-3">
            2
          </div>
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1">Deduplication & Screening</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Real-time screening against existing databases and the Global Suppression List prevents double contact and spam complaints.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold mb-3">
            3
          </div>
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1">Staged for Review</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            All newly discovered leads enter <code className="text-navy-900 font-semibold">pending_review</code> status and are never marked verified automatically.
          </p>
        </div>
      </div>

      {/* Discovery Jobs Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800">Discovery Job History</h3>
            <p className="text-xs text-slate-500">Audit trail of batch collection executions</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 rounded-full text-slate-700">
            {jobs.length} Runs Recorded
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">Job ID</th>
                <th className="py-3 px-4">Connector Source</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Discovered</th>
                <th className="py-3 px-4">Imported</th>
                <th className="py-3 px-4">Rejected / Suppressed</th>
                <th className="py-3 px-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">Loading jobs...</td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    No discovery jobs have been executed yet. Click "Execute Discovery Job" above to stage sample leads.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 px-4 font-mono font-bold text-slate-700">#{job.id}</td>
                    <td className="py-3 px-4">
                      <p className="font-semibold text-slate-900">{job.source_name || job.source_type}</p>
                      <p className="text-[10px] text-slate-400 capitalize">{job.source_type}</p>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-bold text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>{job.status}</span>
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-800">{job.total_discovered}</td>
                    <td className="py-3 px-4 font-bold text-emerald-600">+{job.total_imported}</td>
                    <td className="py-3 px-4 font-semibold text-rose-600">{job.total_rejected}</td>
                    <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardLayout>
  );
};

