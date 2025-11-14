import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { DemoBanner } from "@/components/demo-banner";
import { ErrorBoundary } from "@/components/error-boundary";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TradePal AI - Trading Education & Pattern Analysis",
  description: "Educational trading information center. Learn trading patterns, analyze SPY & Tesla, understand SEC/FINRA regulations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ErrorBoundary>
          <DemoBanner />
          <main className="min-h-screen text-[#dcdcdc]">
            {children}
          </main>
        </ErrorBoundary>
      </body>
    </html>
  );
}
