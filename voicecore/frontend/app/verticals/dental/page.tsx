'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Phone, Clock, Shield, CheckCircle, ArrowRight, Star, MessageSquare, Calendar, AlertCircle, Users, FileText } from 'lucide-react';

export default function DentalPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  const features = [
    {
      icon: Users,
      title: 'New Patient Intake',
      description: 'Handles registration, insurance verification, and collects all necessary information automatically'
    },
    {
      icon: Shield,
      title: 'Insurance Expertise',
      description: 'Understands PPO, HMO, Delta Dental, Cigna, Aetna, and explains coverage in simple terms'
    },
    {
      icon: Calendar,
      title: 'Instant Booking',
      description: 'Books appointments immediately based on procedure type and urgency level'
    },
    {
      icon: AlertCircle,
      title: 'Emergency Priority',
      description: 'Detects dental emergencies (toothache, abscess, broken tooth) and offers same-day appointments'
    },
    {
      icon: FileText,
      title: 'Auto Forms',
      description: 'Sends intake forms automatically via WhatsApp after booking'
    },
    {
      icon: MessageSquare,
      title: 'WhatsApp Confirmations',
      description: 'Sends appointment reminders and confirmations via WhatsApp'
    }
  ];

  const testimonials = [
    { name: 'Dr. Sarah Johnson', practice: 'Smile Design Dental', text: 'Lost patients were going to voicemail. DentalVoice answered 200+ calls last month we would have missed.' },
    { name: 'Dr. Michael Chen', practice: 'Comfort Care Dentistry', text: 'The emergency detection is incredible. A patient with an abscess got same-day treatment because our AI flagged it as urgent.' },
    { name: 'Dr. Lisa Patel', practice: 'Family Dental Group', text: 'New patient bookings increased 40%. The intake forms feature alone saved our front desk 10 hours per week.' }
  ];

  const painPoints = [
    '35% of dental calls go to voicemail after hours',
    'Lost patients = lost revenue ($500-2000+ per patient)',
    'Front desk overwhelmed with scheduling',
    'Missed emergency calls create liability',
    'No way to capture after-hours leads'
  ];

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
              <Phone className="w-6 h-6 text-zinc-950" />
            </div>
            <span className="text-xl font-bold text-white">DentalVoice</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-zinc-400 hover:text-white transition">Sign in</Link>
            <Link href="/signup?vertical=dental" className="btn-primary">Start Free Trial</Link>
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
              <span>Trusted by 500+ dental practices</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
              Your dental practice's{' '}
              <span className="text-amber-500">24/7 receptionist</span>
            </h1>
            
            <p className="text-xl text-zinc-400 mb-10 max-w-2xl mx-auto">
              Never miss a patient call again. Our AI receptionist handles booking, insurance questions, and dental emergencies — while you focus on patient care.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/signup?vertical=dental" className="btn-primary text-lg px-8 py-4 inline-flex items-center gap-2">
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
            <h2 className="text-3xl font-bold text-white mb-8 text-center">Stop losing patients to voicemail</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {painPoints.map((point, i) => (
                <div key={i} className="flex items-center gap-3 text-zinc-300">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <span>{point}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Built for Dental Practices</h2>
            <p className="text-xl text-zinc-400">Everything your front desk needs — automated</p>
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

      {/* How It Works */}
      <section className="py-20 bg-zinc-900/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">How It Works</h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: '01', title: 'Connect Your Phone', description: 'We integrate with your existing phone number in minutes' },
              { step: '02', title: 'AI Learns Your Practice', description: 'Configure hours, procedures, and emergency protocols' },
              { step: '03', title: 'Never Miss a Call', description: '24/7 receptionist starts answering immediately' }
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
            <p className="text-xl text-zinc-400">Less than one missed patient per month</p>
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
              <h3 className="text-2xl font-bold text-white mb-2">DentalVoice</h3>
              <div className="flex items-baseline gap-1 mb-4">
                <span className="text-4xl font-bold text-amber-500">
                  ${billingCycle === 'monthly' ? '399' : '319'}
                </span>
                <span className="text-zinc-400">/month</span>
              </div>
              <p className="text-zinc-400 mb-6">Less than one missed patient per month</p>
              
              <ul className="space-y-3 mb-8">
                {['Unlimited calls', 'New patient intake', 'Insurance verification', 'Emergency detection', 'WhatsApp confirmations', 'Online booking', '24/7 availability', 'No setup fee'].map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-zinc-300">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    {feature}
                  </li>
                ))}
              </ul>
              
              <Link
                href="/signup?vertical=dental"
                className="block text-center py-3 rounded-lg font-semibold bg-amber-500 text-zinc-950 hover:bg-amber-600 transition"
              >
                Start 14-Day Free Trial
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-zinc-900/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Trusted by Dentists</h2>
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
                  <p className="text-zinc-500 text-sm">{testimonial.practice}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to never miss another patient?</h2>
          <p className="text-xl text-zinc-400 mb-8 max-w-2xl mx-auto">
            Join 500+ dental practices using DentalVoice. Start your free 14-day trial — no credit card required.
          </p>
          <Link href="/signup?vertical=dental" className="btn-primary text-lg px-10 py-4 inline-flex items-center gap-2">
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
                <Phone className="w-4 h-4 text-zinc-950" />
              </div>
              <span className="text-lg font-bold text-white">DentalVoice</span>
            </div>
            <div className="flex items-center gap-6 text-zinc-500">
              <Link href="#" className="hover:text-white transition">Privacy</Link>
              <Link href="#" className="hover:text-white transition">Terms</Link>
              <Link href="#" className="hover:text-white transition">Contact</Link>
            </div>
            <div className="text-zinc-500">
              © 2024 DentalVoice. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
