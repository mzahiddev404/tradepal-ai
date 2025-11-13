import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { AlertTriangle } from "lucide-react";

export default function DisclaimerPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto p-4 sm:p-6 lg:p-8 max-w-4xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <h1 className="text-2xl sm:text-3xl font-semibold text-slate-900">Disclaimer</h1>
          <div className="flex flex-wrap gap-2">
            <Link href="/market">
              <Button variant="outline" className="h-9 border-slate-300 text-slate-700 hover:bg-slate-50">
                Market Data
              </Button>
            </Link>
            <Link href="/">
              <Button variant="outline" className="h-9 border-slate-300 text-slate-700 hover:bg-slate-50">
                Chat
              </Button>
            </Link>
          </div>
        </div>

        <Card className="p-6 sm:p-8 space-y-6 border-slate-200 bg-white">
          <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h2 className="font-semibold text-amber-900 mb-1">
                Important Notice
              </h2>
              <p className="text-sm text-amber-800">
                This is a demonstration application for educational and development purposes only.
              </p>
            </div>
          </div>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">1. Demo Application</h2>
            <p className="text-slate-700 leading-relaxed">
              TradePal AI is a demonstration application created for educational and development
              purposes. This application is not intended for actual trading, investment decisions, or
              financial advice.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">2. No Financial Advice</h2>
            <p className="text-slate-700 leading-relaxed">
              The information provided by this application, including but not limited to stock quotes,
              options data, market analysis, and AI-generated responses, is for informational
              purposes only. It does not constitute financial, investment, legal, or tax advice. You
              should not rely on this information to make investment decisions.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">3. Market Data Disclaimer</h2>
            <p className="text-slate-700 leading-relaxed">
              Stock prices, options data, and market information displayed in this application are
              provided by third-party data sources and may be delayed, inaccurate, or incomplete. The
              developers of this application do not guarantee the accuracy, completeness, or timeliness
              of any market data. Real-time data may not be available, and prices shown may not reflect
              current market conditions.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">4. Investment Risks</h2>
            <p className="text-slate-700 leading-relaxed">
              Trading stocks, options, and other securities involves substantial risk of loss. Past
              performance is not indicative of future results. You may lose some or all of your
              investment. Options trading involves additional risks and is not suitable for all
              investors. Please consult with a licensed financial advisor before making any investment
              decisions.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">5. No Liability</h2>
            <p className="text-slate-700 leading-relaxed">
              The developers, contributors, and operators of TradePal AI (collectively, &quot;we&quot;, &quot;us&quot;, or
              &quot;our&quot;) shall not be held liable for any losses, damages, or expenses arising from:
            </p>
            <ul className="list-disc list-inside space-y-2 text-slate-700 ml-4">
              <li>Your use or inability to use this application</li>
              <li>Any errors, inaccuracies, or omissions in the data or information provided</li>
              <li>Any decisions made based on information from this application</li>
              <li>Any financial losses incurred from trading or investment activities</li>
              <li>Technical failures, interruptions, or errors in the application</li>
              <li>Any unauthorized access to your data or information</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">6. AI-Generated Content</h2>
            <p className="text-slate-700 leading-relaxed">
              Responses generated by the AI assistant in this application are created by artificial
              intelligence and may contain errors, inaccuracies, or outdated information. AI-generated
              content should not be relied upon for making financial or investment decisions. Always
              verify information from multiple reliable sources and consult with qualified
              professionals.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">7. Third-Party Services</h2>
            <p className="text-slate-700 leading-relaxed">
              This application may use third-party services and APIs for data and functionality. We
              are not responsible for the availability, accuracy, or terms of service of these
              third-party providers. Your use of third-party services is subject to their respective
              terms and conditions.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">8. No Warranty</h2>
            <p className="text-slate-700 leading-relaxed">
              This application is provided &quot;as is&quot; without any warranties, express or implied,
              including but not limited to warranties of merchantability, fitness for a particular
              purpose, or non-infringement. We do not warrant that the application will be
              uninterrupted, error-free, or secure.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">9. Regulatory Compliance</h2>
            <p className="text-slate-700 leading-relaxed">
              This application is not registered with any financial regulatory authority and is not
              intended to provide regulated financial services. If you require financial services,
              please consult with licensed and registered financial professionals.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">10. Acceptance of Terms</h2>
            <p className="text-slate-700 leading-relaxed">
              By using this application, you acknowledge that you have read, understood, and agree to
              this disclaimer. You understand that this is a demo application and that you use it at
              your own risk. If you do not agree with any part of this disclaimer, you should not use
              this application.
            </p>
          </section>

          <div className="pt-6 border-t border-slate-200">
            <p className="text-sm text-slate-600">
              <strong className="text-slate-900">Last Updated:</strong> December 2024
            </p>
            <p className="text-sm text-slate-600 mt-2">
              If you have any questions about this disclaimer, please contact the development team.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
