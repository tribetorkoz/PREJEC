import Link from 'next/link';
import { Phone } from 'lucide-react';

export default function TermsPage() {
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
          <h1 className="text-4xl font-bold text-white mb-4">Terms of Service</h1>
          <p className="text-zinc-400">Last updated: March 21, 2026</p>
        </div>

        <div className="prose prose-invert max-w-none space-y-8 text-zinc-300">
          <section>
            <h2 className="text-2xl font-bold text-white mb-4">1. Acceptance of Terms</h2>
            <p>
              By accessing or using VoiceCore (&quot;the Service&quot;), you agree to be bound by these Terms of Service (&quot;Terms&quot;). If you do not agree to these Terms, do not use the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">2. Description of Service</h2>
            <p>
              VoiceCore provides AI-powered voice receptionist services, including call handling, appointment scheduling, and customer interaction management through artificial intelligence agents.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">3. Account Registration</h2>
            <p>
              You must register for an account to use the Service. You agree to provide accurate, current, and complete information during registration and to update such information to keep it accurate. You are responsible for maintaining the confidentiality of your account credentials.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">4. Subscription and Payment</h2>
            
            <h3 className="text-xl font-semibold text-white mb-2">Billing Cycles</h3>
            <p>
              Subscriptions are billed monthly or annually in advance. Annual subscriptions receive a 20% discount applied to the monthly rate.
            </p>

            <h3 className="text-xl font-semibold text-white mb-2 mt-4">Refund Policy</h3>
            <p>
              Monthly plans are non-refundable. Annual plans may receive a pro-rata refund within the first 30 days of the subscription period. After 30 days, no refunds are provided for annual subscriptions.
            </p>

            <h3 className="text-xl font-semibold text-white mb-2 mt-4">Failed Payment Grace Period</h3>
            <p>
              If a payment fails, your account will continue to operate for a 7-day grace period. During this time, your AI agent will continue handling calls. If payment is not received within 7 days, your account may be suspended.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">5. Usage Limits and Fair Use</h2>
            <p>
              Each subscription plan includes monthly call limits as specified in your plan. Exceeding your plan limits may result in additional charges or call queuing. We reserve the right to suspend accounts that exceed fair use thresholds.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">6. Prohibited Uses</h2>
            <p>You may not use the Service to:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Violate any applicable laws or regulations</li>
              <li>Infringe on intellectual property rights</li>
              <li>Harass, abuse, or harm other users</li>
              <li>Send unsolicited marketing or spam</li>
              <li>Attempt to gain unauthorized access to the Service</li>
              <li>Use the Service for any fraudulent or deceptive purpose</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">7. Privacy and Data Protection</h2>
            <p>
              Your use of the Service is also governed by our Privacy Policy. We collect and process personal data in accordance with applicable privacy laws, including GDPR and CCPA where applicable.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">8. Call Recording and Transcription Notice</h2>
            <p>
              By using VoiceCore, you acknowledge and agree that calls may be recorded and transcribed for quality assurance and service improvement purposes. You are solely responsible for complying with applicable wiretapping and call recording laws in your jurisdiction, including obtaining necessary consent from callers.
            </p>
            <p className="mt-2">
              You must inform callers that calls may be recorded through an appropriate disclosure or greeting.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">9. Intellectual Property</h2>
            <p>
              VoiceCore retains all rights to the Service, including the software, algorithms, and trademarks. You retain rights to your content, including business information and custom prompts.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">10. Indemnification</h2>
            <p>
              You agree to indemnify and hold VoiceCore harmless from any claims, damages, or expenses arising from your use of the Service or your violation of these Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">11. Limitation of Liability</h2>
            <p>
              <strong>IMPORTANT:</strong> VoiceCore&apos;s total liability for any claims arising from the Service shall not exceed the amount you paid for the Service in the three (3) months preceding the claim. In no event shall VoiceCore be liable for indirect, incidental, special, or consequential damages.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">12. Termination</h2>
            <p>
              You may terminate your subscription at any time through your account settings. VoiceCore may suspend or terminate your access to the Service if you violate these Terms. Upon termination, your data will be retained for 30 days before permanent deletion.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">13. Changes to Terms</h2>
            <p>
              We may update these Terms from time to time. We will notify you of material changes via email or through the Service. Your continued use of the Service after changes constitutes acceptance of the updated Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">14. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of the State of Delaware, USA, without regard to its conflict of law provisions.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">15. Contact Information</h2>
            <p>
              For questions about these Terms, please contact us at:<br />
              <strong>Email:</strong> legal@voicecore.ai<br />
              <strong>Address:</strong> VoiceCore LLC, Delaware, USA
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
          <p className="text-zinc-500 text-sm">
            © {new Date().getFullYear()} VoiceCore. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
