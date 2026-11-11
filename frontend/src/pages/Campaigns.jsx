import React, { useState, useEffect } from 'react';
import { 
  Send, 
  Plus, 
  CheckCircle2, 
  Clock, 
  Pause, 
  Play, 
  Eye, 
  ShieldCheck, 
  AlertTriangle, 
  Edit3, 
  Users, 
  Check, 
  X,
  FileText
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
  'Real Estate'
];

export const Campaigns = () => {
  const { user, isReviewer, isAdmin } = useAuth();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [showEligibilityModal, setShowEligibilityModal] = useState(false);

  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [eligibilityData, setEligibilityData] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    body_template: '',
    sector: 'Information Technology',
    daily_limit: 50
  });

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const res = await api.get('/campaigns');
      setCampaigns(res.data);
    } catch (err) {
      console.error('Failed to load campaigns', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setActionLoading(true);
    try {
      await api.post('/campaigns', formData);
      setShowCreateModal(false);
      resetForm();
      fetchCampaigns();
    } catch (err) {
      setErrorMessage(err.response?.data?.detail || 'Failed to create campaign');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateCampaign = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setActionLoading(true);
    try {
      await api.put(`/campaigns/${selectedCampaign.id}`, formData);
      setShowEditModal(false);
      resetForm();
      fetchCampaigns();
    } catch (err) {
      setErrorMessage(err.response?.data?.detail || 'Failed to update campaign');
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = async (campaignId, action) => {
    const notes = prompt(`Enter ${action} notes (optional):`, `Campaign ${action} via dashboard.`);
    if (notes === null) return;
    try {
      await api.post(`/campaigns/${campaignId}/approve`, { action, notes });
      alert(`Campaign successfully ${action}d.`);
      fetchCampaigns();
    } catch (err) {
      alert(err.response?.data?.detail || `Failed to ${action} campaign`);
    }
  };

  const handlePauseToggle = async (campaignId) => {
    try {
      await api.post(`/campaigns/${campaignId}/pause`);
      fetchCampaigns();
    } catch (err) {
      alert('Failed to toggle pause status');
    }
  };

  const openPreview = async (campaign) => {
    try {
      setSelectedCampaign(campaign);
      const res = await api.get(`/campaigns/${campaign.id}/preview`);
      setPreviewData(res.data);
      setShowPreviewModal(true);
    } catch (err) {
      alert('Failed to generate campaign preview');
    }
  };

  const openEligibilityCheck = async (campaign) => {
    try {
      setSelectedCampaign(campaign);
      const res = await api.get(`/campaigns/${campaign.id}/eligibility`);
      setEligibilityData(res.data);
      setShowEligibilityModal(true);
    } catch (err) {
      alert('Failed to run eligibility audit');
    }
  };

  const openEdit = (campaign) => {
    setSelectedCampaign(campaign);
    setFormData({
      name: campaign.name,
      subject: campaign.subject,
      body_template: campaign.body_template,
      sector: campaign.sector || 'All',
      daily_limit: campaign.daily_limit || 50
    });
    setShowEditModal(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      subject: '',
      body_template: 'Hi {{first_name}},\n\nI noticed the impressive work {{company}} is delivering in {{sector}}.\n\nWe provide enterprise workflow modernization with guaranteed compliance.\n\nBest regards,\nYour Team',
      sector: 'Information Technology',
      daily_limit: 50
    });
    setErrorMessage('');
    setSelectedCampaign(null);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase">Approved</span>;
      case 'pending_approval':
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 uppercase">Pending Approval</span>;
      case 'paused':
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-300 uppercase">Paused</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200 uppercase">Draft</span>;
    }
  };

  return (
    <DashboardLayout
      title="Outreach Campaigns"
      subtitle="Template authoring, merge tag previews, four-eyes approval workflows, and eligibility validation"
    >
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h2 className="text-sm font-bold text-slate-800">Campaign Governance</h2>
          <p className="text-xs text-slate-500">
            Four-Eyes Principle: Campaign creators cannot approve their own outreach. Any template edit revokes approval.
          </p>
        </div>
        <button
          onClick={() => { resetForm(); setShowCreateModal(true); }}
          className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-cyan-600 hover:bg-cyan-500 rounded-lg shadow-sm transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Create Campaign</span>
        </button>
      </div>

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-16 text-center text-slate-400">Loading campaigns...</div>
        ) : campaigns.length === 0 ? (
          <div className="col-span-full py-16 text-center text-slate-400">
            No outreach campaigns created yet. Click "Create Campaign" to begin.
          </div>
        ) : (
          campaigns.map((camp) => {
            const isCreator = camp.created_by_id === user?.id;
            return (
              <div key={camp.id} className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between hover:border-slate-300 transition overflow-hidden">
                <div className="p-5">
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      {camp.sector}
                    </span>
                    {getStatusBadge(camp.status)}
                  </div>

                  <h3 className="text-base font-bold text-slate-900 mb-1 leading-snug">{camp.name}</h3>
                  <p className="text-xs text-slate-500 font-mono mb-3 truncate">
                    Subject: {camp.subject}
                  </p>

                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 text-xs text-slate-600 mb-4 line-clamp-3 whitespace-pre-wrap font-sans">
                    {camp.body_template}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-500 border-t border-slate-100 pt-3">
                    <div>
                      <span className="text-slate-400">Target Audience:</span>{' '}
                      <span className="font-bold text-slate-800">{camp.target_audience_count} leads</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Daily Cap:</span>{' '}
                      <span className="font-bold text-slate-800">{camp.daily_limit} / day</span>
                    </div>
                  </div>
                </div>

                {/* Card Actions Footer */}
                <div className="p-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => openPreview(camp)}
                      title="Preview rendered email with merge fields"
                      className="p-1.5 text-slate-600 hover:text-cyan-700 hover:bg-slate-200 rounded transition"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => openEligibilityCheck(camp)}
                      title="Check compliance eligibility count"
                      className="p-1.5 text-slate-600 hover:text-blue-700 hover:bg-slate-200 rounded transition"
                    >
                      <ShieldCheck className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => openEdit(camp)}
                      title="Edit campaign (will reset approval)"
                      className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-200 rounded transition"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {/* Pause / Resume */}
                    {(camp.status === 'approved' || camp.status === 'paused') && (
                      <button
                        onClick={() => handlePauseToggle(camp.id)}
                        className="px-2.5 py-1 text-[11px] font-semibold rounded bg-slate-200 text-slate-700 hover:bg-slate-300 transition"
                      >
                        {camp.status === 'paused' ? 'Resume' : 'Pause'}
                      </button>
                    )}

                    {/* Reviewer / Admin Approval Buttons */}
                    {isReviewer && camp.status !== 'approved' && (
                      <button
                        onClick={() => handleApprove(camp.id, 'approve')}
                        disabled={isCreator && !isAdmin}
                        title={isCreator && !isAdmin ? 'Creator cannot approve own campaign' : 'Approve campaign for sending'}
                        className="flex items-center gap-1 px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-[11px] shadow-sm disabled:opacity-40 transition"
                      >
                        <Check className="w-3 h-3" />
                        <span>Approve</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Create / Edit Campaign Modal */}
      {(showCreateModal || showEditModal) && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-xl w-full p-6 border border-slate-200 animate-in fade-in duration-200">
            <h3 className="text-base font-bold text-slate-900 mb-1">
              {showCreateModal ? 'Create Outreach Campaign' : 'Edit Outreach Campaign'}
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Configure messaging template. Note that any changes to an approved campaign will reset its approval status.
            </p>

            {errorMessage && (
              <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
                {errorMessage}
              </div>
            )}

            <form onSubmit={showCreateModal ? handleCreateCampaign : handleUpdateCampaign} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Campaign Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                  placeholder="e.g. Q4 Cloud Infrastructure Outreach"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Target Sector</label>
                  <select
                    value={formData.sector}
                    onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                  >
                    {SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Daily Cap</label>
                  <input
                    type="number"
                    min="1"
                    max="500"
                    value={formData.daily_limit}
                    onChange={(e) => setFormData({ ...formData, daily_limit: parseInt(e.target.value) || 50 })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Email Subject Line *</label>
                <input
                  type="text"
                  required
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                  placeholder="e.g. Streamlining infrastructure for {{company}}"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="font-semibold text-slate-700">Email Body Template *</label>
                  <div className="flex items-center gap-1 text-[10px] text-slate-500">
                    <span className="font-mono bg-slate-100 px-1 py-0.5 rounded">{'{{first_name}}'}</span>
                    <span className="font-mono bg-slate-100 px-1 py-0.5 rounded">{'{{company}}'}</span>
                    <span className="font-mono bg-slate-100 px-1 py-0.5 rounded">{'{{sector}}'}</span>
                  </div>
                </div>
                <textarea
                  rows={6}
                  required
                  value={formData.body_template}
                  onChange={(e) => setFormData({ ...formData, body_template: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500 font-sans"
                />
              </div>

              <div className="pt-3 flex justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => { setShowCreateModal(false); setShowEditModal(false); }}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-2 bg-navy-800 hover:bg-navy-900 text-white rounded-lg font-semibold transition"
                >
                  {actionLoading ? 'Saving...' : showCreateModal ? 'Submit for Review' : 'Save & Reset Approval'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Live Preview Modal */}
      {showPreviewModal && previewData && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-3 border-b border-slate-200 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Campaign Email Preview</h3>
                <p className="text-[11px] text-slate-500">Rendered with sample lead merge tags</p>
              </div>
              <button onClick={() => setShowPreviewModal(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>

            <div className="space-y-3 text-xs mb-4">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-slate-500 text-[11px]">To: <span className="font-mono text-slate-800 font-bold">{previewData.recipient_email}</span></p>
                <p className="text-slate-500 text-[11px] mt-0.5">Subject: <span className="font-semibold text-slate-900">{previewData.subject}</span></p>
              </div>

              <div className="p-4 bg-white rounded-lg border border-slate-200 whitespace-pre-wrap leading-relaxed text-slate-800">
                {previewData.rendered_body}
              </div>

              <div className="p-3 bg-cyan-50 border border-cyan-200 rounded-lg text-[11px] text-cyan-900">
                <p className="font-semibold">Cryptographic One-Click Unsubscribe Included:</p>
                <p className="font-mono text-[10px] text-cyan-800 truncate mt-1">{previewData.unsubscribe_url}</p>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setShowPreviewModal(false)}
                className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Compliance Eligibility Modal */}
      {showEligibilityModal && eligibilityData && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-3 border-b border-slate-200 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Audience Compliance Audit</h3>
                <p className="text-[11px] text-slate-500">7-Step Compliance Filter Breakdown</p>
              </div>
              <button onClick={() => setShowEligibilityModal(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>

            <div className="space-y-2.5 text-xs mb-5">
              <div className="flex justify-between p-3 rounded-lg bg-emerald-50 text-emerald-900 border border-emerald-200">
                <span className="font-semibold">Eligible Approved Audience</span>
                <span className="font-bold text-base">{eligibilityData.eligible_count}</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-rose-50 text-rose-800 border border-rose-200">
                <span>Suppressed Contacts Filtered Out</span>
                <span className="font-bold">{eligibilityData.suppressed_count}</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-200">
                <span>Unverified Email Addresses Filtered</span>
                <span className="font-bold">{eligibilityData.unverified_leads_count}</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-50 text-slate-700 border border-slate-200">
                <span>Pending Review Leads Filtered</span>
                <span className="font-bold">{eligibilityData.unapproved_leads_count}</span>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setShowEligibilityModal(false)}
                className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};

