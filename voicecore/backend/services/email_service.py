"""
Email Service — VoiceCore

SendGrid-based email service.
Every email has a specific template — no random strings in code.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import httpx

from config import settings

logger = logging.getLogger(__name__)


class DailySummaryStats:
    def __init__(self, data: dict):
        self.total_calls = data.get("total_calls", 0)
        self.total_duration = data.get("total_duration", 0)
        self.avg_sentiment = data.get("avg_sentiment", 0)
        self.resolved_rate = data.get("resolved_rate", 0)
        self.missed_calls = data.get("missed_calls", 0)
        self.appointments_booked = data.get("appointments_booked", 0)
        self.top_event = data.get("top_event", "Normal calls")
        self.sentiment_breakdown = data.get("sentiment_breakdown", {})


class WeeklyReport:
    def __init__(self, data: dict):
        self.total_calls = data.get("total_calls", 0)
        self.weekly_trend = data.get("weekly_trend", 0)
        self.compared_to_last_week = data.get("compared_to_last_week", 0)
        self.missed_calls = data.get("missed_calls", 0)
        self.appointments_booked = data.get("appointments_booked", 0)
        self.avg_sentiment = data.get("avg_sentiment", 0)
        self.top_event = data.get("top_event", "Normal calls")


class EmailService:
    
    def __init__(self):
        self.sendgrid_api_key = getattr(settings, "sendgrid_api_key", None)
        self.from_email = getattr(settings, "from_email", "noreply@voicecore.ai")
        self.from_name = "VoiceCore"
        self.base_url = getattr(settings, "base_url", "https://app.voicecore.ai")
    
    async def _send_via_sendgrid(
        self,
        to: str,
        subject: str,
        html: str,
        text: str,
        from_name: str = None,
    ) -> bool:
        if not self.sendgrid_api_key:
            logger.warning("SendGrid API key not configured")
            return await self._fallback_send(to, subject, html, text)
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.sendgrid_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": self.from_email, "name": from_name or self.from_name},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text},
                {"type": "text/html", "value": html},
            ],
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return await self._fallback_send(to, subject, html, text)
    
    async def _fallback_send(
        self, to: str, subject: str, html: str, text: str
    ) -> bool:
        logger.info(f"[EMAIL] To: {to}, Subject: {subject}")
        logger.debug(f"HTML content length: {len(html)}")
        return True
    
    def _render_template(self, template_name: str, context: dict) -> str:
        try:
            from jinja2 import Template
            import os
            
            template_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "email_templates",
                f"{template_name}.html",
            )
            
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()
                template = Template(template_content)
                return template.render(**context)
        except Exception as e:
            logger.warning(f"Template rendering failed: {e}")
        
        return self._get_default_template(template_name, context)
    
    def _get_default_template(self, template_name: str, context: dict) -> str:
        templates = {
            "welcome": self._welcome_template,
            "onboarding_complete": self._onboarding_complete_template,
            "angry_customer_alert": self._angry_customer_template,
            "daily_summary": self._daily_summary_template,
            "weekly_report": self._weekly_report_template,
            "missed_call": self._missed_call_template,
            "payment_failed": self._payment_failed_template,
            "day3_checkin": self._day3_checkin_template,
            "churn_risk": self._churn_risk_template,
        }
        
        template_func = templates.get(template_name, self._generic_template)
        return template_func(context)
    
    async def send_welcome_email(
        self, to_email: str, company_name: str, user_name: str
    ) -> bool:
        subject = f"Welcome to VoiceCore, {user_name}! Your AI receptionist is ready."
        
        context = {
            "user_name": user_name,
            "company_name": company_name,
            "onboarding_url": f"{self.base_url}/onboarding",
            "docs_url": f"{self.base_url}/docs",
            "video_url": "https://youtube.com/voicecore-demo",
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("welcome", context)
        text = f"""
Welcome to VoiceCore, {user_name}!

Your AI receptionist for {company_name} is ready to go.

Setup takes only 30 minutes:
{context['onboarding_url']}

Need help? Check our documentation:
{context['docs_url']}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_onboarding_completed_email(
        self, to_email: str, company_name: str, phone_number: str, agent_name: str
    ) -> bool:
        subject = f" {company_name} is now live on VoiceCore!"
        
        context = {
            "company_name": company_name,
            "phone_number": phone_number,
            "agent_name": agent_name,
            "dashboard_url": f"{self.base_url}/dashboard",
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("onboarding_complete", context)
        text = f"""
{company_name} is now live on VoiceCore!

Your AI receptionist "{agent_name}" is now answering calls at {phone_number}.

Go to your dashboard:
{context['dashboard_url']}

Share your new number and start receiving calls!

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_call_confirmation(
        self, to_email: str, caller_phone: str, appointment_details: dict
    ) -> bool:
        subject = "Your appointment is confirmed"
        
        context = {
            "caller_phone": caller_phone,
            "date": appointment_details.get("date", "TBD"),
            "time": appointment_details.get("time", "TBD"),
            "service": appointment_details.get("service", "Appointment"),
            "company_name": appointment_details.get("company_name", "Our office"),
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("onboarding_complete", context)
        text = f"""
Your appointment is confirmed!

Date: {context['date']}
Time: {context['time']}
Service: {context['service']}

See you soon!

Best regards,
{context['company_name']}
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_payment_failed_email(
        self, to_email: str, company_name: str, amount: float, retry_date: datetime
    ) -> bool:
        subject = "Action Required: Payment failed for VoiceCore"
        
        retry_str = retry_date.strftime("%B %d, %Y") if retry_date else "soon"
        
        context = {
            "company_name": company_name,
            "amount": amount,
            "retry_date": retry_str,
            "update_payment_url": f"{self.base_url}/billing",
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("payment_failed", context)
        text = f"""
Action Required: Payment failed for VoiceCore

Company: {company_name}
Amount: ${amount:.2f}
Retry Date: {retry_str}

Your agent will continue working for 7 more days. Please update your payment method:

{context['update_payment_url']}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_subscription_cancelled_email(
        self, to_email: str, company_name: str
    ) -> bool:
        subject = "Your VoiceCore subscription has been cancelled"
        
        context = {
            "company_name": company_name,
            "reactivate_url": f"{self.base_url}/reactivate",
            "year": datetime.utcnow().year,
        }
        
        html = self._generic_template(context)
        text = f"""
Your VoiceCore subscription has been cancelled.

We're sorry to see you go, {company_name}. If you have feedback, please let us know.

To reactivate:
{context['reactivate_url']}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_angry_customer_alert(
        self, to_email: str, company_name: str, call_data: dict
    ) -> bool:
        subject = f" Angry Customer Alert - {company_name}"
        
        masked_phone = self._mask_phone(call_data.get("caller_phone", "Unknown"))
        last_quote = call_data.get("last_statement", "Customer was upset during the call.")
        call_time = call_data.get("call_time", datetime.utcnow().isoformat())
        recording_url = call_data.get("recording_url", f"{self.base_url}/calls")
        
        context = {
            "company_name": company_name,
            "caller_phone": masked_phone,
            "last_quote": last_quote,
            "call_time": call_time,
            "recording_url": recording_url,
            "dashboard_url": f"{self.base_url}/calls",
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("angry_customer_alert", context)
        text = f"""
Angry Customer Alert - Immediate Attention Required

Company: {company_name}
Caller: {masked_phone}
Time: {call_time}

Last statement: "{last_quote}"

Listen to recording: {recording_url}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_daily_summary_email(
        self, to_email: str, company_name: str, stats: dict
    ) -> bool:
        subject = f"Your VoiceCore Daily Summary - {datetime.utcnow().strftime('%B %d, %Y')}"
        
        if isinstance(stats, dict):
            stats_obj = DailySummaryStats(stats)
        else:
            stats_obj = stats
        
        context = {
            "company_name": company_name,
            "total_calls": stats_obj.total_calls,
            "total_duration": stats_obj.total_duration,
            "avg_sentiment": stats_obj.avg_sentiment,
            "resolved_rate": stats_obj.resolved_rate,
            "missed_calls": stats_obj.missed_calls,
            "appointments_booked": stats_obj.appointments_booked,
            "top_event": stats_obj.top_event,
            "sentiment_breakdown": stats_obj.sentiment_breakdown,
            "dashboard_url": f"{self.base_url}/dashboard",
            "date": datetime.utcnow().strftime("%B %d, %Y"),
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("daily_summary", context)
        text = f"""
Your VoiceCore Daily Summary - {context['date']}

Company: {company_name}

Total Calls: {stats_obj.total_calls}
Total Duration: {stats_obj.total_duration} minutes
Avg Sentiment: {stats_obj.avg_sentiment:.1f}%
Resolved Rate: {stats_obj.resolved_rate}%
Missed Calls: {stats_obj.missed_calls}
Appointments Booked: {stats_obj.appointments_booked}

Dashboard: {context['dashboard_url']}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_weekly_report_email(
        self, to_email: str, company_name: str, report: dict
    ) -> bool:
        subject = "Your VoiceCore Weekly Report"
        
        if isinstance(report, dict):
            report_obj = WeeklyReport(report)
        else:
            report_obj = report
        
        context = {
            "company_name": company_name,
            "total_calls": report_obj.total_calls,
            "weekly_trend": report_obj.weekly_trend,
            "compared_to_last_week": report_obj.compared_to_last_week,
            "missed_calls": report_obj.missed_calls,
            "appointments_booked": report_obj.appointments_booked,
            "avg_sentiment": report_obj.avg_sentiment,
            "top_event": report_obj.top_event,
            "dashboard_url": f"{self.base_url}/dashboard",
            "week_start": report.get("week_start", ""),
            "week_end": report.get("week_end", ""),
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("weekly_report", context)
        text = f"""
Your VoiceCore Weekly Report

Company: {company_name}
Week: {context['week_start']} - {context['week_end']}

Total Calls: {report_obj.total_calls}
Trend: {report_obj.weekly_trend:+.1f}% vs last week
Missed Calls: {report_obj.missed_calls}
Appointments Booked: {report_obj.appointments_booked}
Avg Sentiment: {report_obj.avg_sentiment:.1f}%

Dashboard: {context['dashboard_url']}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_missed_call_email(
        self, to_email: str, company_name: str, caller_phone: str
    ) -> bool:
        subject = f"Missed Call from {caller_phone}"
        
        context = {
            "company_name": company_name,
            "caller_phone": caller_phone,
            "dashboard_url": f"{self.base_url}/calls",
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("missed_call", context)
        text = f"""
Missed Call

Company: {company_name}
Caller: {caller_phone}

Callback: {context['dashboard_url']}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_day3_checkin_email(
        self, to_email: str, company_name: str, calls_so_far: int
    ) -> bool:
        if calls_so_far == 0:
            subject = f"Something not working? Let us help - {company_name}"
        else:
            subject = f"How is VoiceCore doing? {calls_so_far} calls handled!"
        
        context = {
            "company_name": company_name,
            "calls_so_far": calls_so_far,
            "support_url": f"{self.base_url}/support",
            "dashboard_url": f"{self.base_url}/dashboard",
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("day3_checkin", context)
        text = f"""
How is VoiceCore doing?

{company_name} - Day 3 Check-in

"""
        if calls_so_far == 0:
            text += "We noticed your agent hasn't received any calls yet. Something not working? Let us help."
        else:
            text += f"Great news! Your agent has handled {calls_so_far} calls already!"

        text += f"""

Dashboard: {context['dashboard_url']}
Support: {context['support_url']}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_churn_risk_email(
        self, to_email: str, company_name: str, days_inactive: int
    ) -> bool:
        subject = f"Is everything OK? We noticed your agent has been quiet"
        
        context = {
            "company_name": company_name,
            "days_inactive": days_inactive,
            "troubleshooting_url": f"{self.base_url}/troubleshooting",
            "support_url": f"{self.base_url}/support",
            "year": datetime.utcnow().year,
        }
        
        html = self._render_template("churn_risk", context)
        text = f"""
Is everything OK?

We noticed {company_name}'s agent has been quiet for {days_inactive} days.

Need help? We're here for you:
- Troubleshooting guide: {context['troubleshooting_url']}
- Contact support: {context['support_url']}

Best regards,
The VoiceCore Team
"""
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    async def send_generic_notification(
        self, to_email: str, subject: str, message: str
    ) -> bool:
        context = {
            "message": message,
            "year": datetime.utcnow().year,
        }
        
        html = self._generic_template(context)
        text = message
        
        return await self._send_via_sendgrid(to_email, subject, html, text)
    
    def _mask_phone(self, phone: str) -> str:
        if not phone or len(phone) < 4:
            return "XXX-XXX-XXXX"
        return phone[:-4].replace("+", "")[:6].replace("1", "") + "XXXX"
    
    def _welcome_template(self, context: dict) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to VoiceCore</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px; text-align: center;">
        <h1 style="color: #F59E0B; margin-bottom: 20px;">Welcome to VoiceCore!</h1>
        <p style="color: #A1A1AA; font-size: 16px;">Hi {context.get('user_name', 'there')},</p>
        <p style="color: #A1A1AA; font-size: 16px;">Your AI receptionist for <strong>{context.get('company_name', 'your business')}</strong> is ready to go.</p>
        <p style="color: #F59E0B; font-size: 18px; margin: 30px 0;">Setup takes only 30 minutes</p>
        <a href="{context.get('onboarding_url', '#')}" style="display: inline-block; background: #F59E0B; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">Start Setup</a>
        <p style="color: #71717A; font-size: 12px; margin-top: 30px;">Need help? Check our <a href="{context.get('docs_url', '#')}" style="color: #F59E0B;">documentation</a></p>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _onboarding_complete_template(self, context: dict) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>You're Live!</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px; text-align: center;">
        <h1 style="color: #F59E0B; margin-bottom: 20px;">You're Live!</h1>
        <p style="color: #FFFFFF; font-size: 24px; margin: 20px 0;"><strong>{context.get('company_name', 'Your Company')}</strong></p>
        <p style="color: #A1A1AA; font-size: 16px;">Your AI receptionist <strong>{context.get('agent_name', 'Agent')}</strong> is now answering calls at:</p>
        <p style="color: #F59E0B; font-size: 28px; font-weight: bold; margin: 20px 0;">{context.get('phone_number', '+1-XXX-XXX-XXXX')}</p>
        <a href="{context.get('dashboard_url', '#')}" style="display: inline-block; background: #F59E0B; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">Go to Dashboard</a>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _angry_customer_template(self, context: dict) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Angry Customer Alert</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px; border-left: 4px solid #EF4444;">
        <h1 style="color: #EF4444; margin-bottom: 20px;"> Angry Customer Alert</h1>
        <p style="color: #A1A1AA; font-size: 14px;">Immediate Attention Required</p>
        <hr style="border-color: #27272A; margin: 20px 0;">
        <p><strong style="color: #FFFFFF;">Caller:</strong> <span style="color: #F59E0B;">{context.get('caller_phone', 'Unknown')}</span></p>
        <p><strong style="color: #FFFFFF;">Time:</strong> <span style="color: #A1A1AA;">{context.get('call_time', 'Just now')}</span></p>
        <p style="margin-top: 20px;"><strong style="color: #FFFFFF;">Last statement:</strong></p>
        <p style="background: #27272A; padding: 15px; border-radius: 8px; font-style: italic; color: #FCA5A5;">"{context.get('last_quote', 'Customer was upset during the call.')}"</p>
        <div style="margin-top: 30px;">
            <a href="{context.get('recording_url', '#')}" style="display: inline-block; background: #EF4444; color: #FFF; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-right: 10px;">Listen to Recording</a>
            <a href="{context.get('dashboard_url', '#')}" style="display: inline-block; background: #27272A; color: #FFF; padding: 12px 24px; text-decoration: none; border-radius: 8px;">View Dashboard</a>
        </div>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _daily_summary_template(self, context: dict) -> str:
        sentiment_bar = int(context.get('avg_sentiment', 0) / 10)
        sentiment_color = "#22C55E" if sentiment_bar >= 7 else "#F59E0B" if sentiment_bar >= 4 else "#EF4444"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Summary</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px;">
        <h1 style="color: #F59E0B; margin-bottom: 5px;"> Daily Summary</h1>
        <p style="color: #71717A; font-size: 14px;">{context.get('date', 'Today')} - {context.get('company_name', 'Your Company')}</p>
        <hr style="border-color: #27272A; margin: 20px 0;">
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px;">
            <div style="background: #27272A; padding: 15px; border-radius: 8px; text-align: center;">
                <p style="color: #F59E0B; font-size: 28px; margin: 0;">{context.get('total_calls', 0)}</p>
                <p style="color: #71717A; font-size: 12px; margin: 5px 0 0 0;">Total Calls</p>
            </div>
            <div style="background: #27272A; padding: 15px; border-radius: 8px; text-align: center;">
                <p style="color: #F59E0B; font-size: 28px; margin: 0;">{context.get('total_duration', 0)}</p>
                <p style="color: #71717A; font-size: 12px; margin: 5px 0 0 0;">Minutes</p>
            </div>
            <div style="background: #27272A; padding: 15px; border-radius: 8px; text-align: center;">
                <p style="color: #EF4444; font-size: 28px; margin: 0;">{context.get('missed_calls', 0)}</p>
                <p style="color: #71717A; font-size: 12px; margin: 5px 0 0 0;">Missed</p>
            </div>
            <div style="background: #27272A; padding: 15px; border-radius: 8px; text-align: center;">
                <p style="color: #22C55E; font-size: 28px; margin: 0;">{context.get('appointments_booked', 0)}</p>
                <p style="color: #71717A; font-size: 12px; margin: 5px 0 0 0;">Appointments</p>
            </div>
        </div>
        
        <div style="background: #27272A; padding: 15px; border-radius: 8px;">
            <p style="color: #FFFFFF; margin: 0 0 10px 0;"><strong>Sentiment Score: {context.get('avg_sentiment', 0):.1f}%</strong></p>
            <div style="background: #3F3F46; height: 8px; border-radius: 4px;">
                <div style="background: {sentiment_color}; height: 8px; border-radius: 4px; width: {context.get('avg_sentiment', 0):.1f}%;"></div>
            </div>
        </div>
        
        <a href="{context.get('dashboard_url', '#')}" style="display: block; text-align: center; background: #F59E0B; color: #000; padding: 15px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 20px;">View Full Dashboard</a>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _weekly_report_template(self, context: dict) -> str:
        trend_color = "#22C55E" if context.get('weekly_trend', 0) > 0 else "#EF4444"
        trend_arrow = "↑" if context.get('weekly_trend', 0) > 0 else "↓"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Report</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px;">
        <h1 style="color: #F59E0B; margin-bottom: 5px;"> Weekly Report</h1>
        <p style="color: #71717A; font-size: 14px;">{context.get('week_start', 'This week')} - {context.get('company_name', 'Your Company')}</p>
        <hr style="border-color: #27272A; margin: 20px 0;">
        
        <div style="background: #27272A; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
            <p style="color: #F59E0B; font-size: 48px; margin: 0;">{context.get('total_calls', 0)}</p>
            <p style="color: #71717A; margin: 5px 0;">Total Calls</p>
            <p style="color: {trend_color}; font-size: 18px; margin: 10px 0 0 0;">{trend_arrow} {abs(context.get('weekly_trend', 0)):.1f}% vs last week</p>
        </div>
        
        <a href="{context.get('dashboard_url', '#')}" style="display: block; text-align: center; background: #F59E0B; color: #000; padding: 15px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 20px;">View Full Report</a>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _missed_call_template(self, context: dict) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Missed Call</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px; text-align: center;">
        <h1 style="color: #F59E0B; margin-bottom: 20px;"> Missed Call</h1>
        <p style="color: #A1A1AA; font-size: 14px;">{context.get('company_name', 'Your Company')}</p>
        <p style="color: #FFFFFF; font-size: 24px; margin: 20px 0;">{context.get('caller_phone', 'Unknown')}</p>
        <a href="{context.get('dashboard_url', '#')}" style="display: inline-block; background: #F59E0B; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">Call Back Now</a>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _payment_failed_template(self, context: dict) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Failed</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px; text-align: center;">
        <h1 style="color: #EF4444; margin-bottom: 20px;"> Action Required</h1>
        <p style="color: #A1A1AA; font-size: 16px;">Payment failed for VoiceCore</p>
        <p style="color: #FFFFFF; font-size: 18px; margin: 20px 0;">Amount: <strong>${context.get('amount', 0):.2f}</strong></p>
        <p style="color: #71717A; font-size: 14px;">Retry Date: {context.get('retry_date', 'Soon')}</p>
        <p style="color: #A1A1AA; font-size: 14px; margin-top: 20px;">Your agent will continue working for 7 more days.</p>
        <a href="{context.get('update_payment_url', '#')}" style="display: inline-block; background: #F59E0B; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 20px;">Update Payment</a>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _day3_checkin_template(self, context: dict) -> str:
        if context.get('calls_so_far', 0) == 0:
            message = "We noticed your agent hasn't received any calls yet. Something not working? Let us help."
            color = "#F59E0B"
        else:
            message = f"Great news! Your agent has handled {context.get('calls_so_far', 0)} calls already!"
            color = "#22C55E"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Day 3 Check-in</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px; text-align: center;">
        <h1 style="color: {color}; margin-bottom: 20px;">How is {context.get('company_name', 'Your Agent')} doing?</h1>
        <p style="color: #FFFFFF; font-size: 18px;">{message}</p>
        <div style="margin-top: 30px;">
            <a href="{context.get('dashboard_url', '#')}" style="display: inline-block; background: #27272A; color: #FFF; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-right: 10px;">View Dashboard</a>
            <a href="{context.get('support_url', '#')}" style="display: inline-block; background: #F59E0B; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 8px;">Get Help</a>
        </div>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _churn_risk_template(self, context: dict) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Is everything OK?</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px; text-align: center;">
        <h1 style="color: #F59E0B; margin-bottom: 20px;">Is everything OK?</h1>
        <p style="color: #A1A1AA; font-size: 16px;">We noticed {context.get('company_name', 'your agent')}'s agent has been quiet for <strong>{context.get('days_inactive', 7)} days</strong>.</p>
        <p style="color: #71717A; font-size: 14px; margin-top: 20px;">Need help? We're here for you.</p>
        <div style="margin-top: 30px;">
            <a href="{context.get('troubleshooting_url', '#')}" style="display: inline-block; background: #27272A; color: #FFF; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-right: 10px;">Troubleshooting</a>
            <a href="{context.get('support_url', '#')}" style="display: inline-block; background: #F59E0B; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 8px;">Contact Support</a>
        </div>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
    
    def _generic_template(self, context: dict) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceCore Notification</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0A0A0A; color: #FFFFFF;">
    <div style="background: #1A1A1A; border-radius: 12px; padding: 30px;">
        <p style="color: #FFFFFF; font-size: 16px;">{context.get('message', 'You have a new notification from VoiceCore.')}</p>
    </div>
    <p style="text-align: center; color: #52525B; font-size: 12px; margin-top: 20px;">VoiceCore AI Receptionist - {context.get('year', 2024)}</p>
</body>
</html>
"""
