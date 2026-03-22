import Link from 'next/link';
import { Phone, Shield, Globe, Lock } from 'lucide-react';

export default function PrivacyPage() {
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
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">Privacy Policy</h1>
          <p className="text-zinc-400">Last updated: March 21, 2026</p>
          
          <div className="flex items-center justify-center gap-4 mt-6">
            <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
              <Shield className="w-4 h-4 text-green-500" />
              <span className="text-xs text-green-500">GDPR Compliant</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full">
              <Globe className="w-4 h-4 text-blue-500" />
              <span className="text-xs text-blue-500">CCPA Compliant</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full">
              <Lock className="w-4 h-4 text-purple-500" />
              <span className="text-xs text-purple-500">HIPAA Ready</span>
            </div>
          </div>
        </div>

        <div className="prose prose-invert max-w-none space-y-8 text-zinc-300">
          <section>
            <h2 className="text-2xl font-bold text-white mb-4">1. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold text-white mb-2">Account Data</h3>
            <p>When you register for VoiceCore, we collect:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Name and email address</li>
              <li>Company name and contact information</li>
              <li>Billing information (processed securely by Stripe)</li>
              <li>Phone numbers you provision or port to VoiceCore</li>
            </ul>

            <h3 className="text-xl font-semibold text-white mb-2 mt-4">Call Data</h3>
            <p>We collect and process:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Call recordings and transcripts</li>
              <li>Caller phone numbers and metadata</li>
              <li>Call duration and timestamps</li>
              <li>Sentiment analysis and outcome data</li>
            </ul>

            <h3 className="text-xl font-semibold text-white mb-2 mt-4">Usage Data</h3>
            <p>We collect information about how you use VoiceCore, including:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Features used and configuration settings</li>
              <li>API calls and integration usage</li>
              <li>Dashboard interactions</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">2. How We Use Information</h2>
            <p>We use collected information to:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Provide and maintain the VoiceCore service</li>
              <li>Process calls and generate transcripts</li>
              <li>Send service-related notifications</li>
              <li>Provide customer support</li>
              <li>Improve our AI models and service quality</li>
              <li>Detect and prevent fraud or abuse</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">3. Data Sharing</h2>
            <p>
              <strong>We NEVER sell your data.</strong> We share information only in the following circumstances:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li><strong>Service Providers:</strong> With third-party vendors who help us deliver the service (Twilio, ElevenLabs, AWS, Stripe)</li>
              <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
              <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
              <li><strong>With Your Consent:</strong> When you explicitly authorize sharing</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">4. Data Storage and Security</h2>
            <p>We implement industry-standard security measures:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li><strong>Encryption at Rest:</strong> AES-256-GCM encryption for all stored data</li>
              <li><strong>Encryption in Transit:</strong> TLS 1.3 for all data transmission</li>
              <li><strong>Access Controls:</strong> Role-based access control and audit logging</li>
              <li><strong>SOC 2 Type II:</strong> Infrastructure certified (in progress)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">5. Data Retention</h2>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li><strong>Call Recordings:</strong> Retained for 90 days (configurable)</li>
              <li><strong>Transcripts:</strong> Retained for 1 year with PII masked</li>
              <li><strong>Account Data:</strong> Retained until account deletion</li>
              <li><strong>Call Metadata:</strong> Retained for 7 years for compliance</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">6. Your Rights (GDPR)</h2>
            <p>If you are located in the European Economic Area, you have the right to:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Rectification:</strong> Correct inaccurate personal data</li>
              <li><strong>Erasure:</strong> Request deletion of your data (&quot;right to be forgotten&quot;)</li>
              <li><strong>Restriction:</strong> Request restriction of processing</li>
              <li><strong>Portability:</strong> Receive your data in a portable format</li>
              <li><strong>Object:</strong> Object to processing based on legitimate interests</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">7. California Residents (CCPA)</h2>
            <p>Under the California Consumer Privacy Act, California residents have additional rights:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Right to know what personal information is collected</li>
              <li>Right to know if personal information is sold or shared</li>
              <li>Right to non-discrimination for exercising your rights</li>
              <li>Right to request deletion of personal information</li>
              <li>Right to opt-out of the sale of personal information</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">8. Children&apos;s Privacy</h2>
            <p>
              VoiceCore is not intended for users under 18 years of age. We do not knowingly collect personal information from children.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">9. HIPAA Section</h2>
            <p>
              For healthcare customers on Business or Enterprise plans, VoiceCore offers HIPAA-compliant services. Please see our <Link href="/legal/hipaa" className="text-amber-500 hover:underline">HIPAA Compliance page</Link> for details on protected health information (PHI) handling.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">10. Contact for Privacy Requests</h2>
            <p>
              To exercise your privacy rights or ask questions about this policy:<br />
              <strong>Email:</strong> privacy@voicecore.ai<br />
              <strong>Response Time:</strong> Within 30 days
            </p>
          </section>
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
