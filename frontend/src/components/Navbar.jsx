import React from 'react';
import { ShieldCheck, Activity, Terminal } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar = ({ title, subtitle }) => {
  const { user, role } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between shrink-0">
      <div>
        <h1 className="text-xl font-bold text-slate-800 tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500 font-medium">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Environment Tag */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>FastAPI Engine Online</span>
        </div>

        {/* Guard Mode */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
          <span>Sending Disabled (Version 1 Safe Mode)</span>
        </div>

        <div className="h-6 w-[1px] bg-slate-200"></div>

        {/* Current User Pill */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-navy-800 text-white font-bold text-xs flex items-center justify-center">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div className="text-left hidden md:block">
            <p className="text-xs font-bold text-slate-700 leading-none">{user?.full_name}</p>
            <p className="text-[10px] text-slate-400 capitalize">{role} Account</p>
          </div>
        </div>
      </div>
    </header>
  );
};
