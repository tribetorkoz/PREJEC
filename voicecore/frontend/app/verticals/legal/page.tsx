'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Phone, Clock, Shield, CheckCircle, ArrowRight, Star, MessageSquare, AlertTriangle, FileText, Scale, Users, Lock, Gavel } from 'lucide-react';

export default function LegalPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  const features = [
    {
      icon: Scale,
      title: 'All Practice Areas',
      description: 'Handles Personal Injury, Criminal Defense, Family Law, Immigration, Employment, Estate Planning, and Bankruptcy'
    },
    {
      icon: Lock,
      title: 'Confidentiality First',
      description: 'Trained to never repeat sensitive info, refuse to confirm client status, and maintain attorney-client privilege'
    },
    {
      icon: AlertTriangle,
      title: 'Urgency Detection',
      description: 'Instantly flags emergencies (arrests, deportation, custody) and alerts on-call attorney within 15 minutes'
    },
    {
      icon: Shield,
      title: 'HIPAA & Privilege Compliant',
      description: 'AES-256 encryption, audit logging, and strict PII retention policies protect client information'
    },
    {
      icon: Users,
      title: 'Case Qualification',
      description: 'Pre-screens potential clients and determines if cases fit your practice areas before scheduling'
    },
    {
      icon: FileText,
      title: 'Conflict Checking',
      description: 'Automatically checks for conflicts of interest before scheduling — critical for legal ethics compliance'
    }
  ];

  const testimonials = [
    { name: 'James Morrison', firm: 'Morrison & Associates', text: 'We were losing $50K/month to missed calls. LegalVoice captured every lead and our intake conversion jumped 60%.' },
    { name: 'Sarah Chen', firm: 'Chen Criminal Defense', text: 'The urgency detection is a game-changer. When a potential client said they were arrested, our on-call attorney got the alert immediately.' },
    { name: 'Robert Williams', firm: 'Williams Family Law', text: 'Finally handling after-hours calls properly. The conflict check alone has prevented potential ethics issues.' }
  ];

  const painPoints = [
    '42% of law firm calls go to voicemail after hours',
    'Missed call = $1,500+ in lost potential fees on average',
    'Front desk can\'t handle 24/7 coverage economically',
    'Potential clients rarely call back',
    'No systematic way to capture after-hours leads'
  ];

  const practiceAreas = [
    'Personal Injury',
    'Criminal Defense',
    'Family Law',
    'Immigration',
    'Employment Law',
    'Estate Planning',
    'Bankruptcy'
  ];

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
              <Gavel className="w-6 h-6 text-zinc-950" />
            </div>
            <span className="text-xl font-bold text-white">LegalVoice</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-zinc-400 hover:text-white transition">Sign in</Link>
            <Link href="/signup?vertical=legal" className="btn-primary">Start Free Trial</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-amber-500/5 to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-amber-500/10 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-6 relative">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 text-amber-500 text-sm mb-8">
              <Star className="w-4 h-4" />
              <span>SOC 2 Compliant • Attorney-Client Privilege Protected</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
              Never miss a potential client{' '}
              <span className="text-amber-500">again — 24/7 legal intake</span>
            </h1>
            
            <p className="text-xl text-zinc-400 mb-10 max-w-2xl mx-auto">
              Your AI intake specialist handles calls, qualifies cases, checks conflicts, and alerts your team to emergencies — while you focus on practicing law.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/signup?vertical=legal" className="btn-primary text-lg px-8 py-4 inline-flex items-center gap-2">
                Start free trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <button className="btn-secondary text-lg px-8 py-4">
                See demo
              </button>
            </div>

            <div className="mt-12 flex items-end justify-center gap-1 h-16">
              {[...Array(12)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 bg-amber-500/60 rounded-t"
                  style={{
                    height: `${20 + Math.sin(i * 0.5) * 30}%`,
                    animationDelay: `${i * 0.1}s`,
                    animation: 'wave 1.5s ease-in-out infinite'
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Pain Points */}
      <section className="py-16 bg-red-500/5 border-y border-red-500/10">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">Law firms miss 42% of calls</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {painPoints.map((point, i) => (
                <div key={i} className="flex items-center gap-3 text-zinc-300">
                  <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <span>{point}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Practice Areas */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Understands All Major Practice Areas</h2>
            <p className="text-xl text-zinc-400">LegalVoice is trained on intake procedures for</p>
          </div>
          
          <div className="flex flex-wrap justify-center gap-3">
            {practiceAreas.map((area, i) => (
              <span 
                key={i} 
                className="px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-full text-zinc-300"
              >
                {area}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-zinc-900/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Built for Law Firms</h2>
            <p className="text-xl text-zinc-400">Everything your intake team needs — automated</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-amber-500/50 transition">
                <feature.icon className="w-10 h-10 text-amber-500 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-zinc-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Compliance */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-white mb-4">Enterprise-Grade Security & Compliance</h2>
              <p className="text-xl text-zinc-400">Built for the strict requirements of legal ethics</p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                <Lock className="w-10 h-10 text-amber-500 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">AES-256 Encryption</h3>
                <p className="text-zinc-400">All call transcripts are encrypted at rest and in transit</p>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                <Clock className="w-10 h-10 text-amber-500 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">30-Day PII Retention</h3>
                <p className="text-zinc-400">Automatically purges caller data after 30 days (configurable)</p>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                <FileText className="w-10 h-10 text-amber-500 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Complete Audit Log</h3>
                <p className="text-zinc-400">Every data access is logged for compliance and ethics reviews</p>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                <Shield className="w-10 h-10 text-amber-500 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Conflict Checking</h3>
                <p className="text-zinc-400">Automated conflict checks before scheduling consultations</p>
              </div>
            </div>
            
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <span className="px-4 py-2 bg-green-500/10 text-green-500 rounded-full text-sm font-medium">
                SOC 2 Compliant
              </span>
              <span className="px-4 py-2 bg-green-500/10 text-green-500 rounded-full text-sm font-medium">
                HIPAA Ready
              </span>
              <span className="px-4 py-2 bg-green-500/10 text-green-500 rounded-full text-sm font-medium">
                Attorney-Client Privilege Protected
              </span>
              <span className="px-4 py-2 bg-green-500/10 text-green-500 rounded-full text-sm font-medium">
                State Wiretapping Law Compliant
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-zinc-900/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">How It Works</h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: '01', title: 'Connect Your Phone', description: 'We integrate with your existing phone number in minutes' },
              { step: '02', title: 'Configure Practice Areas', description: 'Set your practice areas, emergency protocols, and intake procedures' },
              { step: '03', title: 'Never Miss a Lead', description: '24/7 intake specialist starts capturing leads immediately' }
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="text-6xl font-bold text-amber-500/20 mb-4">{item.step}</div>
                <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-zinc-400">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-zinc-400">Less than one missed case per month</p>
          </div>
          
          <div className="flex justify-center mb-8">
            <div className="bg-zinc-800 rounded-lg p-1 flex">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${billingCycle === 'monthly' ? 'bg-amber-500 text-zinc-950' : 'text-zinc-400 hover:text-white'}`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('annual')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${billingCycle === 'annual' ? 'bg-amber-500 text-zinc-950' : 'text-zinc-400 hover:text-white'}`}
              >
                Annual <span className="text-xs text-green-500 ml-1">(Save 20%)</span>
              </button>
            </div>
          </div>
          
          <div className="max-w-md mx-auto">
            <div className="bg-zinc-900 border-2 border-amber-500 rounded-2xl p-8">
              <h3 className="text-2xl font-bold text-white mb-2">LegalVoice</h3>
              <div className="flex items-baseline gap-1 mb-4">
                <span className="text-4xl font-bold text-amber-500">
                  ${billingCycle === 'monthly' ? '599' : '479'}
                </span>
                <span className="text-zinc-400">/month</span>
              </div>
              <p className="text-zinc-400 mb-6">Less than one missed case ($1,500+) per month</p>
              
              <ul className="space-y-3 mb-8">
                {['Unlimited calls', 'All practice areas', 'Conflict checking', 'Urgency detection', 'AES-256 encryption', 'Audit logging', '24/7 availability', 'No setup fee'].map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-zinc-300">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    {feature}
                  </li>
                ))}
              </ul>
              
              <Link
                href="/signup?vertical=legal"
                className="block text-center py-3 rounded-lg font-semibold bg-amber-500 text-zinc-950 hover:bg-amber-600 transition"
              >
                Start 14-Day Free Trial
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="py-12 bg-zinc-900/50 border-t border-zinc-800">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center">
            <p className="text-zinc-500 text-sm">
              <strong className="text-zinc-400">Important Disclaimer:</strong> LegalVoice is an intake and scheduling tool only. 
              It does not provide legal advice. All consultations must be conducted by licensed attorneys. 
              Users should have a qualified attorney review the system configuration before going live. 
              Compliance with state-specific wiretapping laws is the responsibility of the law firm.
            </p>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Trusted by Law Firms</h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, j) => (
                    <Star key={j} className="w-5 h-5 text-amber-500 fill-amber-500" />
                  ))}
                </div>
                <p className="text-zinc-300 mb-4">"{testimonial.text}"</p>
                <div>
                  <p className="font-semibold text-white">{testimonial.name}</p>
                  <p className="text-zinc-500 text-sm">{testimonial.firm}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to capture every potential client?</h2>
          <p className="text-xl text-zinc-400 mb-8 max-w-2xl mx-auto">
            Join law firms using LegalVoice. Start your free 14-day trial — no credit card required.
          </p>
          <Link href="/signup?vertical=legal" className="btn-primary text-lg px-10 py-4 inline-flex items-center gap-2">
            Start free trial
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-zinc-800">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
                <Gavel className="w-4 h-4 text-zinc-950" />
              </div>
              <span className="text-lg font-bold text-white">LegalVoice</span>
            </div>
            <div className="flex items-center gap-6 text-zinc-500">
              <Link href="#" className="hover:text-white transition">Privacy</Link>
              <Link href="#" className="hover:text-white transition">Terms</Link>
              <Link href="#" className="hover:text-white transition">Contact</Link>
            </div>
            <div className="text-zinc-500">
              © 2024 LegalVoice. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
