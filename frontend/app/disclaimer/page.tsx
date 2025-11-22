"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle } from "lucide-react";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { MarketTime } from "@/components/chat/market-time";
import { useRouter } from "next/navigation";

export default function DisclaimerPage() {
  const router = useRouter();
  const lastUpdated = "November 22, 2025";

  return (
    <div className="flex h-screen w-full bg-[#0F1115] bg-grid-subtle text-[#dcdcdc] overflow-hidden">
      <AppSidebar 
        chatMode="standard"
        onModeChange={() => router.push("/")}
        showDocuments={false}
        onToggleDocuments={() => router.push("/")}
      />
      
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="h-14 border-b border-white/5 flex items-center justify-between px-4 sm:px-6 bg-[#131619]/50 backdrop-blur-sm shrink-0 z-10">
           <div className="flex items-center gap-3 md:hidden">
             <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-[#34c759] to-[#28a745]">
               <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
               </svg>
             </div>
             <span className="font-bold text-white tracking-tight">TRADEPAL</span>
          </div>

          <div className="hidden md:flex items-center text-sm font-medium text-gray-400">
             <span className="text-gray-500">System</span>
             <span className="mx-2">/</span>
             <span className="text-white">Disclaimer</span>
          </div>

          <div className="flex items-center gap-4">
            <MarketTime />
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8 custom-scrollbar">
          <div className="max-w-5xl mx-auto">
            <Card className="trading-panel border-[#2d3237]">
              <CardHeader className="pb-6 border-b border-white/5">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[#ff9500] to-[#ff7a00] border-2 border-[#ff9500] shadow-lg shadow-orange-500/20">
                    <AlertTriangle className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold text-[#dcdcdc] tracking-tight">
                      SYSTEM DISCLAIMER
                    </CardTitle>
                    <p className="text-xs text-gray-500 font-mono mt-1 uppercase tracking-wider">
                      Compliance Protocol v2.0
                    </p>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-8 pt-6 font-mono text-sm">
                {/* Critical Warning */}
                <div className="flex items-start gap-4 p-5 bg-[#2d1f1f]/50 border border-[#ff3b30]/20 rounded-lg relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-[#ff3b30]"></div>
                  <AlertTriangle className="h-6 w-6 text-[#ff3b30] flex-shrink-0 mt-0.5" />
                  <div>
                    <h2 className="font-bold text-[#ff3b30] mb-2 uppercase tracking-wider text-base">
                      Critical Warning: Demo Environment
                    </h2>
                    <p className="text-[#ffcc80] leading-relaxed text-sm">
                      TradePal AI is a <strong>software development demonstration</strong> created solely for educational and portfolio purposes. It is NOT a trading platform, brokerage, or financial advisor. All capital, positions, and executions displayed are simulated. <strong>Do not use any information from this system for real-world financial decisions.</strong>
                    </p>
                  </div>
                </div>

                {/* Core Sections Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <section className="space-y-3">
                      <h2 className="text-base font-bold text-[#dcdcdc] uppercase border-b border-white/10 pb-2 flex items-center gap-2">
                        <span className="text-[#34c759]">01 //</span> Data Integrity
                      </h2>
                      <p className="text-gray-400 leading-relaxed text-xs sm:text-sm">
                        Market data (stocks, crypto, options) is aggregated from third-party APIs (e.g., CoinCap, Alpha Vantage) and may be delayed, simulated, or inaccurate. <strong>Real-time accuracy is not guaranteed.</strong> We accept no liability for data errors, service interruptions, or latency issues.
                      </p>
                    </section>

                    <section className="space-y-3">
                      <h2 className="text-base font-bold text-[#dcdcdc] uppercase border-b border-white/10 pb-2 flex items-center gap-2">
                         <span className="text-[#34c759]">02 //</span> AI Limitations
                      </h2>
                      <p className="text-gray-400 leading-relaxed text-xs sm:text-sm">
                        Analysis provided by AI models (Gemini, GPT, etc.) is probabilistic and experimental. Large Language Models can hallucinate or generate misleading financial "advice." <strong>Treat all AI outputs as experimental code artifacts, not verified financial guidance.</strong>
                      </p>
                    </section>

                    <section className="space-y-3">
                      <h2 className="text-base font-bold text-[#dcdcdc] uppercase border-b border-white/10 pb-2 flex items-center gap-2">
                         <span className="text-[#34c759]">03 //</span> Investment Risk
                      </h2>
                      <p className="text-gray-400 leading-relaxed text-xs sm:text-sm">
                        Trading securities involves substantial risk of loss. Strategies discussed here (options flow, technical patterns) are for educational simulation only. You acknowledge that you are solely responsible for your own due diligence and financial decisions. Past performance is not indicative of future results.
                      </p>
                    </section>

                    <section className="space-y-3">
                      <h2 className="text-base font-bold text-[#dcdcdc] uppercase border-b border-white/10 pb-2 flex items-center gap-2">
                         <span className="text-[#34c759]">04 //</span> No Liability
                      </h2>
                      <p className="text-gray-400 leading-relaxed text-xs sm:text-sm">
                        The developers, contributors, and operators assume <strong>zero liability</strong> for any damages, losses, or expenses arising from the use of this software. The application is provided "AS IS" without warranty of any kind, express or implied.
                      </p>
                    </section>
                </div>
                
                {/* Footer */}
                <div className="pt-8 mt-4 border-t border-[#2d3237] flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-gray-500">
                  <p className="text-center sm:text-left">
                    By using this terminal, you irrevocably agree to these terms.
                  </p>
                  <p className="font-mono bg-white/5 px-3 py-1 rounded border border-white/5">
                    LAST_UPDATED: <span className="text-[#dcdcdc] font-bold">{lastUpdated}</span>
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
