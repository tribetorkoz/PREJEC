'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Phone, Mail, Lock, Eye, EyeOff, Building2, User, ArrowRight, Loader2 } from 'lucide-react';
import { z } from 'zod';

const signupSchema = z.object({
  company_name: z.string().min(2, 'Company name must be at least 2 characters'),
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  industry: z.string().min(1, 'Please select an industry'),
  phone: z.string().min(10, 'Valid phone number required'),
  agreed_terms: z.boolean().refine(val => val === true, 'You must agree to the terms'),
});

type SignupFormData = z.infer<typeof signupSchema>;

const INDUSTRIES = [
  'Healthcare', 'Restaurants', 'Real Estate', 'Legal', 'Finance', 'Retail', 'Other'
];

export default function SignupPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const plan = searchParams.get('plan') || 'starter';

  const [formData, setFormData] = useState<SignupFormData>({
    company_name: '',
    full_name: '',
    email: '',
    password: '',
    industry: '',
    phone: '',
    agreed_terms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState('');

  const passwordStrength = () => {
    if (!formData.password) return 0;
    let strength = 0;
    if (formData.password.length >= 8) strength++;
    if (/[A-Z]/.test(formData.password)) strength++;
    if (/[0-9]/.test(formData.password)) strength++;
    if (/[^A-Za-z0-9]/.test(formData.password)) strength++;
    return strength;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    setServerError('');

    try {
      signupSchema.parse(formData);
    } catch (err) {
      if (err instanceof z.ZodError) {
        const fieldErrors: Record<string, string> = {};
        err.errors.forEach((error) => {
          if (error.path[0]) {
            fieldErrors[error.path[0] as string] = error.message;
          }
        });
        setErrors(fieldErrors);
        setLoading(false);
        return;
      }
    }

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: formData.company_name,
          full_name: formData.full_name,
          email: formData.email,
          password: formData.password,
          phone: formData.phone,
          industry: formData.industry,
          plan: plan,
        }),
        credentials: 'include',
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        router.push('/onboarding');
      }
    } catch (err: any) {
      setServerError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignup = () => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/google?plan=${plan}`;
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex">
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-amber-500/20 to-zinc-900 items-center justify-center p-12">
        <div className="max-w-md">
          <h2 className="text-4xl font-bold text-white mb-6">Start your free trial</h2>
          <p className="text-zinc-400 text-lg mb-8">Get started in minutes. No credit card required.</p>
          <ul className="space-y-4">
            {['14-day free trial', 'Full access to all features', 'Setup in 5 minutes', 'Cancel anytime'].map((item, i) => (
              <li key={i} className="flex items-center gap-3 text-zinc-300">
                <div className="w-6 h-6 bg-amber-500/20 rounded-full flex items-center justify-center">
                  <span className="text-amber-500 text-sm">✓</span>
                </div>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <Link href="/" className="flex items-center gap-2 mb-8">
            <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
              <Phone className="w-6 h-6 text-zinc-950" />
            </div>
            <span className="text-xl font-bold text-white">VoiceCore</span>
          </Link>

          <h1 className="text-2xl font-bold text-white mb-2">Create your account</h1>
          <p className="text-zinc-400 mb-6">
            Selected plan: <span className="text-amber-500 font-medium capitalize">{plan}</span>
          </p>

          <button
            onClick={handleGoogleSignup}
            className="w-full flex items-center justify-center gap-3 bg-white text-zinc-950 py-3 rounded-lg font-medium hover:bg-zinc-100 transition mb-6"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign up with Google
          </button>

          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 h-px bg-zinc-800"></div>
            <span className="text-zinc-500 text-sm">or sign up with email</span>
            <div className="flex-1 h-px bg-zinc-800"></div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {serverError && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg text-sm">
                {serverError}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Company name</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input
                  type="text"
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-11 pr-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="Acme Inc."
                  required
                />
              </div>
              {errors.company_name && <p className="text-red-500 text-xs mt-1">{errors.company_name}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Full name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-11 pr-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="John Doe"
                  required
                />
              </div>
              {errors.full_name && <p className="text-red-500 text-xs mt-1">{errors.full_name}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Work email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-11 pr-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="john@company.com"
                  required
                />
              </div>
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-11 pr-12 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="Min 8 characters"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              <div className="mt-2 flex gap-1">
                {[1, 2, 3, 4].map((level) => (
                  <div
                    key={level}
                    className={`h-1 flex-1 rounded ${passwordStrength() >= level ? (level <= 1 ? 'bg-red-500' : level <= 2 ? 'bg-yellow-500' : 'bg-green-500') : 'bg-zinc-800'}`}
                  />
                ))}
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Industry</label>
              <select
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                required
              >
                <option value="">Select industry</option>
                {INDUSTRIES.map((ind) => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
              {errors.industry && <p className="text-red-500 text-xs mt-1">{errors.industry}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Phone number</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                placeholder="+1 (555) 000-0000"
                required
              />
              {errors.phone && <p className="text-red-500 text-xs mt-1">{errors.phone}</p>}
            </div>

            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="terms"
                checked={formData.agreed_terms}
                onChange={(e) => setFormData({ ...formData, agreed_terms: e.target.checked })}
                className="mt-1 w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-amber-500 focus:ring-amber-500"
              />
              <label htmlFor="terms" className="text-sm text-zinc-400">
                I agree to the <Link href="/terms" className="text-amber-500 hover:underline">Terms of Service</Link> and <Link href="/privacy" className="text-amber-500 hover:underline">Privacy Policy</Link>
              </label>
            </div>
            {errors.agreed_terms && <p className="text-red-500 text-xs">{errors.agreed_terms}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-amber-500 hover:bg-amber-600 text-zinc-950 font-semibold py-3 rounded-lg transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>Create account <ArrowRight className="w-5 h-5" /></>}
            </button>
          </form>

          <p className="text-center text-zinc-400 mt-6">
            Already have an account? <Link href="/login" className="text-amber-500 hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
