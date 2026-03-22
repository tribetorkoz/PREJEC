'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Phone, Check, X, ArrowRight, MessageSquare } from 'lucide-react';

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    yearlyPrice: 0,
    calls: '50',
    agents: '1',
    languages: '3',
    popular: false,
    features: [
      { name: 'Basic analytics', included: true },
      { name: '1 AI agent', included: true },
      { name: '3 languages', included: true },
      { name: 'Calendar integration', included: false },
      { name: 'CRM integration', included: false },
      { name: 'HIPAA compliance', included: false },
      { name: 'White-label', included: false },
      { name: 'Priority support', included: false },
    ],
  },
  {
    id: 'starter',
    name: 'Starter',
    price: 99,
    yearlyPrice: 950,
    calls: '500',
    agents: '3',
    languages: '10',
    popular: false,
    features: [
      { name: 'Full analytics', included: true },
      { name: '3 AI agents', included: true },
      { name: '10 languages', included: true },
      { name: 'Calendar integration', included: true },
      { name: 'CRM integration', included: false },
      { name: 'HIPAA compliance', included: false },
      { name: 'White-label', included: false },
      { name: 'Priority support', included: false },
    ],
  },
  {
    id: 'business',
    name: 'Business',
    price: 399,
    yearlyPrice: 3830,
    calls: '2,000',
    agents: '10',
    languages: '50+',
    popular: true,
    features: [
      { name: 'Advanced analytics', included: true },
      { name: '10 AI agents', included: true },
      { name: '50+ languages', included: true },
      { name: 'Calendar integration', included: true },
      { name: 'CRM integration', included: true },
      { name: 'HIPAA compliance', included: true },
      { name: 'White-label', included: false },
      { name: 'Priority support', included: false },
    ],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: null,
    yearlyPrice: null,
    calls: 'Unlimited',
    agents: 'Unlimited',
    languages: 'All',
    popular: false,
    features: [
      { name: 'Custom analytics', included: true },
      { name: 'Unlimited AI agents', included: true },
      { name: 'All languages', included: true },
      { name: 'Calendar integration', included: true },
      { name: 'CRM integration', included: true },
      { name: 'HIPAA compliance', included: true },
      { name: 'White-label', included: true },
      { name: 'Dedicated support', included: true },
    ],
  },
];

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="border-b border-zinc-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
                <Phone className="w-6 h-6 text-zinc-950" />
              </div>
              <span className="text-xl font-bold text-white">VoiceCore</span>
            </Link>
            <Link
              href="/signup"
              className="bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-4 py-2 rounded-lg transition"
            >
              Start Free Trial
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-zinc-400 mb-8">
            Choose the plan that fits your business
          </p>

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

        {/* Plan Cards */}
        <div className="grid md:grid-cols-4 gap-6 max-w-6xl mx-auto mb-16">
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
                    <span className="text-3xl font-bold text-white">
                      ${billingCycle === 'monthly' ? plan.price : Math.round(plan.yearlyPrice / 12)}
                    </span>
                    <span className="text-zinc-500">/month</span>
                  </>
                )}
              </div>

              {billingCycle === 'annual' && plan.price !== null && (
                <div className="text-sm text-green-500 mb-4">
                  ${plan.yearlyPrice}/year (save ${plan.price * 12 - plan.yearlyPrice})
                </div>
              )}

              <div className="space-y-2 text-sm text-zinc-500 mb-6">
                <div>{plan.calls} calls/month</div>
                <div>{plan.agents} AI agents</div>
                <div>{plan.languages} languages</div>
              </div>

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

        {/* Feature Comparison Table */}
        <div className="max-w-5xl mx-auto mb-16">
          <h2 className="text-2xl font-bold text-white mb-8 text-center">
            Compare Plans
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="text-left py-4 px-4 text-zinc-400 font-medium">Feature</th>
                  <th className="text-center py-4 px-4 text-zinc-400 font-medium">Free</th>
                  <th className="text-center py-4 px-4 text-zinc-400 font-medium">Starter</th>
                  <th className="text-center py-4 px-4 text-amber-500 font-medium bg-amber-500/10 rounded-t-lg">Business</th>
                  <th className="text-center py-4 px-4 text-zinc-400 font-medium">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Monthly calls', '50', '500', '2,000', 'Unlimited'],
                  ['AI agents', '1', '3', '10', 'Unlimited'],
                  ['Languages', '3', '10', '50+', 'All'],
                  ['Calendar integration', '✗', '✓', '✓', '✓'],
                  ['CRM integration', '✗', '✗', '✓', '✓'],
                  ['Sentiment analysis', '✓', '✓', '✓', '✓'],
                  ['Custom system prompt', '✗', '✓', '✓', '✓'],
                  ['Email notifications', '✓', '✓', '✓', '✓'],
                  ['SMS alerts', '✗', '✗', '✓', '✓'],
                  ['Analytics dashboard', 'Basic', 'Full', 'Full', 'Advanced'],
                  ['HIPAA compliance', '✗', '✗', '✓', '✓'],
                  ['White-label', '✗', '✗', '✗', '✓'],
                  ['Dedicated support', '✗', '✗', '✗', '✓'],
                  ['SLA uptime guarantee', '✗', '✗', '99.9%', '99.99%'],
                ].map((row, i) => (
                  <tr key={i} className="border-b border-zinc-800">
                    <td className="py-4 px-4 text-zinc-300">{row[0]}</td>
                    <td className="py-4 px-4 text-center">{row[1]}</td>
                    <td className="py-4 px-4 text-center">{row[2]}</td>
                    <td className="py-4 px-4 text-center bg-amber-500/5">{row[3]}</td>
                    <td className="py-4 px-4 text-center">{row[4]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-white mb-8 text-center">
            Pricing FAQ
          </h2>

          <div className="space-y-4">
            {[
              {
                q: 'What counts as a call?',
                a: 'A call is any inbound or outbound voice connection handled by your AI agent. Calls are counted from start to finish, regardless of duration.',
              },
              {
                q: 'Can I change plans at any time?',
                a: 'Yes, you can upgrade or downgrade your plan at any time. Upgrades take effect immediately, and downgrades take effect at the start of your next billing cycle.',
              },
              {
                q: 'Is there a free trial?',
                a: 'Yes! All paid plans come with a 14-day free trial with no credit card required. You get full access to all features during the trial.',
              },
              {
                q: 'What happens if I exceed my call limit?',
                a: 'We\'ll notify you when you reach 90% of your limit. Once you reach 100%, additional calls will be queued or you can upgrade to a higher plan.',
              },
              {
                q: 'Do you offer refunds?',
                a: 'We don\'t offer refunds for monthly plans, but you can cancel anytime. For annual plans, we offer pro-rata refunds within the first 30 days.',
              },
            ].map((faq, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
                <h3 className="font-medium text-white mb-2">{faq.q}</h3>
                <p className="text-zinc-400 text-sm">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise CTA */}
        <div className="text-center mt-16 pt-8 border-t border-zinc-800">
          <h3 className="text-xl font-semibold text-white mb-4">
            Need a custom solution?
          </h3>
          <p className="text-zinc-400 mb-6">
            Contact our sales team for volume discounts and custom pricing
          </p>
          <Link
            href="/contact"
            className="inline-flex items-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold px-6 py-3 rounded-lg transition"
          >
            <MessageSquare className="w-5 h-5" />
            Talk to Sales
          </Link>
        </div>
      </main>

      <footer className="py-12 border-t border-zinc-800 mt-16">
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
            </div>
            <div className="text-zinc-500 text-sm">
              © {new Date().getFullYear()} VoiceCore. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
