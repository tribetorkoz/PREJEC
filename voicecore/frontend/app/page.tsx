'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import {
  Phone,
  Globe,
  BarChart3,
  Clock,
  CheckCircle,
  Star,
  MessageSquare,
  Zap,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  Play,
  Users,
  TrendingUp,
  Shield,
  Calendar,
  Brain,
  Globe2,
} from 'lucide-react';

interface Stats {
  calls_today: number;
  calls_total: number;
  companies_active: number;
  uptime_percentage: number;
}

interface Testimonial {
  id: number;
  name: string;
  company: string;
  city: string;
  avatar: string;
  rating: number;
  quote: string;
  industry: string;
}

export default function Home() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [selectedIndustry, setSelectedIndustry] = useState('dental');
  const [stats, setStats] = useState<Stats>({
    calls_today: 2847,
    calls_total: 1250000,
    companies_active: 523,
    uptime_percentage: 99.97,
  });
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [demoStarted, setDemoStarted] = useState(false);

  useEffect(() => {
    fetchStats();
    fetchTestimonials();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/v1/stats/today');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      console.error('Failed to fetch stats');
    }
  };

  const fetchTestimonials = async () => {
    try {
      const res = await fetch('/api/v1/testimonials');
      if (res.ok) {
        const data = await res.json();
        setTestimonials(data.testimonials || []);
      }
    } catch (e) {
      setTestimonials([
        {
          id: 1,
          name: 'Dr. Michael Chen',
          company: 'Bright Smile Dental',
          city: 'Chicago',
          avatar: 'MC',
          rating: 5,
          quote: 'VoiceCore handled 847 calls last month. We recovered $23,000 in appointments we would have missed.',
          industry: 'dental',
        },
        {
          id: 2,
          name: 'Sarah Kim',
          company: 'Kim & Associates Law Firm',
          city: 'Los Angeles',
          avatar: 'SK',
          rating: 5,
          quote: 'Our intake process went from 3 days to 4 hours. The AI catches everything.',
          industry: 'legal',
        },
        {
          id: 3,
          name: 'James Rodriguez',
          company: 'Premier Realty Group',
          city: 'Miami',
          avatar: 'JR',
          rating: 5,
          quote: 'Closed 12 extra deals last quarter from leads VoiceCore captured.',
          industry: 'realty',
        },
      ]);
    }
  };

  const industries = [
    { id: 'dental', name: 'Dental', icon: '🦷' },
    { id: 'legal', name: 'Legal', icon: '⚖️' },
    { id: 'realty', name: 'Realty', icon: '🏠' },
    { id: 'general', name: 'General', icon: '📱' },
  ];

  const features = [
    {
      icon: Brain,
      title: 'Remembers Customers',
      description: 'Your AI knows every returning caller and their history',
    },
    {
      icon: Globe2,
      title: 'Speaks 50+ Languages',
      description: 'Auto-detects and responds in customer\'s language',
    },
    {
      icon: Calendar,
      title: 'Books Appointments',
      description: 'Syncs with Google Calendar, Outlook, Calendly',
    },
    {
      icon: TrendingUp,
      title: 'Detects Emotions',
      description: 'Escalates frustrated customers automatically',
    },
    {
      icon: BarChart3,
      title: 'Full Analytics',
      description: 'Sentiment, intent, conversion — all tracked',
    },
    {
      icon: Shield,
      title: 'HIPAA Compliant',
      description: 'Safe for medical, legal, financial industries',
    },
  ];

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      yearlyPrice: 0,
      calls: '50',
      popular: false,
      features: ['Basic analytics', '1 AI agent', '3 languages'],
    },
    {
      id: 'starter',
      name: 'Starter',
      price: 99,
      yearlyPrice: 950,
      calls: '500',
      popular: false,
      features: ['Full analytics', '3 AI agents', '10 languages', 'Calendar integration'],
    },
    {
      id: 'business',
      name: 'Business',
      price: 399,
      yearlyPrice: 3830,
      calls: '2,000',
      popular: true,
      features: ['Advanced analytics', '10 AI agents', '50+ languages', 'CRM integration', 'HIPAA compliant'],
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: null,
      yearlyPrice: null,
      calls: 'Unlimited',
      popular: false,
      features: ['Custom analytics', 'Unlimited agents', 'White-label', 'Dedicated support', 'SLA'],
    },
  ];

  const faqs = [
    {
      q: 'How long does setup take?',
      a: 'Most customers are up and running in under 30 minutes. Our onboarding wizard guides you through configuring your AI agent, selecting a voice, and connecting your phone number.',
    },
    {
      q: 'Do I need technical knowledge?',
      a: 'Not at all! VoiceCore is designed for non-technical users. If you can use a phone, you can use VoiceCore.',
    },
    {
      q: 'Can the AI handle multiple calls simultaneously?',
      a: 'Yes! Unlike human receptionists, our AI can handle unlimited simultaneous calls without getting tired or making mistakes.',
    },
    {
      q: 'What happens when the AI cannot answer?',
      a: 'The AI will gather relevant information and seamlessly transfer the caller to a human agent with full context of the conversation.',
    },
    {
      q: 'Is it HIPAA compliant?',
      a: 'Yes! VoiceCore is HIPAA compliant on Business and Enterprise plans. We offer BAA agreements and AES-256 encryption for all PHI data.',
    },
    {
      q: 'Can I keep my existing phone number?',
      a: 'Absolutely! We support number porting for most phone numbers. Your existing customers can continue reaching you at the same number.',
    },
    {
      q: 'What languages are supported?',
      a: 'VoiceCore supports 50+ languages including English, Arabic, French, Spanish, German, Chinese, Japanese, and more.',
    },
    {
      q: 'Can I cancel anytime?',
      a: 'Yes, you can cancel your subscription at any time with no cancellation fees. Your data is exportable before you go.',
    },
  ];

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-zinc-950/80 backdrop-blur-sm border-b border-zinc-800">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
              <Phone className="w-6 h-6 text-zinc-950" />
            </div>
            <span className="text-xl font-bold text-white">VoiceCore</span>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-zinc-400 hover:text-white transition">Features</Link>
            <Link href="#pricing" className="text-zinc-400 hover:text-white transition">Pricing</Link>
            <Link href="/demo" className="text-zinc-400 hover:text-white transition">Demo</Link>
            <Link href="/roi" className="text-zinc-400 hover:text-white transition">ROI Calculator</Link>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-zinc-400 hover:text-white transition hidden sm:block">
              Sign in
            </Link>
            <Link
              href="/signup"
              className="bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-4 py-2 rounded-lg transition"
            >
              Start Trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-amber-500/5 to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-amber-500/5 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-6 relative">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-sm mb-8">
              <Star className="w-4 h-4 text-amber-500" />
              <span>Trusted by 500+ businesses worldwide</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              Your AI Receptionist.{' '}
              <span className="text-amber-500">Working 24/7.</span>
            </h1>
            
            <p className="text-xl text-zinc-400 mb-10 max-w-2xl mx-auto">
              Handle calls, book appointments, capture leads — while you focus on what matters.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link
                href="/signup"
                className="bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-8 py-4 rounded-lg inline-flex items-center gap-2 transition"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/demo"
                className="bg-zinc-800 hover:bg-zinc-700 text-white font-semibold px-8 py-4 rounded-lg inline-flex items-center gap-2 transition"
              >
                <Play className="w-5 h-5" />
                Watch Demo
              </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
              <div className="text-center">
                <div className="text-3xl font-bold text-amber-500 mb-1">{stats.calls_today.toLocaleString()}+</div>
                <div className="text-zinc-500 text-sm">Calls today</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-amber-500 mb-1">{stats.companies_active}+</div>
                <div className="text-zinc-500 text-sm">Active businesses</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-amber-500 mb-1">{stats.uptime_percentage}%</div>
                <div className="text-zinc-500 text-sm">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-amber-500 mb-1">&lt;1s</div>
                <div className="text-zinc-500 text-sm">Response time</div>
              </div>
            </div>

            {/* Wave Animation */}
            <div className="flex items-end justify-center gap-1 h-16">
              {[...Array(12)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 bg-amber-500/60 rounded-t"
                  style={{
                    height: `${20 + Math.sin(i * 0.5) * 30}%`,
                    animationDelay: `${i * 0.1}s`,
                    animation: 'wave 1.5s ease-in-out infinite',
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section className="py-20 bg-zinc-900/50">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Try it now — hear your AI receptionist</h2>
            <p className="text-zinc-400">Select your industry and experience a live demo</p>
          </div>

          <div className="max-w-3xl mx-auto">
            <div className="flex justify-center gap-2 mb-8">
              {industries.map((ind) => (
                <button
                  key={ind.id}
                  onClick={() => setSelectedIndustry(ind.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    selectedIndustry === ind.id
                      ? 'bg-amber-500 text-zinc-950'
                      : 'bg-zinc-800 text-zinc-400 hover:text-white'
                  }`}
                >
                  {ind.icon} {ind.name}
                </button>
              ))}
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center">
              <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Phone className="w-8 h-8 text-amber-500" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                {industries.find((i) => i.id === selectedIndustry)?.name} Demo
              </h3>
              <p className="text-zinc-400 mb-6">
                Click below to start a live conversation with our AI receptionist
              </p>
              <Link
                href={`/demo?industry=${selectedIndustry}`}
                className="inline-flex items-center gap-2 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-6 py-3 rounded-lg transition"
              >
                <Play className="w-5 h-5" />
                Start Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">How It Works</h2>
            <p className="text-zinc-400">Get started in 3 simple steps</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: '01', title: 'Sign up', description: 'Create your account in 30 seconds. No credit card required.', icon: Users },
              { step: '02', title: 'Configure', description: 'Set up your AI agent with custom prompts and voice in 10 minutes.', icon: Zap },
              { step: '03', title: 'Go live', description: 'Connect your phone number and start handling calls instantly.', icon: Phone },
            ].map((item, i) => (
              <div key={i} className="relative text-center">
                <div className="w-20 h-20 bg-amber-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <item.icon className="w-10 h-10 text-amber-500" />
                </div>
                <h3 className="text-2xl font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-zinc-400">{item.description}</p>
                {i < 2 && (
                  <div className="hidden md:block absolute top-10 left-[60%] w-[80%] h-0.5 bg-zinc-800" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-zinc-900/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-zinc-400">Everything you need to automate your phone support</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {features.map((feature, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl hover:border-zinc-700 transition">
                <feature.icon className="w-12 h-12 text-amber-500 mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-zinc-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Industry Verticals */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Industry Solutions</h2>
            <p className="text-zinc-400">Specialized AI agents for your industry</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              {
                icon: '🦷',
                name: 'Dental',
                price: '$399/mo',
                features: ['Insurance verification', 'Emergency detection', 'Appointment booking'],
                popular: true,
              },
              {
                icon: '⚖️',
                name: 'Legal',
                price: '$599/mo',
                features: ['Case intake', 'Conflict check', 'Consultation scheduling'],
                popular: false,
              },
              {
                icon: '🏠',
                name: 'Realty',
                price: '$299/mo',
                features: ['Buyer qualification', 'Showing scheduling', 'Hot lead alerts'],
                popular: false,
              },
            ].map((vertical, i) => (
              <div
                key={i}
                className={`bg-zinc-900 border rounded-xl p-6 ${
                  vertical.popular ? 'border-amber-500' : 'border-zinc-800'
                }`}
              >
                {vertical.popular && (
                  <div className="bg-amber-500 text-zinc-950 text-xs font-bold px-3 py-1 rounded-full inline-block mb-4">
                    Most Popular
                  </div>
                )}
                <div className="text-4xl mb-4">{vertical.icon}</div>
                <h3 className="text-xl font-semibold text-white mb-1">{vertical.name}</h3>
                <div className="text-2xl font-bold text-amber-500 mb-4">{vertical.price}</div>
                <ul className="space-y-2 mb-6">
                  {vertical.features.map((feature, j) => (
                    <li key={j} className="flex items-center gap-2 text-zinc-400">
                      <CheckCircle className="w-4 h-4 text-amber-500" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  href={`/signup?industry=${vertical.name.toLowerCase()}`}
                  className="block text-center bg-zinc-800 hover:bg-zinc-700 text-white font-medium py-2 rounded-lg transition"
                >
                  Learn More
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-zinc-900/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">What Our Customers Say</h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {testimonials.map((testimonial) => (
              <div key={testimonial.id} className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl">
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-amber-500 text-amber-500" />
                  ))}
                </div>
                <p className="text-zinc-300 mb-6">"{testimonial.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-amber-500/20 rounded-full flex items-center justify-center text-amber-500 font-bold">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="font-medium text-white">{testimonial.name}</div>
                    <div className="text-sm text-zinc-500">{testimonial.company}, {testimonial.city}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Simple, Transparent Pricing</h2>
            <p className="text-zinc-400 mb-8">No hidden fees. Cancel anytime.</p>
            
            <div className="inline-flex bg-zinc-900 p-1 rounded-lg">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                  billingCycle === 'monthly' ? 'bg-amber-500 text-zinc-950' : 'text-zinc-400 hover:text-white'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('annual')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                  billingCycle === 'annual' ? 'bg-amber-500 text-zinc-950' : 'text-zinc-400 hover:text-white'
                }`}
              >
                Annual <span className="text-xs text-green-500 ml-1">(Save 20%)</span>
              </button>
            </div>
          </div>
          
          <div className="grid md:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`bg-zinc-900 border rounded-xl p-6 ${
                  plan.popular ? 'border-amber-500' : 'border-zinc-800'
                }`}
              >
                {plan.popular && (
                  <div className="bg-amber-500 text-zinc-950 text-xs font-bold px-3 py-1 rounded-full inline-block mb-4">
                    Most Popular
                  </div>
                )}
                <h3 className="text-xl font-semibold text-white mb-2">{plan.name}</h3>
                <div className="mb-4">
                  {plan.price === null ? (
                    <span className="text-3xl font-bold text-white">Custom</span>
                  ) : (
                    <>
                      <span className="text-3xl font-bold text-white">${billingCycle === 'monthly' ? plan.price : Math.round(plan.yearlyPrice / 12)}</span>
                      <span className="text-zinc-500">/month</span>
                    </>
                  )}
                </div>
                <div className="text-sm text-zinc-500 mb-4">{plan.calls} calls/month</div>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-center gap-2 text-zinc-400 text-sm">
                      <CheckCircle className="w-4 h-4 text-amber-500 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  href={`/signup?plan=${plan.id}`}
                  className={`block text-center py-3 rounded-lg font-semibold transition ${
                    plan.popular
                      ? 'bg-amber-500 hover:bg-amber-400 text-zinc-950'
                      : 'bg-zinc-800 hover:bg-zinc-700 text-white'
                  }`}
                >
                  Start Free Trial
                </Link>
              </div>
            ))}
          </div>

          <p className="text-center text-zinc-500 mt-8">
            All plans include 24/7 uptime, SSL security, and cancel anytime
          </p>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-zinc-900/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Frequently Asked Questions</h2>
          </div>
          
          <div className="max-w-3xl mx-auto space-y-4">
            {faqs.map((faq, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-zinc-800/50 transition"
                >
                  <span className="font-medium text-white">{faq.q}</span>
                  {openFaq === i ? (
                    <ChevronUp className="w-5 h-5 text-zinc-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-zinc-400" />
                  )}
                </button>
                {openFaq === i && (
                  <div className="px-4 pb-4 text-zinc-400">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="bg-gradient-to-r from-amber-500/20 to-amber-500/5 rounded-2xl p-12 text-center max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to never miss a call again?
            </h2>
            <p className="text-xl text-zinc-400 mb-8">
              Join 500+ businesses already using VoiceCore
            </p>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-8 py-4 rounded-lg transition"
            >
              Start Free Trial — No Credit Card Required
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
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
              <span className="text-lg font-bold text-white">VoiceCore</span>
            </div>
            <div className="flex items-center gap-6 text-zinc-400">
              <Link href="/legal/privacy" className="hover:text-white transition">Privacy</Link>
              <Link href="/legal/terms" className="hover:text-white transition">Terms</Link>
              <Link href="/legal/hipaa" className="hover:text-white transition">HIPAA</Link>
              <Link href="/pricing" className="hover:text-white transition">Pricing</Link>
            </div>
            <div className="text-zinc-500 text-sm">
              © {new Date().getFullYear()} VoiceCore. All rights reserved.
            </div>
          </div>
        </div>
      </footer>

      <style jsx global>{`
        @keyframes wave {
          0%, 100% { transform: scaleY(1); }
          50% { transform: scaleY(0.5); }
        }
      `}</style>
    </div>
  );
}
