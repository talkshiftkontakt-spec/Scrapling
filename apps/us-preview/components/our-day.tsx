"use client";

import { useEffect, useState } from "react";

export type ThemeId = "paper-ink" | "sunday-morning";

function LivingMock({
  theme,
  src
}: {
  theme: ThemeId;
  src: string;
}) {
  const [note, setNote] = useState("");
  const [toast, setToast] = useState("");
  const [pulseShare, setPulseShare] = useState(false);

  useEffect(() => {
    setNote("");
    setToast("");
  }, [theme]);

  function share() {
    if (!note.trim()) {
      setToast(theme === "paper-ink" ? "Even one word is enough." : "A tiny thank-you still counts.");
      return;
    }
    setPulseShare(true);
    setToast(theme === "paper-ink" ? "Shared softly with Jakub." : "Sent with a soft ping.");
    setNote("");
    window.setTimeout(() => setPulseShare(false), 500);
  }

  return (
    <div className={`phone living ${theme}`}>
      <div className="living-stage">
        <img className="mock-exact" src={src} alt={`Us ${theme} mockup`} />

        <div className="fx" aria-hidden="true">
          <span className="orb o1" />
          <span className="orb o2" />
          <span className="orb o3" />
          <span className="spark sp1">✦</span>
          <span className="spark sp2">✧</span>
          <span className="spark sp3">♥</span>
          <span className="spark sp4">✦</span>
        </div>

        <div className="interact">
          <label className="sr-only" htmlFor={`note-${theme}`}>
            Daily prompt note
          </label>
          <input
            id={`note-${theme}`}
            className="hit-note"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Write your note..."
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                share();
              }
            }}
          />
          <button
            type="button"
            className={`hit-share${pulseShare ? " pulse" : ""}`}
            onClick={share}
          >
            Share
          </button>
        </div>

        {toast ? (
          <div className="living-toast" role="status">
            {toast}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export function OurDay({ theme }: { theme: ThemeId }) {
  const src =
    theme === "paper-ink" ? "/mockups/paper-ink-cropped.png" : "/mockups/sunday-morning-cropped.png";

  return <LivingMock key={theme} theme={theme} src={src} />;
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
