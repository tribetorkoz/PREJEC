'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  LayoutDashboard, Users, Bot, Phone, DollarSign, 
  Settings, FileText, LogOut, Menu, X, Bell,
  TrendingUp, AlertCircle, Globe, Database, Zap,
  BarChart3, Link2, Brain, Shield, Key, FileBarChart,
  Building2, Activity
} from 'lucide-react';

const navItems = [
  { href: '/super-admin', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/super-admin/clients', label: 'Clients', icon: Users },
  { href: '/super-admin/agents', label: 'Agents', icon: Bot },
  { href: '/super-admin/calls', label: 'Calls', icon: Phone },
  { href: '/super-admin/customers', label: 'Customers', icon: Users },
  { href: '/super-admin/revenue', label: 'Revenue', icon: DollarSign },
  { href: '/super-admin/platform', label: 'Platform', icon: Activity },
  { href: '/super-admin/providers', label: 'Providers', icon: Zap },
  { href: '/super-admin/verticals', label: 'Verticals', icon: Globe },
  { href: '/super-admin/integrations', label: 'Integrations', icon: Link2 },
  { href: '/super-admin/intelligence', label: 'Intelligence', icon: Brain },
  { href: '/super-admin/roi', label: 'ROI Calculator', icon: BarChart3 },
  { href: '/super-admin/webhooks', label: 'Webhooks', icon: Zap },
  { href: '/super-admin/api-keys', label: 'API Keys', icon: Key },
  { href: '/super-admin/whitelabel', label: 'White-label', icon: Building2 },
  { href: '/super-admin/reports', label: 'Reports', icon: FileBarChart },
  { href: '/super-admin/settings', label: 'Settings', icon: Settings },
  { href: '/super-admin/logs', label: 'Audit Logs', icon: FileText },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [adminUser, setAdminUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (pathname === '/super-admin/login') {
      setLoading(false);
      return;
    }
    
    const token = localStorage.getItem('admin_token');
    const user = localStorage.getItem('admin_user');
    
    if (!token || !user) {
      router.push('/super-admin/login');
      return;
    }
    
    try {
      setAdminUser(JSON.parse(user));
    } catch {
      router.push('/super-admin/login');
      return;
    }
    setLoading(false);
  }, [router, pathname]);

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    router.push('/super-admin/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  if (pathname === '/super-admin/login') {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-zinc-950 flex">
      <aside 
        className={`${sidebarOpen ? 'w-72' : 'w-20'} bg-zinc-900 border-r border-zinc-800 transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          {sidebarOpen && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-zinc-950" />
              </div>
              <span className="font-bold text-white">VoiceCore</span>
            </div>
          )}
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-amber-500/10 text-amber-500' 
                    : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
                }`}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-zinc-800">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 w-full text-zinc-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-zinc-900 border-b border-zinc-800 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <h1 className="text-lg font-semibold text-white">
              {navItems.find(item => item.href === pathname)?.label || 'Admin'}
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-zinc-700 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {adminUser?.name?.charAt(0) || 'A'}
                </span>
              </div>
              {sidebarOpen && (
                <div className="text-sm">
                  <p className="text-white font-medium">{adminUser?.name}</p>
                  <p className="text-zinc-500 text-xs">{adminUser?.email}</p>
                </div>
              )}
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
