import type { ReactNode } from "react";
import { DM_Sans, Fraunces } from "next/font/google";

import "./globals.css";

const sans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-sans"
});

const display = Fraunces({
  subsets: ["latin"],
  variable: "--font-display"
});

export const metadata = {
  title: "Design Intelligence — Reference Library",
  description: "Premium dashboard for browsing curated design references"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pl" className={`${sans.variable} ${display.variable}`}>
      <body style={{ fontFamily: "var(--font-sans), system-ui, sans-serif" }}>{children}</body>
    </html>
  );
}
