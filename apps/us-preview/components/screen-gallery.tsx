"use client";

import { useEffect, useState } from "react";

export type ThemeId = "paper-ink" | "sunday-morning";
export type ScreenId =
  | "splash"
  | "our-day"
  | "plan"
  | "together"
  | "wellbeing"
  | "memories";

const SCREENS: { id: ScreenId; label: string }[] = [
  { id: "splash", label: "Splash" },
  { id: "our-day", label: "Our Day" },
  { id: "plan", label: "Plan" },
  { id: "together", label: "Together" },
  { id: "wellbeing", label: "Wellbeing" },
  { id: "memories", label: "Memories" }
];

const TABS: ScreenId[] = ["our-day", "plan", "together", "wellbeing", "memories"];

function screenSrc(theme: ThemeId, screen: ScreenId): string {
  if (theme === "sunday-morning" && screen === "splash") {
    return "/screens/paper-ink/splash.png";
  }
  const folder = theme === "paper-ink" ? "paper-ink" : "sunday-morning";
  return `/screens/${folder}/${screen}.png`;
}

export function ThemePicker({
  theme,
  onChange
}: {
  theme: ThemeId;
  onChange: (theme: ThemeId) => void;
}) {
  return (
    <div className="picker" role="tablist" aria-label="Design direction">
      <button
        type="button"
        role="tab"
        aria-pressed={theme === "paper-ink"}
        onClick={() => onChange("paper-ink")}
      >
        1 · Paper & Ink
      </button>
      <button
        type="button"
        role="tab"
        aria-pressed={theme === "sunday-morning"}
        onClick={() => onChange("sunday-morning")}
      >
        3 · Sunday Morning
      </button>
    </div>
  );
}

export function ScreenRail({
  theme,
  screen,
  onChange
}: {
  theme: ThemeId;
  screen: ScreenId;
  onChange: (screen: ScreenId) => void;
}) {
  return (
    <div className="screen-rail" role="tablist" aria-label="App screens">
      {SCREENS.map((item) => {
        if (theme === "sunday-morning" && item.id === "splash") {
          return null;
        }
        return (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-pressed={screen === item.id}
            onClick={() => onChange(item.id)}
          >
            {item.label}
          </button>
        );
      })}
    </div>
  );
}

export function ImagePhone({
  theme,
  screen,
  onTab
}: {
  theme: ThemeId;
  screen: ScreenId;
  onTab: (screen: ScreenId) => void;
}) {
  const [fade, setFade] = useState(true);
  const src = screenSrc(theme, screen);

  useEffect(() => {
    setFade(false);
    const id = window.setTimeout(() => setFade(true), 30);
    return () => window.clearTimeout(id);
  }, [src]);

  return (
    <div className={`phone image-phone ${theme}`}>
      <div className={`screen-frame ${fade ? "is-in" : "is-out"}`}>
        <img className="screen-art" src={src} alt={`${theme} ${screen}`} />
        {screen !== "splash" ? (
          <div className="tab-hotspots" aria-label="Bottom navigation">
            {TABS.map((tab) => (
              <button
                key={tab}
                type="button"
                className={screen === tab ? "active" : undefined}
                aria-label={tab}
                onClick={() => onTab(tab)}
              />
            ))}
          </div>
        ) : (
          <button
            type="button"
            className="splash-cta"
            onClick={() => onTab("our-day")}
            aria-label="Start our story"
          />
        )}
      </div>
    </div>
  );
}

export function LivingHero({ theme }: { theme: ThemeId }) {
  return (
    <div className={`phone living-hero ${theme}`} aria-hidden="true">
      <div className="hero-paper">
        <img className="layer hills" src="/layers/layer-hills.png" alt="" />
        <img className="layer clouds" src="/layers/layer-clouds.png" alt="" />
        <img className="layer sun" src="/layers/layer-sun.png" alt="" />
        <img className="layer hearts" src="/layers/layer-hearts.png" alt="" />
        <img className="layer stars" src="/layers/layer-stars.png" alt="" />
        <img className="layer plane" src="/layers/layer-plane.png" alt="" />
        <div className="hero-copy">
          <p className="hero-eyebrow">Living layers</p>
          <p className="hero-title">Us.</p>
        </div>
      </div>
    </div>
  );
}
