"use client";

import { useEffect, useState } from "react";

export type ThemeId = "paper-ink" | "sunday-morning";

function LivingMock({ theme }: { theme: ThemeId }) {
  const [note, setNote] = useState("");
  const [toast, setToast] = useState("");

  const isPaper = theme === "paper-ink";
  const topSrc = isPaper ? "/mockups/paper-ink-top.png" : "/mockups/sunday-top.png";
  const navSrc = isPaper ? "/mockups/paper-ink-nav.png" : "/mockups/sunday-nav.png";

  useEffect(() => {
    setNote("");
    setToast("");
  }, [theme]);

  function share() {
    if (!note.trim()) {
      setToast(isPaper ? "Even one word is enough." : "A tiny thank-you still counts.");
      return;
    }
    setToast(isPaper ? "Shared softly with Jakub." : "Sent with a soft ping.");
    setNote("");
  }

  return (
    <div className={`phone living ${theme}`}>
      <div className="living-stage">
        <div className="art-wrap">
          <img className="mock-exact" src={topSrc} alt="" />
          <div className="fx" aria-hidden="true">
            <span className="orb o1" />
            <span className="orb o2" />
            <span className="orb o3" />
            <span className="spark sp1">✦</span>
            <span className="spark sp2">✧</span>
            <span className="spark sp3">♥</span>
            <span className="spark sp4">✦</span>
          </div>
        </div>

        <section className={`live-prompt ${theme}`}>
          <div className="live-prompt-head">
            <span aria-hidden="true">{isPaper ? "🌿" : "♡"}</span>
            <h3>Daily Prompt</h3>
          </div>
          <p>
            {isPaper
              ? "What is one small thing you appreciate about your partner today?"
              : "What’s one thing you’re grateful for about us today?"}
          </p>
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
  return <LivingMock key={theme} theme={theme} />;
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
