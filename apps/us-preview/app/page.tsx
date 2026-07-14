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
            ? "Twoje oryginalne Paper & Ink — animacja + Share/note na wierzchu."
            : "Twoje oryginalne Sunday Morning — sparkles + live Share/note."}
        </p>
      </div>
    </main>
  );
}
