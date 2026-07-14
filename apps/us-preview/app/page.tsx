"use client";

import { useEffect, useState } from "react";

import {
  ImagePhone,
  LivingHero,
  ScreenRail,
  ThemePicker,
  type ScreenId,
  type ThemeId
} from "../components/screen-gallery";

export default function HomePage() {
  const [theme, setTheme] = useState<ThemeId>("paper-ink");
  const [screen, setScreen] = useState<ScreenId>("our-day");
  const [showLayers, setShowLayers] = useState(false);

  useEffect(() => {
    if (theme === "sunday-morning" && screen === "splash") {
      setScreen("our-day");
    }
  }, [theme, screen]);

  return (
    <main className="stage" data-theme={theme}>
      <div className="stage-inner">
        <ThemePicker
          theme={theme}
          onChange={(next) => {
            setTheme(next);
            setShowLayers(false);
          }}
        />
        <ScreenRail
          theme={theme}
          screen={screen}
          onChange={(next) => {
            setShowLayers(false);
            setScreen(next);
          }}
        />
        <div className="mode-row">
          <button
            type="button"
            aria-pressed={!showLayers}
            onClick={() => setShowLayers(false)}
          >
            Pełne ekrany
          </button>
          <button
            type="button"
            aria-pressed={showLayers}
            onClick={() => setShowLayers(true)}
          >
            Warstwy live
          </button>
        </div>

        {showLayers ? (
          <LivingHero theme={theme} />
        ) : (
          <ImagePhone theme={theme} screen={screen} onTab={setScreen} />
        )}

        <p className="caption">
          {showLayers
            ? "Osobne warstwy ilustracji (słońce, chmury, wzgórza…) — gotowe do subtelnej animacji."
            : "Całe UI z wygenerowanych obrazów. Kliknij dolny pasek na telefonie albo pigułki nad ekranem."}
        </p>
      </div>
    </main>
  );
}
