import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "What-If · FIFA World Cup 2026 Simulator",
  description:
    "Ask what-if questions about the FIFA World Cup 2026 and see recomputed standings, qualification odds, knockout paths and AI explanations.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <header className="sticky top-0 z-20 border-b border-border bg-background/80 backdrop-blur">
          <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
            <Link href="/" className="flex items-center gap-2 font-semibold">
              <span className="text-xl">⚽</span>
              <span>
                What<span className="text-accent">-If</span>
              </span>
              <span className="hidden text-xs text-muted sm:inline">
                World Cup 2026
              </span>
            </Link>
            <div className="flex items-center gap-1 text-sm">
              <Link
                href="/"
                className="rounded-md px-3 py-1.5 text-muted hover:bg-surface hover:text-foreground"
              >
                Simulate
              </Link>
              <Link
                href="/groups"
                className="rounded-md px-3 py-1.5 text-muted hover:bg-surface hover:text-foreground"
              >
                Groups
              </Link>
            </div>
          </nav>
        </header>
        <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6">{children}</main>
        <footer className="border-t border-border px-4 py-6 text-center text-xs text-muted">
          Probabilities via Monte Carlo simulation · Not affiliated with FIFA ·
          Demonstration data
        </footer>
      </body>
    </html>
  );
}
