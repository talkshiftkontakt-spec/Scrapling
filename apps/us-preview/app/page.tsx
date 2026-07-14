"use client";

import { useState } from "react";

import { OurDay, ThemePicker, type ThemeId } from "../components/our-day";

export default function HomePage() {
  const [theme, setTheme] = useState<ThemeId>("paper-ink");

  return (
    <main className="stage" data-theme={theme}>
      <div className="stage-inner">
        <ThemePicker theme={theme} onChange={setTheme} />
        <OurDay theme={theme} />
        <p className="caption">
          {theme === "paper-ink"
            ? "Paper & Ink — czysty oryginalny PNG (bez zepsutych wycinek)."
            : "Sunday Morning — czysty oryginalny PNG + działający Daily Prompt."}
        </p>
      </div>
    </main>
  );
}
