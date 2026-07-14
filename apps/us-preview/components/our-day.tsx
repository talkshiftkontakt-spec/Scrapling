"use client";

import { useEffect, useState } from "react";

export type ThemeId = "paper-ink" | "sunday-morning";

function LivingScreen({
  theme,
  topSrc,
  navSrc,
  prompt
}: {
  theme: ThemeId;
  topSrc: string;
  navSrc: string;
  prompt: string;
}) {
  const [note, setNote] = useState("");
  const [toast, setToast] = useState("");

  useEffect(() => {
    setNote("");
    setToast("");
  }, [theme]);

  function share() {
    if (!note.trim()) {
      setToast(theme === "paper-ink" ? "Even one word is enough." : "A tiny thank-you still counts.");
      return;
    }
    setToast(theme === "paper-ink" ? "Shared softly with Jakub." : "Sent with a soft ping.");
    setNote("");
  }

  return (
    <div className={`phone living ${theme}`}>
      <div className="living-stage">
        <div className="art-wrap">
          <img className="mock-exact" src={topSrc} alt="" />
          {/* Soft life overlays — do NOT cover the drawing with cutout ghosts */}
          <div className="fx soft-only" aria-hidden="true">
            <span className="spark sp1">✦</span>
            <span className="spark sp2">✧</span>
            <span className="spark sp3">♥</span>
          </div>
        </div>

        <section className={`live-prompt ${theme}`}>
          <div className="live-prompt-head">
            <span aria-hidden="true">{theme === "paper-ink" ? "🌿" : "♡"}</span>
            <h3>Daily Prompt</h3>
          </div>
          <p>{prompt}</p>
          <div className="prompt-row">
            <input
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Write your note..."
              aria-label="Daily prompt note"
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  share();
                }
              }}
            />
            <button type="button" className="share" onClick={share}>
              Share
            </button>
          </div>
          <div className="toast" aria-live="polite">
            {toast}
          </div>
        </section>

        <img className="mock-nav" src={navSrc} alt="" />
      </div>
    </div>
  );
}

export function OurDay({ theme }: { theme: ThemeId }) {
  if (theme === "paper-ink") {
    return (
      <LivingScreen
        theme="paper-ink"
        topSrc="/mockups/paper-ink-top.png"
        navSrc="/mockups/paper-ink-nav.png"
        prompt="What is one small thing you appreciate about your partner today?"
      />
    );
  }

  return (
    <LivingScreen
      theme="sunday-morning"
      topSrc="/mockups/sunday-top.png"
      navSrc="/mockups/sunday-nav.png"
      prompt="What’s one thing you’re grateful for about us today?"
    />
  );
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
