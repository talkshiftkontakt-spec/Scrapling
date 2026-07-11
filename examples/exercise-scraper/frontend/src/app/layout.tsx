import type { Metadata } from "next";
import { DM_Sans, Fraunces } from "next/font/google";
import "./globals.css";
import { SiteHeader } from "@/components/site-header";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin", "latin-ext"],
});

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin", "latin-ext"],
});

export const metadata: Metadata = {
  title: "Zadania z Gramatyki",
  description: "Wyszukuj i zbieraj ćwiczenia gramatyczne po polsku i po angielsku.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pl" className={`${fraunces.variable} ${dmSans.variable} h-full`}>
      <body className="min-h-full antialiased">
        <SiteHeader />
        {children}
      </body>
    </html>
  );
}
