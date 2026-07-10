"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Szukaj" },
  { href: "/corpus", label: "Korpus gramatyki" },
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-4 px-6 pt-8">
      <Link href="/" className="display-title text-2xl text-[var(--ink)]">
        Zadania z Gramatyki
      </Link>
      <nav className="flex flex-wrap gap-2">
        {links.map((link) => {
          const active = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                active
                  ? "bg-[var(--accent)] text-white"
                  : "bg-[var(--card)] text-[var(--ink-soft)] ring-1 ring-[var(--line)] hover:text-[var(--ink)]"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
