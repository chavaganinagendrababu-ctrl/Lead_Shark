import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CheckCircle2, ShieldAlert, Layers, AlertCircle, ArrowLeft } from 'lucide-react';
import axios from 'axios';

export const Unsubscribe = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState('idle'); // idle, processing, success, error
  const [message, setMessage] = useState('');

  const handleConfirmUnsubscribe = async () => {
    if (!token) {
      setStatus('error');
      setMessage('Missing or invalid unsubscribe token.');
      return;
    }
    setStatus('processing');
    try {
      const res = await axios.post(`/unsubscribe/${token}`);
      setStatus('success');
      setMessage(res.data.message);
    } catch (err) {
      setStatus('error');
      setMessage(err.response?.data?.detail || 'Unable to process unsubscribe request. Token may be expired.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center items-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 border border-slate-200 text-center">
        <div className="w-12 h-12 bg-navy-900 rounded-xl mx-auto flex items-center justify-center text-cyan-400 mb-4 shadow-md">
          <Layers className="w-6 h-6" />
        </div>

        <h1 className="text-xl font-bold text-slate-900 mb-1">Lead Shark Communications</h1>
        <p className="text-xs text-slate-500 mb-6 uppercase tracking-wider font-semibold">
          Compliant Opt-Out & Suppression Portal
        </p>

        {status === 'idle' && (
          <div className="space-y-4">
            <p className="text-xs text-slate-600 leading-relaxed">
              We respect your communication preferences and privacy. Clicking below will immediately register your address on our <strong>Global Suppression List</strong>, preventing any future B2B correspondence.
            </p>
            <button
              onClick={handleConfirmUnsubscribe}
              className="w-full py-3 px-4 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition shadow-md"
            >
              Confirm Permanent Opt-Out
            </button>
          </div>
        )}

        {status === 'processing' && (
          <div className="py-8 space-y-3">
            <div className="w-8 h-8 border-3 border-rose-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-xs font-semibold text-slate-600">Registering suppression record...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-4 py-2">
            <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto text-emerald-600">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h2 className="text-base font-bold text-slate-900">Unsubscribe Confirmed</h2>
            <p className="text-xs text-slate-600 leading-relaxed">{message}</p>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-500">
              Reference: GDPR Article 17 Right to Erasure / CAN-SPAM Compliance Act
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-4 py-2">
            <div className="w-12 h-12 bg-rose-100 rounded-full flex items-center justify-center mx-auto text-rose-600">
              <AlertCircle className="w-7 h-7" />
            </div>
            <h2 className="text-base font-bold text-slate-900">Request Incomplete</h2>
            <p className="text-xs text-rose-600 leading-relaxed">{message}</p>
          </div>
        )}
      </div>
    </div>
  );
};
