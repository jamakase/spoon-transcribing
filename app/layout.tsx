import type { Metadata } from "next";
import { Unbounded, DM_Sans } from "next/font/google";
import "./globals.css";
import { Sidebar } from "./components/Sidebar";
import { NeoWalletProvider } from "./context/NeoWalletContext";

const unbounded = Unbounded({
  variable: "--font-unbounded",
  subsets: ["latin"],
});

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Meeting Summarizer",
  description: "AI-powered meeting intelligence",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${unbounded.variable} ${dmSans.variable} antialiased bg-slate-950 text-slate-100 font-sans selection:bg-neon-yellow selection:text-black`}
      >
        <NeoWalletProvider>
          <div className="flex h-screen w-full overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto relative">
              {children}
            </main>
          </div>
        </NeoWalletProvider>
      </body>
    </html>
  );
}
