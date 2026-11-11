import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Compass, 
  Send, 
  ShieldCheck, 
  BarChart3, 
  FileText, 
  LogOut,
  Shield,
  Layers
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar = () => {
  const { user, role, logout } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Leads Management', path: '/leads', icon: Users },
    { name: 'Discovery Engine', path: '/discovery', icon: Compass },
    { name: 'Campaigns', path: '/campaigns', icon: Send },
    { name: 'Compliance & Suppression', path: '/compliance', icon: ShieldCheck },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Audit Logs', path: '/audit-logs', icon: FileText, roles: ['admin', 'reviewer'] },
  ];

  const getRoleBadgeColor = (r) => {
    switch (r) {
      case 'admin':
        return 'bg-purple-900/60 text-purple-300 border-purple-700/50';
      case 'reviewer':
        return 'bg-blue-900/60 text-blue-300 border-blue-700/50';
      default:
        return 'bg-emerald-900/60 text-emerald-300 border-emerald-700/50';
    }
  };

  return (
    <aside className="w-64 bg-navy-950 text-slate-300 flex flex-col border-r border-slate-800 shrink-0 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-slate-800/80 bg-navy-900">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center text-white shadow-md shadow-cyan-900/30">
          <Layers className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
            LEAD <span className="text-cyan-400">SHARK</span>
          </span>
          <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Compliant Outreach</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 py-6 px-3 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          Enterprise Modules
        </div>
        {navItems.map((item) => {
          if (item.roles && !item.roles.includes(role) && role !== 'admin') {
            return null;
          }
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyan-600/20 text-cyan-300 border-l-4 border-cyan-400 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </div>

      {/* Compliance Notice */}
      <div className="mx-3 mb-4 p-3 rounded-lg bg-navy-900/80 border border-slate-800 text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5 font-semibold text-cyan-400 mb-1">
          <Shield className="w-3.5 h-3.5" />
          <span>Active Compliance Guard</span>
        </div>
        <p className="leading-relaxed text-slate-400">
          Global suppression filters and four-eyes review enforce GDPR/CAN-SPAM compliance.
        </p>
      </div>

      {/* User Footer */}
      <div className="p-4 border-t border-slate-800 bg-navy-900 flex items-center justify-between">
        <div className="overflow-hidden">
          <p className="text-xs font-semibold text-white truncate">{user?.full_name || 'Authorized User'}</p>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded border ${getRoleBadgeColor(role)}`}>
              {role}
            </span>
            <span className="text-[10px] text-slate-400 truncate">{user?.email}</span>
          </div>
        </div>
        <button
          onClick={logout}
          title="Sign out"
          className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
};
