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
            ? "Paper & Ink — oryginalna grafika + działający Daily Prompt (bez dublowania)."
            : "Sunday Morning — oryginalna grafika + działający Daily Prompt (bez dublowania)."}
        </p>
      </div>
    </main>
  );
}
