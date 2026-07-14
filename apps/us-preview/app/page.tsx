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
            ? "Paper & Ink — rysowany hero z animacją słońca/chmur + count-up 763."
            : "Sunday Morning — fale, sun/cloud bob, carousel Our Day + sparkles."}
        </p>
      </div>
    </main>
  );
}
