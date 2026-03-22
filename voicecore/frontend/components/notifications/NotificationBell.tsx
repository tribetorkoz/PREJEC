'use client';

import { useState, useEffect, useRef } from 'react';
import { Bell, X, AlertTriangle, Phone, Target, CreditCard, BarChart3 } from 'lucide-react';
import NotificationPanel from './NotificationPanel';

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

export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/v1/notifications');
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await fetch(`/api/v1/notifications/${id}/read`, { method: 'POST' });
      setNotifications(
        notifications.map((n) =>
          n.id === id ? { ...n, read: true } : n
        )
      );
      setUnreadCount(Math.max(0, unreadCount - 1));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch('/api/v1/notifications/read-all', { method: 'POST' });
      setNotifications(notifications.map((n) => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'angry_customer':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'missed_call':
        return <Phone className="w-4 h-4 text-amber-500" />;
      case 'hot_lead':
        return <Target className="w-4 h-4 text-green-500" />;
      case 'payment_failed':
      case 'payment_issue':
        return <CreditCard className="w-4 h-4 text-orange-500" />;
      case 'daily_summary':
      case 'weekly_report':
        return <BarChart3 className="w-4 h-4 text-blue-500" />;
      default:
        return <Bell className="w-4 h-4 text-zinc-400" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'angry_customer':
      case 'emergency':
        return 'bg-red-500/10 border-red-500/20';
      case 'missed_call':
        return 'bg-amber-500/10 border-amber-500/20';
      case 'hot_lead':
        return 'bg-green-500/10 border-green-500/20';
      case 'payment_failed':
      case 'payment_issue':
        return 'bg-orange-500/10 border-orange-500/20';
      default:
        return 'bg-zinc-800 border-zinc-700';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-zinc-400 hover:text-white transition"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-zinc-900 border border-zinc-800 rounded-xl shadow-xl z-50 overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-zinc-800">
            <h3 className="font-semibold text-white">Notifications</h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-amber-500 hover:text-amber-400"
                >
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 text-zinc-400 hover:text-white transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center">
                <Bell className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
                <p className="text-zinc-500">No notifications yet</p>
              </div>
            ) : (
              notifications.map((notification) => (
                <button
                  key={notification.id}
                  onClick={() => markAsRead(notification.id)}
                  className={`w-full p-4 text-left border-b border-zinc-800 last:border-0 hover:bg-zinc-800/50 transition ${
                    !notification.read ? 'bg-zinc-800/30' : ''
                  } ${getNotificationColor(notification.event_type)}`}
                >
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 mt-1">
                      {getNotificationIcon(notification.event_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">
                        {notification.subject || notification.event_type.replace(/_/g, ' ')}
                      </p>
                      {notification.content && (
                        <p className="text-xs text-zinc-400 mt-1 line-clamp-2">
                          {notification.content}
                        </p>
                      )}
                      <p className="text-xs text-zinc-500 mt-1">
                        {formatTime(notification.created_at)}
                      </p>
                    </div>
                    {!notification.read && (
                      <div className="w-2 h-2 bg-amber-500 rounded-full flex-shrink-0 mt-2" />
                    )}
                  </div>
                </button>
              ))
            )}
          </div>

          <div className="p-3 border-t border-zinc-800">
            <a
              href="/dashboard/notifications"
              className="block text-center text-sm text-amber-500 hover:text-amber-400"
            >
              View all notifications
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
