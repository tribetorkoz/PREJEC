'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Bell,
  Mail,
  MessageSquare,
  Globe,
  Clock,
  Phone,
  Check,
  Loader2,
  ChevronRight,
  AlertTriangle,
  CreditCard,
  BarChart3,
  Target,
} from 'lucide-react';

interface Notification {
  id: number;
  event_type: string;
  channel: string;
  subject: string;
  content: string;
  status: string;
  created_at: string;
  read: boolean;
}

interface NotificationPreferences {
  id: number;
  email_angry_customer: boolean;
  sms_angry_customer: boolean;
  email_missed_call: boolean;
  email_daily_summary: boolean;
  email_weekly_report: boolean;
  webhook_url: string | null;
  webhook_events: string[];
  notification_email: string | null;
  notification_phone: string | null;
  timezone: string;
  daily_summary_time: string;
}

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState<'notifications' | 'settings'>('notifications');
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);
  const [testingSms, setTestingSms] = useState(false);

  const [prefsForm, setPrefsForm] = useState({
    email_angry_customer: true,
    sms_angry_customer: false,
    email_missed_call: true,
    email_daily_summary: true,
    email_weekly_report: true,
    notification_email: '',
    notification_phone: '',
    timezone: 'America/New_York',
    daily_summary_time: '08:00',
  });

  useEffect(() => {
    fetchNotifications();
    fetchPreferences();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/v1/notifications?limit=50');
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      }
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPreferences = async () => {
    try {
      const response = await fetch('/api/v1/notifications/preferences');
      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
        setPrefsForm({
          email_angry_customer: data.email_angry_customer,
          sms_angry_customer: data.sms_angry_customer,
          email_missed_call: data.email_missed_call,
          email_daily_summary: data.email_daily_summary,
          email_weekly_report: data.email_weekly_report,
          notification_email: data.notification_email || '',
          notification_phone: data.notification_phone || '',
          timezone: data.timezone,
          daily_summary_time: data.daily_summary_time,
        });
      }
    } catch (err) {
      console.error('Failed to fetch preferences:', err);
    }
  };

  const savePreferences = async () => {
    setSaving(true);
    setSaveSuccess(false);
    try {
      const response = await fetch('/api/v1/notifications/preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(prefsForm),
      });
      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Failed to save preferences:', err);
    } finally {
      setSaving(false);
    }
  };

  const sendTestEmail = async () => {
    setTestingEmail(true);
    try {
      const response = await fetch('/api/v1/notifications/preferences/test-email', {
        method: 'POST',
      });
      const data = await response.json();
      alert(data.message || data.error);
    } catch (err) {
      console.error('Failed to send test email:', err);
    } finally {
      setTestingEmail(false);
    }
  };

  const sendTestSms = async () => {
    if (!prefsForm.notification_phone) {
      alert('Please add a phone number first');
      return;
    }
    setTestingSms(true);
    try {
      const response = await fetch('/api/v1/notifications/preferences/test-sms', {
        method: 'POST',
      });
      const data = await response.json();
      alert(data.message || data.error);
    } catch (err) {
      console.error('Failed to send test SMS:', err);
    } finally {
      setTestingSms(false);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await fetch(`/api/v1/notifications/${id}/read`, { method: 'POST' });
      setNotifications(notifications.map((n) => (n.id === id ? { ...n, read: true } : n)));
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'angry_customer':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'missed_call':
        return <Phone className="w-5 h-5 text-amber-500" />;
      case 'hot_lead':
        return <Target className="w-5 h-5 text-green-500" />;
      case 'payment_failed':
        return <CreditCard className="w-5 h-5 text-orange-500" />;
      case 'daily_summary':
      case 'weekly_report':
        return <BarChart3 className="w-5 h-5 text-blue-500" />;
      default:
        return <Bell className="w-5 h-5 text-zinc-400" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'angry_customer':
        return 'border-l-red-500';
      case 'missed_call':
        return 'border-l-amber-500';
      case 'hot_lead':
        return 'border-l-green-500';
      case 'payment_failed':
        return 'border-l-orange-500';
      default:
        return 'border-l-zinc-600';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="border-b border-zinc-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-zinc-400 hover:text-white">
                Dashboard
              </Link>
              <ChevronRight className="w-4 h-4 text-zinc-600" />
              <span className="text-white font-medium">Notifications</span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-4xl">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center">
            <Bell className="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Notifications</h1>
            <p className="text-zinc-400">Manage your alerts and notification preferences</p>
          </div>
        </div>

        <div className="flex gap-1 mb-6 bg-zinc-900 p-1 rounded-lg w-fit">
          <button
            onClick={() => setActiveTab('notifications')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              activeTab === 'notifications'
                ? 'bg-amber-500 text-zinc-950'
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            Notifications
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              activeTab === 'settings'
                ? 'bg-amber-500 text-zinc-950'
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            Settings
          </button>
        </div>

        {activeTab === 'notifications' && (
          <div className="space-y-4">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
              </div>
            ) : notifications.length === 0 ? (
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-12 text-center">
                <Bell className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">No notifications yet</h3>
                <p className="text-zinc-500">
                  You'll see alerts here when your AI receptionist handles calls
                </p>
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`bg-zinc-900 border border-zinc-800 rounded-xl p-4 border-l-4 ${
                    getNotificationColor(notification.event_type)
                  } ${!notification.read ? 'bg-zinc-800/30' : ''}`}
                >
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 mt-1">{getNotificationIcon(notification.event_type)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="font-medium text-white">
                            {notification.subject || notification.event_type.replace(/_/g, ' ')}
                          </p>
                          {notification.content && (
                            <p className="text-sm text-zinc-400 mt-1">{notification.content}</p>
                          )}
                        </div>
                        {!notification.read && (
                          <button
                            onClick={() => markAsRead(notification.id)}
                            className="p-1 text-zinc-400 hover:text-white transition"
                            title="Mark as read"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      <div className="flex items-center gap-4 mt-2 text-xs text-zinc-500">
                        <span>{formatDate(notification.created_at)}</span>
                        <span className="uppercase">{notification.channel}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-6">
            <h3 className="text-lg font-semibold text-white">Email Notifications</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-zinc-400" />
                  <div>
                    <p className="text-white">Angry customer alerts</p>
                    <p className="text-zinc-500 text-sm">Get notified immediately when a customer is upset</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={prefsForm.email_angry_customer}
                    onChange={(e) => setPrefsForm({ ...prefsForm, email_angry_customer: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-zinc-700 peer-focus:ring-2 peer-focus:ring-amber-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-zinc-400" />
                  <div>
                    <p className="text-white">Missed call alerts</p>
                    <p className="text-zinc-500 text-sm">Email me when a call is missed</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={prefsForm.email_missed_call}
                    onChange={(e) => setPrefsForm({ ...prefsForm, email_missed_call: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-zinc-700 peer-focus:ring-2 peer-focus:ring-amber-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-5 h-5 text-zinc-400" />
                  <div>
                    <p className="text-white">Daily summary</p>
                    <p className="text-zinc-500 text-sm">Receive daily call statistics</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={prefsForm.email_daily_summary}
                    onChange={(e) => setPrefsForm({ ...prefsForm, email_daily_summary: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-zinc-700 peer-focus:ring-2 peer-focus:ring-amber-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-5 h-5 text-zinc-400" />
                  <div>
                    <p className="text-white">Weekly report</p>
                    <p className="text-zinc-500 text-sm">Receive weekly analytics every Monday</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={prefsForm.email_weekly_report}
                    onChange={(e) => setPrefsForm({ ...prefsForm, email_weekly_report: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-zinc-700 peer-focus:ring-2 peer-focus:ring-amber-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                </label>
              </div>
            </div>

            <hr className="border-zinc-800" />

            <h3 className="text-lg font-semibold text-white">SMS Notifications</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <MessageSquare className="w-5 h-5 text-zinc-400" />
                  <div>
                    <p className="text-white">SMS alerts for angry customers</p>
                    <p className="text-zinc-500 text-sm">Get text messages for critical alerts</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={prefsForm.sms_angry_customer}
                    onChange={(e) => setPrefsForm({ ...prefsForm, sms_angry_customer: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-zinc-700 peer-focus:ring-2 peer-focus:ring-amber-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">
                  SMS Phone Number
                </label>
                <input
                  type="tel"
                  value={prefsForm.notification_phone}
                  onChange={(e) => setPrefsForm({ ...prefsForm, notification_phone: e.target.value })}
                  placeholder="+1 (555) 123-4567"
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <button
                onClick={sendTestSms}
                disabled={testingSms || !prefsForm.notification_phone}
                className="flex items-center gap-2 px-4 py-2 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 disabled:opacity-50 transition"
              >
                {testingSms ? <Loader2 className="w-4 h-4 animate-spin" /> : <MessageSquare className="w-4 h-4" />}
                Send Test SMS
              </button>
            </div>

            <hr className="border-zinc-800" />

            <h3 className="text-lg font-semibold text-white">Delivery Settings</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">
                  Timezone
                </label>
                <select
                  value={prefsForm.timezone}
                  onChange={(e) => setPrefsForm({ ...prefsForm, timezone: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  <option value="America/New_York">Eastern Time</option>
                  <option value="America/Chicago">Central Time</option>
                  <option value="America/Denver">Mountain Time</option>
                  <option value="America/Los_Angeles">Pacific Time</option>
                  <option value="Europe/London">London</option>
                  <option value="Europe/Paris">Paris</option>
                  <option value="Asia/Dubai">Dubai</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">
                  Daily Summary Time
                </label>
                <input
                  type="time"
                  value={prefsForm.daily_summary_time}
                  onChange={(e) => setPrefsForm({ ...prefsForm, daily_summary_time: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>
            </div>

            <hr className="border-zinc-800" />

            <h3 className="text-lg font-semibold text-white">Custom Notification Email</h3>
            
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Notification Email (optional)
              </label>
              <input
                type="email"
                value={prefsForm.notification_email}
                onChange={(e) => setPrefsForm({ ...prefsForm, notification_email: e.target.value })}
                placeholder="notifications@yourcompany.com"
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
              />
              <p className="mt-1 text-xs text-zinc-500">
                Leave empty to use your account email
              </p>
            </div>

            <button
              onClick={sendTestEmail}
              disabled={testingEmail}
              className="flex items-center gap-2 px-4 py-2 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 disabled:opacity-50 transition"
            >
              {testingEmail ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />}
              Send Test Email
            </button>

            <div className="flex items-center gap-4 pt-4">
              <button
                onClick={savePreferences}
                disabled={saving}
                className="flex items-center gap-2 px-6 py-3 bg-amber-500 text-zinc-950 font-semibold rounded-lg hover:bg-amber-400 disabled:opacity-50 transition"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Saving...
                  </>
                ) : saveSuccess ? (
                  <>
                    <Check className="w-5 h-5" />
                    Saved!
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
