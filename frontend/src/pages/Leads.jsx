import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Upload, 
  Download, 
  Search, 
  Filter, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  HelpCircle, 
  Trash2, 
  Edit3, 
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  FileSpreadsheet,
  Check,
  X
} from 'lucide-react';
import api from '../services/api';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { useAuth } from '../context/AuthContext';

const SECTORS = [
  'All',
  'Information Technology',
  'Healthcare',
  'Education',
  'Finance',
  'Manufacturing',
  'Retail',
  'Real Estate',
  'Other'
];

const STATUSES = ['All', 'new', 'pending_review', 'approved', 'rejected'];
const VERIFICATIONS = ['All', 'valid', 'invalid', 'risky', 'unknown'];

export const Leads = () => {
  const { role, isReviewer, isAdmin } = useAuth();
  const [leads, setLeads] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size] = useState(10);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [sector, setSector] = useState('All');
  const [leadStatus, setLeadStatus] = useState('All');
  const [verificationStatus, setVerificationStatus] = useState('All');

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [importSummary, setImportSummary] = useState(null);
  const [importing, setImporting] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [formError, setFormError] = useState('');

  // Form State
  const [formData, setFormData] = useState({
    company_name: '',
    contact_name: '',
    job_title: '',
    email: '',
    phone: '',
    website: '',
    sector: 'Information Technology',
    region: 'North America',
    lawful_basis_note: 'Legitimate interest for B2B commercial outreach'
  });

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        size,
        search: search || undefined,
        sector: sector !== 'All' ? sector : undefined,
        lead_status: leadStatus !== 'All' ? leadStatus : undefined,
        verification_status: verificationStatus !== 'All' ? verificationStatus : undefined,
      };
      const res = await api.get('/leads', { params });
      setLeads(res.data.items);
      setTotal(res.data.total);
      setPages(res.data.pages);
    } catch (err) {
      console.error('Error fetching leads:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, [page, sector, leadStatus, verificationStatus]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLeads();
  };

  const handleCreateLead = async (e) => {
    e.preventDefault();
    setFormError('');
    setActionLoading(true);
    try {
      await api.post('/leads', formData);
      setShowAddModal(false);
      resetForm();
      fetchLeads();
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to create lead.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateLead = async (e) => {
    e.preventDefault();
    setFormError('');
    setActionLoading(true);
    try {
      await api.put(`/leads/${selectedLead.id}`, formData);
      setShowEditModal(false);
      resetForm();
      fetchLeads();
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to update lead.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteLead = async (id) => {
    if (!window.confirm('Are you sure you want to delete this lead? Global suppression protections will remain intact.')) {
      return;
    }
    try {
      await api.delete(`/leads/${id}`);
      fetchLeads();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete lead.');
    }
  };

  const handleVerifyEmail = async (id) => {
    try {
      const res = await api.post(`/leads/${id}/verify`);
      alert(`Verification Result for ${res.data.email}:\nStatus: ${res.data.status.toUpperCase()}\nDetails: ${res.data.details}`);
      fetchLeads();
    } catch (err) {
      alert(err.response?.data?.detail || 'Verification request failed.');
    }
  };

  const handleClassify = async (id) => {
    try {
      const res = await api.post(`/leads/${id}/classify`);
      alert(`Classified into sector: ${res.data.sector}\nConfidence: ${Math.round(res.data.classification_confidence * 100)}%\nReason: ${res.data.classification_reason}`);
      fetchLeads();
    } catch (err) {
      alert('Classification failed.');
    }
  };

  const handleStatusChange = async (lead, newStatus) => {
    try {
      await api.put(`/leads/${lead.id}`, { lead_status: newStatus });
      fetchLeads();
    } catch (err) {
      alert('Failed to update lead status');
    }
  };

  const handleExportCSV = async () => {
    try {
      const res = await api.get('/leads/export', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `leadshark_export_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to export CSV');
    }
  };

  const handleCSVUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImporting(true);
    setImportSummary(null);
    const data = new FormData();
    data.append('file', file);
    try {
      const res = await api.post('/leads/import', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setImportSummary(res.data);
      fetchLeads();
    } catch (err) {
      alert(err.response?.data?.detail || 'CSV upload failed');
    } finally {
      setImporting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      company_name: '',
      contact_name: '',
      job_title: '',
      email: '',
      phone: '',
      website: '',
      sector: 'Information Technology',
      region: 'North America',
      lawful_basis_note: 'Legitimate interest for B2B commercial outreach'
    });
    setFormError('');
    setSelectedLead(null);
  };

  const openEditModal = (lead) => {
    setSelectedLead(lead);
    setFormData({
      company_name: lead.company_name,
      contact_name: lead.contact_name,
      job_title: lead.job_title || '',
      email: lead.email,
      phone: lead.phone || '',
      website: lead.website || '',
      sector: lead.sector || 'Other',
      region: lead.region || 'North America',
      lawful_basis_note: lead.lawful_basis_note || ''
    });
    setShowEditModal(true);
  };

  const getVerificationBadge = (status) => {
    switch (status) {
      case 'valid':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            <span>Valid (MX Confirmed)</span>
          </span>
        );
      case 'risky':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
            <AlertTriangle className="w-3 h-3 text-amber-600" />
            <span>Risky (Role Mailbox)</span>
          </span>
        );
      case 'invalid':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800">
            <XCircle className="w-3 h-3 text-rose-600" />
            <span>Invalid Email</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700">
            <HelpCircle className="w-3 h-3 text-slate-500" />
            <span>Unverified</span>
          </span>
        );
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase">Approved</span>;
      case 'rejected':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200 uppercase">Rejected</span>;
      case 'pending_review':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 uppercase">Pending Review</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200 uppercase">New</span>;
    }
  };

  return (
    <DashboardLayout 
      title="Lead Management" 
      subtitle="Staged prospect data, email verification, sector classification, and approval workflows"
    >
      {/* Top Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <form onSubmit={handleSearch} className="flex-1 flex items-center gap-2 max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search company, contact name, email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
          <button type="submit" className="px-3 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg text-xs font-semibold">
            Search
          </button>
        </form>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg shadow-sm transition"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => setShowImportModal(true)}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg shadow-sm transition"
          >
            <Upload className="w-3.5 h-3.5 text-slate-500" />
            <span>Import CSV</span>
          </button>
          <button
            onClick={() => { resetForm(); setShowAddModal(true); }}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-white bg-cyan-600 hover:bg-cyan-500 rounded-lg shadow-sm transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Lead</span>
          </button>
        </div>
      </div>

      {/* Filter Row */}
      <div className="flex flex-wrap items-center gap-3 bg-white p-3.5 rounded-xl border border-slate-200 text-xs shadow-sm">
        <div className="flex items-center gap-1.5 text-slate-500 font-semibold uppercase text-[10px] tracking-wider mr-2">
          <Filter className="w-3.5 h-3.5" />
          <span>Filters</span>
        </div>

        <div>
          <select 
            value={sector} 
            onChange={(e) => { setSector(e.target.value); setPage(1); }}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-700 focus:outline-none"
          >
            {SECTORS.map(s => <option key={s} value={s}>Sector: {s}</option>)}
          </select>
        </div>

        <div>
          <select 
            value={leadStatus} 
            onChange={(e) => { setLeadStatus(e.target.value); setPage(1); }}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-700 focus:outline-none"
          >
            {STATUSES.map(s => <option key={s} value={s}>Approval: {s}</option>)}
          </select>
        </div>

        <div>
          <select 
            value={verificationStatus} 
            onChange={(e) => { setVerificationStatus(e.target.value); setPage(1); }}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-700 focus:outline-none"
          >
            {VERIFICATIONS.map(s => <option key={s} value={s}>Verification: {s}</option>)}
          </select>
        </div>

        <div className="ml-auto text-slate-500 text-xs font-medium">
          Showing <span className="font-bold text-slate-800">{leads.length}</span> of <span className="font-bold text-slate-800">{total}</span> leads
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">Company & Contact</th>
                <th className="py-3 px-4">Professional Email</th>
                <th className="py-3 px-4">Sector & Region</th>
                <th className="py-3 px-4">Email Verification</th>
                <th className="py-3 px-4">Compliance Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <div className="flex justify-center items-center gap-2">
                      <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                      <span>Loading lead repository...</span>
                    </div>
                  </td>
                </tr>
              ) : leads.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    No leads found matching current query or filters.
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 px-4">
                      <p className="font-bold text-slate-900">{lead.company_name}</p>
                      <p className="text-slate-500 text-[11px]">{lead.contact_name} {lead.job_title ? `• ${lead.job_title}` : ''}</p>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-slate-700">{lead.email}</span>
                      {lead.phone && <p className="text-[10px] text-slate-400">{lead.phone}</p>}
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-800 text-[10px] font-semibold">
                        {lead.sector}
                      </span>
                      {lead.region && <p className="text-[10px] text-slate-400 mt-0.5">{lead.region}</p>}
                    </td>
                    <td className="py-3 px-4">
                      {getVerificationBadge(lead.email_verification_status)}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-1.5">
                        {getStatusBadge(lead.lead_status)}
                        {isReviewer && (
                          <div className="flex items-center gap-1 ml-1">
                            {lead.lead_status !== 'approved' && (
                              <button
                                onClick={() => handleStatusChange(lead, 'approved')}
                                title="Approve Lead"
                                className="p-1 rounded bg-emerald-50 text-emerald-600 hover:bg-emerald-100"
                              >
                                <Check className="w-3 h-3" />
                              </button>
                            )}
                            {lead.lead_status !== 'rejected' && (
                              <button
                                onClick={() => handleStatusChange(lead, 'rejected')}
                                title="Reject Lead"
                                className="p-1 rounded bg-rose-50 text-rose-600 hover:bg-rose-100"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <div className="inline-flex items-center gap-1.5">
                        <button
                          onClick={() => handleVerifyEmail(lead.id)}
                          title="Run DNS/MX & Syntax Email Verification"
                          className="px-2 py-1 bg-slate-100 hover:bg-cyan-50 hover:text-cyan-700 text-slate-600 rounded text-[11px] font-semibold transition"
                        >
                          Verify MX
                        </button>
                        <button
                          onClick={() => handleClassify(lead.id)}
                          title="Run Sector Classification"
                          className="px-2 py-1 bg-slate-100 hover:bg-blue-50 hover:text-blue-700 text-slate-600 rounded text-[11px] font-semibold transition"
                        >
                          <Sparkles className="w-3 h-3 inline mr-0.5 text-blue-500" />
                          Classify
                        </button>
                        <button
                          onClick={() => openEditModal(lead)}
                          title="Edit Lead"
                          className="p-1 text-slate-400 hover:text-slate-700 rounded transition"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        {isReviewer && (
                          <button
                            onClick={() => handleDeleteLead(lead.id)}
                            title="Delete Lead"
                            className="p-1 text-slate-400 hover:text-rose-600 rounded transition"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
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
            Page <span className="font-bold text-slate-800">{page}</span> of <span className="font-bold text-slate-800">{pages}</span>
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
              onClick={() => setPage(p => Math.min(pages, p + 1))}
              disabled={page === pages}
              className="p-1.5 rounded border border-slate-200 bg-white text-slate-600 disabled:opacity-40 hover:bg-slate-50"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Add / Edit Lead Modal */}
      {(showAddModal || showEditModal) && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200 animate-in fade-in duration-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">
              {showAddModal ? 'Add New Business Lead' : 'Edit Staged Lead'}
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Enter professional business contact information with compliant lawful basis.
            </p>

            {formError && (
              <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
                {formError}
              </div>
            )}

            <form onSubmit={showAddModal ? handleCreateLead : handleUpdateLead} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Company Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.company_name}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                    placeholder="e.g. Acme Cloud Corp"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Contact Full Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.contact_name}
                    onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                    placeholder="e.g. Jane Doe"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Professional Email *</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                    placeholder="name@company.com"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Job Title</label>
                  <input
                    type="text"
                    value={formData.job_title}
                    onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                    placeholder="e.g. VP Infrastructure"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Sector</label>
                  <select
                    value={formData.sector}
                    onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                  >
                    {SECTORS.filter(s => s !== 'All').map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Region</label>
                  <input
                    type="text"
                    value={formData.region}
                    onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                    placeholder="e.g. North America / Europe"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Lawful Basis (GDPR / Compliance Note)</label>
                <input
                  type="text"
                  value={formData.lawful_basis_note}
                  onChange={(e) => setFormData({ ...formData, lawful_basis_note: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div className="pt-3 flex justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => { setShowAddModal(false); setShowEditModal(false); }}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-2 bg-navy-800 hover:bg-navy-900 text-white rounded-lg font-semibold transition"
                >
                  {actionLoading ? 'Saving...' : showAddModal ? 'Save Lead' : 'Update Lead'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CSV Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-base font-bold text-slate-900">Import Business Leads (CSV)</h3>
              <button 
                onClick={() => { setShowImportModal(false); setImportSummary(null); }}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Upload a valid CSV file. Leads will be screened against global suppression, de-duplicated, and staged for email verification.
            </p>

            {/* Template Download pill */}
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg mb-4 text-xs text-blue-900 flex items-center justify-between">
              <div>
                <p className="font-semibold">Required columns: company_name, contact_name, email</p>
                <p className="text-[11px] text-blue-700">Optional: job_title, phone, website, sector, region</p>
              </div>
              <a
                href="data:text/csv;charset=utf-8,company_name,contact_name,job_title,email,sector,region%0AApex%20Systems,John%20Smith,CTO,john@apexsystems.example,Information%20Technology,North%20America"
                download="leadshark_template.csv"
                className="px-2.5 py-1 bg-white border border-blue-300 text-blue-800 rounded font-semibold text-[11px] hover:bg-blue-50 shrink-0"
              >
                Template.csv
              </a>
            </div>

            <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center bg-slate-50/50 hover:bg-slate-50 transition">
              <FileSpreadsheet className="w-10 h-10 text-cyan-600 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-800 mb-1">Select CSV file to process</p>
              <input
                type="file"
                accept=".csv"
                onChange={handleCSVUpload}
                disabled={importing}
                className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100 cursor-pointer"
              />
            </div>

            {importing && (
              <div className="mt-4 flex items-center justify-center gap-2 text-xs text-cyan-700 font-semibold">
                <div className="w-4 h-4 border-2 border-cyan-600 border-t-transparent rounded-full animate-spin"></div>
                <span>Parsing CSV, filtering suppressions & duplicates...</span>
              </div>
            )}

            {importSummary && (
              <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-2">
                <p className="font-bold text-slate-900">Import Batch Results:</p>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="p-2 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                    <span className="font-bold">{importSummary.imported}</span> Successfully Staged
                  </div>
                  <div className="p-2 rounded bg-amber-50 text-amber-800 border border-amber-200">
                    <span className="font-bold">{importSummary.duplicates}</span> Duplicates Skipped
                  </div>
                  <div className="p-2 rounded bg-rose-50 text-rose-800 border border-rose-200">
                    <span className="font-bold">{importSummary.suppressed}</span> Suppressed Globally
                  </div>
                  <div className="p-2 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    <span className="font-bold">{importSummary.invalid}</span> Invalid Formats
                  </div>
                </div>
              </div>
            )}

            <div className="mt-5 flex justify-end">
              <button
                onClick={() => { setShowImportModal(false); setImportSummary(null); }}
                className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-slate-900"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};
