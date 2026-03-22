import Link from 'next/link';
import { Phone, Shield, Lock, CheckCircle, FileText, Building, AlertTriangle } from 'lucide-react';

export default function HIPAAPage() {
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
              href="/signup?plan=business"
              className="bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-4 py-2 rounded-lg transition"
            >
              Get HIPAA-Ready
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-4">
            <Shield className="w-5 h-5 text-green-500" />
            <span className="text-green-500 font-medium">HIPAA Compliant</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">HIPAA Compliance</h1>
          <p className="text-xl text-zinc-400">
            Enterprise-grade security for healthcare and compliant industries
          </p>

          <div className="flex items-center justify-center gap-4 mt-6">
            <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
              <Lock className="w-4 h-4 text-green-500" />
              <span className="text-xs text-green-500">AES-256 Encryption</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full">
              <Shield className="w-4 h-4 text-blue-500" />
              <span className="text-xs text-blue-500">SOC 2 (In Progress)</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-zinc-700/50 border border-zinc-600 rounded-full">
              <Shield className="w-4 h-4 text-zinc-400" />
              <span className="text-xs text-zinc-400">SSL Secured</span>
            </div>
          </div>
        </div>

        <div className="prose prose-invert max-w-none space-y-8 text-zinc-300">
          <section>
            <h2 className="text-2xl font-bold text-white mb-4">1. HIPAA Overview</h2>
            <p>
              The Health Insurance Portability and Accountability Act (HIPAA) sets the standard for protecting sensitive patient health information (PHI). Healthcare providers, insurers, and their business associates must ensure all PHI is handled in compliance with HIPAA regulations.
            </p>
            <p className="mt-2">
              VoiceCore is designed to help covered entities meet HIPAA requirements with built-in security features, audit logging, and Business Associate Agreement (BAA) support.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">2. How VoiceCore Protects PHI</h2>

            <div className="grid gap-4 mt-4">
              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Lock className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-white">Encryption at Rest</h3>
                    <p className="text-zinc-400 text-sm mt-1">
                      All PHI is encrypted using AES-256-GCM encryption before storage. This ensures that even if data is accessed without authorization, it remains unreadable.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Shield className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-white">Encryption in Transit</h3>
                    <p className="text-zinc-400 text-sm mt-1">
                      All data transmitted to and from VoiceCore is protected with TLS 1.3 encryption, ensuring end-to-end security.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <FileText className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-white">Access Controls & Audit Logging</h3>
                    <p className="text-zinc-400 text-sm mt-1">
                      Role-based access control (RBAC) ensures only authorized personnel can access PHI. All access is logged and retained for 6 years per HIPAA requirements.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Building className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-white">Employee Training & Policies</h3>
                    <p className="text-zinc-400 text-sm mt-1">
                      All VoiceCore employees with access to customer data undergo annual HIPAA training and background checks.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">3. Business Associate Agreement (BAA)</h2>
            <p>
              A Business Associate Agreement (BAA) is required when a covered entity works with a third party that will have access to PHI. VoiceCore offers signed BAAs for all Business and Enterprise customers.
            </p>

            <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 mt-4">
              <h3 className="font-semibold text-amber-500 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Important
              </h3>
              <p className="text-zinc-300 text-sm mt-2">
                HIPAA features are only available on Business and Enterprise plans. You must sign a BAA before processing any PHI with VoiceCore.
              </p>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 mt-4">
              <h3 className="font-semibold text-white mb-2">The BAA includes:</h3>
              <ul className="space-y-2">
                {[
                  'Agreement to not use or disclose PHI except as permitted',
                  'Implementation of appropriate safeguards',
                  'Reporting of security incidents',
                  'Assurance of subcontractor compliance',
                  'Access to PHI for compliance audits',
                  'Data return and destruction policies',
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                    <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            <Link
              href="/dashboard/settings/hipaa"
              className="inline-flex items-center gap-2 bg-green-500 hover:bg-green-400 text-white font-semibold px-6 py-3 rounded-lg mt-4 transition"
            >
              <FileText className="w-5 h-5" />
              Sign BAA Online
            </Link>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">4. Data Center Security</h2>
            <p>
              VoiceCore infrastructure is hosted on AWS in the following regions:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4 mt-2">
              <li><strong>us-east-1</strong> (Virginia, USA)</li>
              <li><strong>us-west-2</strong> (Oregon, USA)</li>
            </ul>
            <p className="mt-2">
              All data centers are SOC 2 Type II certified and maintain compliance with industry standards including ISO 27001 and SOC 2.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">5. Breach Notification Policy</h2>
            <p>
              In the event of a breach of unsecured PHI, VoiceCore will:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4 mt-2">
              <li>Notify affected covered entities within 24 hours of discovery</li>
              <li>Provide detailed information about the breach</li>
              <li>Assist with required regulatory notifications</li>
              <li>Conduct a thorough investigation</li>
              <li>Implement corrective measures to prevent future incidents</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">6. Covered Entities FAQ</h2>
            
            <div className="space-y-4 mt-4">
              {[
                {
                  q: 'What types of healthcare providers can use VoiceCore?',
                  a: 'VoiceCore is suitable for dental practices, medical clinics, mental health providers, pharmacies, and any healthcare-related business that handles patient calls.',
                },
                {
                  q: 'Can we use VoiceCore without signing a BAA?',
                  a: 'No. HIPAA features require a signed BAA. Without it, you should not process any PHI through VoiceCore.',
                },
                {
                  q: 'How long are call recordings retained?',
                  a: 'For HIPAA customers, recordings are retained for 90 days by default. This can be configured based on your compliance requirements.',
                },
                {
                  q: 'Can we export PHI if we cancel?',
                  a: 'Yes, you can export all your data before account deletion. Data is available for 30 days after cancellation.',
                },
              ].map((faq, i) => (
                <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
                  <h3 className="font-medium text-white">{faq.q}</h3>
                  <p className="text-zinc-400 text-sm mt-1">{faq.a}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="bg-green-500/10 border border-green-500/20 rounded-xl p-6">
            <h2 className="text-2xl font-bold text-white mb-4">Get HIPAA-Ready in Minutes</h2>
            <p className="text-zinc-300 mb-6">
              Start your 14-day free trial on the Business plan to access HIPAA-compliant features and sign a BAA.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/signup?plan=business"
                className="inline-flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-6 py-3 rounded-lg transition"
              >
                Start Business Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/contact"
                className="inline-flex items-center justify-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold px-6 py-3 rounded-lg transition"
              >
                Contact Sales
              </Link>
            </div>
          </section>
        </div>

        <div className="mt-12 pt-8 border-t border-zinc-800 text-center">
          <p className="text-zinc-500">
            Questions about HIPAA compliance? Contact our HIPAA Officer:<br />
            <strong className="text-zinc-400">hipaa@voicecore.ai</strong>
          </p>
        </div>
      </main>

      <footer className="py-12 border-t border-zinc-800 mt-16">
        <div className="container mx-auto px-6 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
              <Phone className="w-4 h-4 text-zinc-950" />
            </div>
            <span className="text-lg font-bold text-white">VoiceCore</span>
          </div>
          <div className="flex items-center justify-center gap-4 text-zinc-400 text-sm">
            <Link href="/legal/terms" className="hover:text-white">Terms</Link>
            <Link href="/legal/privacy" className="hover:text-white">Privacy</Link>
            <Link href="/legal/hipaa" className="hover:text-white">HIPAA</Link>
          </div>
          <p className="text-zinc-500 text-sm mt-4">
            © {new Date().getFullYear()} VoiceCore. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
