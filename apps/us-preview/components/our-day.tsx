"use client";

import { useEffect, useState } from "react";

export type ThemeId = "paper-ink" | "sunday-morning";

const AGENDA = [
  {
    id: "anniv",
    title: "Anniversary celebration",
    meta: "Tonight · both",
    tag: "EVENT",
    owners: ["a", "b"] as const,
    done: false
  },
  {
    id: "flowers",
    title: "Pick up flowers",
    meta: "Emily",
    tag: "TASK",
    owners: ["a"] as const,
    done: false
  },
  {
    id: "dinner",
    title: "Book dinner table",
    meta: "Jakub",
    tag: "TASK",
    owners: ["b"] as const,
    done: true
  },
  {
    id: "coffee",
    title: "Coffee or tea together?",
    meta: "Soft suggestion",
    tag: "SUGGESTION",
    owners: ["a", "b"] as const,
    done: false
  }
] as const;

function SunIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.6" />
      <path
        d="M12 3v2.2M12 18.8V21M3 12h2.2M18.8 12H21M5.2 5.2l1.6 1.6M17.2 17.2l1.6 1.6M17.2 6.8l1.6-1.6M5.2 18.8l1.6-1.6"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

type TabName = "Our Day" | "Plan" | "Together" | "Wellbeing" | "Memories";

function TabIcon({ name }: { name: TabName }) {
  switch (name) {
    case "Our Day":
      return (
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M4 11.5 12 5l8 6.5V20a1 1 0 0 1-1 1h-5v-5H10v5H5a1 1 0 0 1-1-1v-8.5Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
        </svg>
      );
    case "Plan":
      return (
        <svg viewBox="0 0 24 24" fill="none">
          <rect x="4" y="5" width="16" height="15" rx="2" stroke="currentColor" strokeWidth="1.6" />
          <path d="M8 3v4M16 3v4M4 10h16" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      );
    case "Together":
      return (
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M8 14a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7ZM16 14a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7Z" stroke="currentColor" strokeWidth="1.6" />
          <path d="M3.5 19c.6-2.2 2.5-3.5 4.5-3.5h1c1.1 0 2.1.3 2.9.9M13.1 16.4c.8-.6 1.8-.9 2.9-.9h1c2 0 3.9 1.3 4.5 3.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      );
    case "Wellbeing":
      return (
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 20c4-3.2 7-6 7-9.5A4.5 4.5 0 0 0 12 7a4.5 4.5 0 0 0-7 3.5C5 14 8 16.8 12 20Z" stroke="currentColor" strokeWidth="1.6" />
        </svg>
      );
    case "Memories":
      return (
        <svg viewBox="0 0 24 24" fill="none">
          <rect x="4" y="6" width="16" height="13" rx="2" stroke="currentColor" strokeWidth="1.6" />
          <path d="M4 15l4-3 3 2 4-4 5 5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    default: {
      const _exhaustive: never = name;
      return _exhaustive;
    }
  }
}

function Mascot({ theme }: { theme: ThemeId }) {
  if (theme === "paper-ink") {
    return (
      <svg className="mascot" viewBox="0 0 74 62" aria-hidden="true">
        <ellipse cx="38" cy="34" rx="24" ry="16" fill="#edd7cb" />
        <circle cx="30" cy="32" r="2" fill="#2a231c" />
        <circle cx="44" cy="32" r="2" fill="#2a231c" />
        <path d="M30 40c3 3 11 3 14 0" stroke="#c05b33" strokeWidth="2" strokeLinecap="round" fill="none" />
        <path d="M18 22c4-10 16-14 28-8" stroke="#7c9070" strokeWidth="2" strokeLinecap="round" fill="none" />
      </svg>
    );
  }

  return (
    <svg className="mascot" viewBox="0 0 74 62" aria-hidden="true">
      <circle cx="40" cy="30" r="20" fill="#ffd8c4" />
      <circle cx="33" cy="28" r="2.2" fill="#2c221c" />
      <circle cx="47" cy="28" r="2.2" fill="#2c221c" />
      <path d="M33 36c3.5 3.5 12 3.5 15.5 0" stroke="#e07a52" strokeWidth="2.2" strokeLinecap="round" fill="none" />
      <path d="M18 18l4 2M58 16l-4 2M14 34h4M62 30h4" stroke="#5f86ad" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export function OurDay({ theme }: { theme: ThemeId }) {
  const [done, setDone] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(AGENDA.map((item) => [item.id, item.done]))
  );
  const [note, setNote] = useState("");
  const [toast, setToast] = useState("");

  useEffect(() => {
    setToast("");
    setNote("");
  }, [theme]);

  function toggle(id: string) {
    setDone((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  function shareNote() {
    if (!note.trim()) {
      setToast("Write a tiny note first — even one word counts.");
      return;
    }
    setToast("Shared with Jakub. Soft and private.");
    setNote("");
  }

  return (
    <div className="phone" key={theme}>
      <div className="screen">
        <header className="topbar">
          <div className="brand">
            Us<span>.</span>
          </div>
          <div className="top-actions">
            <button className="icon-btn" aria-label="Theme cue" type="button">
              <SunIcon />
            </button>
            <div className="avatar">
              <i />
              Emily
            </div>
          </div>
        </header>

        <section className="hero" aria-label="Days together">
          <div className="hero-kicker">We have been sharing</div>
          <h1 className="hero-days">763 days</h1>
          <p className="hero-sub">together as one.</p>
          <Mascot theme={theme} />
        </section>

        <h2 className="section-title">Our Day Today</h2>
        <div className="agenda">
          {AGENDA.map((item) => {
            const isDone = done[item.id];
            return (
              <button
                key={item.id}
                type="button"
                className={`agenda-item${isDone ? " done" : ""}`}
                onClick={() => toggle(item.id)}
              >
                <span className="check" aria-hidden="true">
                  {isDone ? "✓" : ""}
                </span>
                <span className="agenda-body">
                  <strong>{item.title}</strong>
                  <span className="meta">
                    {item.owners.map((owner) => (
                      <span key={owner} className={`dot ${owner}`} />
                    ))}
                    {item.meta}
                  </span>
                </span>
                <span className="tag">{item.tag}</span>
              </button>
            );
          })}
        </div>

        <section className="prompt">
          <h3>Daily Prompt</h3>
          <p>What is one small thing you appreciate about your partner today?</p>
          <div className="prompt-row">
            <input
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Write your note..."
              aria-label="Appreciation note"
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  shareNote();
                }
              }}
            />
            <button className="share" type="button" onClick={shareNote}>
              Share
            </button>
          </div>
          <div className="toast" aria-live="polite">
            {toast}
          </div>
        </section>
      </div>

      <nav className="tabbar" aria-label="Main">
        {(["Our Day", "Plan", "Together", "Wellbeing", "Memories"] as const).map((tab) => (
          <button key={tab} type="button" className={`tab${tab === "Our Day" ? " active" : ""}`}>
            <TabIcon name={tab} />
            {tab}
          </button>
        ))}
      </nav>
    </div>
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
