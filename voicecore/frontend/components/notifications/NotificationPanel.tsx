'use client';

import { useState } from 'react';
import { Bell, AlertTriangle, Phone, Target, CreditCard, BarChart3, Check, X, Loader2 } from 'lucide-react';

interface Notification {
  id: number;
  event_type: string;
  channel: string;
  subject: string;
  content: string;
  status: string;
  created_at: string;
  read: boolean;
  metadata?: any;
}

interface NotificationPanelProps {
  notifications: Notification[];
  onMarkAsRead: (id: number) => void;
  onMarkAllAsRead: () => void;
}

export default function NotificationPanel({
  notifications,
  onMarkAsRead,
  onMarkAllAsRead,
}: NotificationPanelProps) {
  const [filter, setFilter] = useState<string>('all');
  const [loading, setLoading] = useState<number | null>(null);

  const filteredNotifications = notifications.filter((n) => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !n.read;
    return n.event_type === filter;
  });

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'angry_customer':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'missed_call':
        return <Phone className="w-5 h-5 text-amber-500" />;
      case 'hot_lead':
        return <Target className="w-5 h-5 text-green-500" />;
      case 'payment_failed':
      case 'payment_issue':
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
      case 'emergency':
        return 'border-l-red-500';
      case 'missed_call':
        return 'border-l-amber-500';
      case 'hot_lead':
        return 'border-l-green-500';
      case 'payment_failed':
      case 'payment_issue':
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

  const handleMarkAsRead = async (id: number) => {
    setLoading(id);
    try {
      await onMarkAsRead(id);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Notifications</h2>
        {notifications.some((n) => !n.read) && (
          <button
            onClick={onMarkAllAsRead}
            className="text-sm text-amber-500 hover:text-amber-400"
          >
            Mark all as read
          </button>
        )}
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2">
        {[
          { value: 'all', label: 'All' },
          { value: 'unread', label: 'Unread' },
          { value: 'angry_customer', label: 'Alerts' },
          { value: 'missed_call', label: 'Missed' },
          { value: 'daily_summary', label: 'Reports' },
        ].map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition ${
              filter === f.value
                ? 'bg-amber-500 text-zinc-950'
                : 'bg-zinc-800 text-zinc-400 hover:text-white'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {filteredNotifications.length === 0 ? (
        <div className="py-12 text-center">
          <Bell className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
          <p className="text-zinc-500">No notifications found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`bg-zinc-900 border border-zinc-800 rounded-lg p-4 border-l-4 ${getNotificationColor(
                notification.event_type
              )} ${!notification.read ? 'bg-zinc-800/30' : ''}`}
            >
              <div className="flex gap-4">
                <div className="flex-shrink-0 mt-1">
                  {getNotificationIcon(notification.event_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-medium text-white">
                        {notification.subject ||
                          notification.event_type.replace(/_/g, ' ')}
                      </p>
                      {notification.content && (
                        <p className="text-sm text-zinc-400 mt-1">
                          {notification.content}
                        </p>
                      )}
                    </div>
                    {!notification.read && (
                      <button
                        onClick={() => handleMarkAsRead(notification.id)}
                        disabled={loading === notification.id}
                        className="p-1 text-zinc-400 hover:text-white transition"
                        title="Mark as read"
                      >
                        {loading === notification.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Check className="w-4 h-4" />
                        )}
                      </button>
                    )}
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-xs text-zinc-500">
                    <span>{formatDate(notification.created_at)}</span>
                    <span className="uppercase">{notification.channel}</span>
                    <span
                      className={`px-2 py-0.5 rounded ${
                        notification.status === 'sent'
                          ? 'bg-green-500/20 text-green-400'
                          : notification.status === 'failed'
                          ? 'bg-red-500/20 text-red-400'
                          : 'bg-zinc-700 text-zinc-400'
                      }`}
                    >
                      {notification.status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
