"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AppHeader } from "@/components/layout/app-header";
import { AlertTriangle } from "lucide-react";

export default function DisclaimerPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1e23] via-[#23272c] to-[#1a1e23]">
      <AppHeader />
      <div className="p-4 sm:p-6 md:p-8">
        <div className="max-w-4xl mx-auto">
          <Card className="border-[#2d3237] bg-[#1a1e23]/95 backdrop-blur-sm shadow-2xl">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[#ff9500] to-[#ff7a00] border-2 border-[#ff9500]">
                  <AlertTriangle className="h-5 w-5 text-white" />
                </div>
                <CardTitle className="text-2xl sm:text-3xl font-bold text-[#dcdcdc]">
                  Disclaimer
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-start gap-3 p-4 bg-[#2d1f1f] border border-[#ff9500]/30 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-[#ff9500] flex-shrink-0 mt-0.5" />
                <div>
                  <h2 className="font-semibold text-[#ffb84d] mb-1">
                    Important Notice
                  </h2>
                  <p className="text-sm text-[#ffcc80]">
                    This is a demonstration application for educational and development purposes only.
                  </p>
                </div>
              </div>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">1. Demo Application</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  TradePal AI is a demonstration application created for educational and development
                  purposes. This application is not intended for actual trading, investment decisions, or
                  financial advice.
                </p>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">2. No Financial Advice</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  The information provided by this application, including but not limited to stock quotes,
                  options data, market analysis, and AI-generated responses, is for informational
                  purposes only. It does not constitute financial, investment, legal, or tax advice. You
                  should not rely on this information to make investment decisions.
                </p>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">3. Market Data Disclaimer</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  Stock prices, options data, and market information displayed in this application are
                  provided by third-party data sources and may be delayed, inaccurate, or incomplete. The
                  developers of this application do not guarantee the accuracy, completeness, or timeliness
                  of any market data. Real-time data may not be available, and prices shown may not reflect
                  current market conditions.
                </p>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">4. Investment Risks</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  Trading stocks, options, and other securities involves substantial risk of loss. Past
                  performance is not indicative of future results. You may lose some or all of your
                  investment. Options trading involves additional risks and is not suitable for all
                  investors. Please consult with a licensed financial advisor before making any investment
                  decisions.
                </p>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">5. No Liability</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  The developers, contributors, and operators of TradePal AI (collectively, "we", "us", or
                  "our") shall not be held liable for any losses, damages, or expenses arising from:
                </p>
                <ul className="list-disc list-inside space-y-2 text-[#9ca3af] ml-4 leading-relaxed">
                  <li>Your use or inability to use this application</li>
                  <li>Any errors, inaccuracies, or omissions in the data or information provided</li>
                  <li>Any decisions made based on information from this application</li>
                  <li>Any financial losses incurred from trading or investment activities</li>
                  <li>Technical failures, interruptions, or errors in the application</li>
                  <li>Any unauthorized access to your data or information</li>
                </ul>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">6. AI-Generated Content</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  Responses generated by the AI assistant in this application are created by artificial
                  intelligence and may contain errors, inaccuracies, or outdated information. AI-generated
                  content should not be relied upon for making financial or investment decisions. Always
                  verify information from multiple reliable sources and consult with qualified
                  professionals.
                </p>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">7. Third-Party Services</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  This application may use third-party services and APIs for data and functionality. We
                  are not responsible for the availability, accuracy, or terms of service of these
                  third-party providers. Your use of third-party services is subject to their respective
                  terms and conditions.
                </p>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">8. No Warranty</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  This application is provided "as is" without any warranties, express or implied,
                  including but not limited to warranties of merchantability, fitness for a particular
                  purpose, or non-infringement. We do not warrant that the application will be
                  uninterrupted, error-free, or secure.
                </p>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">9. Regulatory Compliance</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  This application is not registered with any financial regulatory authority and is not
                  intended to provide regulated financial services. If you require financial services,
                  please consult with licensed and registered financial professionals.
                </p>
              </section>

              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-[#dcdcdc]">10. Acceptance of Terms</h2>
                <p className="text-[#9ca3af] leading-relaxed">
                  By using this application, you acknowledge that you have read, understood, and agree to
                  this disclaimer. You understand that this is a demo application and that you use it at
                  your own risk. If you do not agree with any part of this disclaimer, you should not use
                  this application.
                </p>
              </section>

              <div className="pt-6 border-t border-[#2d3237]">
                <p className="text-sm text-[#9ca3af]">
                  <strong className="text-[#dcdcdc]">Last Updated:</strong> {new Date().toLocaleDateString()}
                </p>
                <p className="text-sm text-[#9ca3af] mt-2">
                  If you have any questions about this disclaimer, please contact the development team.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}


