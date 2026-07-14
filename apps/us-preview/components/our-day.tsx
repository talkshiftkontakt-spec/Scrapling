"use client";

import { useEffect, useState } from "react";

export type ThemeId = "paper-ink" | "sunday-morning";

type AgendaItem = {
  id: string;
  title: string;
  meta: string;
  tag: string;
  owners: Array<"a" | "b">;
  done: boolean;
  icon: "calendar" | "check" | "dinner" | "coffee";
};

const PAPER_AGENDA: AgendaItem[] = [
  {
    id: "anniv",
    title: "3 Year Anniversary",
    meta: "All day",
    tag: "EVENT",
    owners: ["a", "b"],
    done: false,
    icon: "calendar"
  },
  {
    id: "flowers",
    title: "Pick up flowers",
    meta: "Shared",
    tag: "TASK",
    owners: ["a", "b"],
    done: false,
    icon: "check"
  },
  {
    id: "dinner",
    title: "Dinner reservation at Luma",
    meta: "7:30 PM",
    tag: "EVENT",
    owners: ["b"],
    done: true,
    icon: "dinner"
  },
  {
    id: "coffee",
    title: "Coffee together",
    meta: "Suggestion",
    tag: "SUGGESTION",
    owners: ["a", "b"],
    done: false,
    icon: "coffee"
  }
];

const SUNDAY_CARDS = [
  { id: "anniv", tone: "coral", tag: "EVENT", title: "Anniversary", meta: "All day", done: false },
  { id: "flowers", tone: "peach", tag: "TASK", title: "Flowers", meta: "You · E", done: false },
  { id: "dinner", tone: "sky", tag: "TASK", title: "Dinner", meta: "Completed", done: true },
  { id: "coffee", tone: "blue", tag: "SUGGESTION", title: "Coffee", meta: "Plan together", done: false }
] as const;

function useCountUp(target: number, active: boolean) {
  const [value, setValue] = useState(active ? 0 : target);

  useEffect(() => {
    if (!active) {
      setValue(target);
      return;
    }
    setValue(0);
    const started = performance.now();
    const duration = 1100;
    let frame = 0;

    const tick = (now: number) => {
      const progress = Math.min(1, (now - started) / duration);
      const eased = 1 - (1 - progress) ** 3;
      setValue(Math.round(target * eased));
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      }
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [active, target]);

  return value;
}

function LineIcon({ name }: { name: AgendaItem["icon"] }) {
  switch (name) {
    case "calendar":
      return (
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="4" y="5" width="16" height="15" rx="2" stroke="currentColor" strokeWidth="1.5" />
          <path d="M8 3v4M16 3v4M4 10h16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );
    case "check":
      return (
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="4" y="4" width="16" height="16" rx="4" stroke="currentColor" strokeWidth="1.5" />
          <path d="m8 12 2.5 2.5L16 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );
    case "dinner":
      return (
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M7 4v9M7 13v7M5 4v5a2 2 0 0 0 4 0V4M15 4c2 2 2 5 2 9v7M15 4v8h3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );
    case "coffee":
      return (
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M6 9h10v5a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4V9Z" stroke="currentColor" strokeWidth="1.5" />
          <path d="M16 10h2a2 2 0 0 1 0 4h-2M8 19h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );
    default: {
      const _exhaustive: never = name;
      return _exhaustive;
    }
  }
}

function PaperScreen() {
  const days = useCountUp(763, true);
  const [done, setDone] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(PAPER_AGENDA.map((item) => [item.id, item.done]))
  );
  const [note, setNote] = useState("");
  const [toast, setToast] = useState("");

  return (
    <div className="phone paper-screen">
      <div className="screen">
        <header className="topbar paper-top">
          <div className="brand paper-brand">
            <span className="heart-mark" aria-hidden="true">
              ♥
            </span>
            Us<span>.</span>
          </div>
          <div className="top-actions">
            <button className="icon-btn" type="button" aria-label="Daylight">
              <svg viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.5" />
                <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.5 5.5l1.4 1.4M17.1 17.1l1.4 1.4M17.1 6.9l1.4-1.4M5.5 18.5l1.4-1.4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
            <div className="avatar">
              <img src="/avatars/emily.png" alt="" />
              Emily
            </div>
          </div>
        </header>

        <section className="hero-illustrated paper-hero" aria-label="Days together">
          <div className="hero-art" aria-hidden="true">
            <img className="hero-base" src="/illustrations/hero-base.png" alt="" />
            <img className="layer sun" src="/illustrations/sun.png" alt="" />
            <img className="layer cloud cloud-a" src="/illustrations/cloud.png" alt="" />
            <img className="layer cloud cloud-b" src="/illustrations/cloud.png" alt="" />
            <span className="float-heart">♥</span>
            <div className="hero-wash" />
          </div>
          <div className="hero-copy">
            <div className="hero-kicker">We have been sharing</div>
            <h1 className="hero-days">
              <span className="count">{days}</span> days
            </h1>
            <p className="hero-sub">together as one.</p>
          </div>
        </section>

        <h2 className="section-title">Our Day Today</h2>
        <div className="agenda paper-agenda">
          {PAPER_AGENDA.map((item) => {
            const isDone = done[item.id];
            return (
              <button
                key={item.id}
                type="button"
                className={`agenda-row${isDone ? " done" : ""}`}
                onClick={() => setDone((prev) => ({ ...prev, [item.id]: !prev[item.id] }))}
              >
                <span className="row-icon">
                  <LineIcon name={item.icon} />
                </span>
                <span className="agenda-body">
                  <strong>{item.title}</strong>
                  <span className="meta">
                    {item.owners.map((owner) => (
                      <span key={owner} className={`mini ${owner}`}>
                        {owner === "a" ? "E" : "J"}
                      </span>
                    ))}
                    {item.meta}
                  </span>
                </span>
                <span className="chev" aria-hidden="true">
                  ›
                </span>
              </button>
            );
          })}
        </div>

        <section className="prompt paper-prompt">
          <div className="prompt-ornament" aria-hidden="true">
            ✦
          </div>
          <h3>Daily Prompt</h3>
          <p>What is one small thing you appreciate about your partner today?</p>
          <div className="prompt-row">
            <input
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Write your note..."
              aria-label="Appreciation note"
            />
            <button
              className="share"
              type="button"
              onClick={() => {
                if (!note.trim()) {
                  setToast("Even one word is enough.");
                  return;
                }
                setToast("Shared softly with Jakub.");
                setNote("");
              }}
            >
              Share
            </button>
          </div>
          <div className="toast" aria-live="polite">
            {toast}
          </div>
        </section>
      </div>

      <nav className="tabbar paper-tabs" aria-label="Main">
        {(
          [
            ["Our Day", "sun"],
            ["Plan", "cal"],
            ["Together", "hearts"],
            ["Wellbeing", "leaf"],
            ["Memories", "photo"]
          ] as const
        ).map(([label], index) => (
          <button key={label} type="button" className={`tab${index === 0 ? " active" : ""}`}>
            <span className="tab-glyph" aria-hidden="true">
              {index === 0 ? "☀" : index === 1 ? "▦" : index === 2 ? "♡" : index === 3 ? "☘" : "▤"}
            </span>
            {label}
          </button>
        ))}
      </nav>
    </div>
  );
}

function SundayScreen() {
  const days = useCountUp(763, true);
  const [note, setNote] = useState("");
  const [toast, setToast] = useState("");
  const [activeCard, setActiveCard] = useState(0);
  const [done, setDone] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(SUNDAY_CARDS.map((card) => [card.id, card.done]))
  );

  const digits = String(days).padStart(3, "0").slice(-3).split("");

  return (
    <div className="phone sunday-screen">
      <div className="screen">
        <header className="sunday-top">
          <button className="ghost-icon" type="button" aria-label="Gifts">
            ▤
          </button>
          <div className="sunday-logo">
            Us<span>.</span>
            <i>♥</i>
          </div>
          <img className="sunday-avatar" src="/avatars/emily.png" alt="Emily" />
        </header>

        <section className="sunday-hero" aria-label="Days together">
          <div className="wave wave-a" aria-hidden="true" />
          <div className="wave wave-b" aria-hidden="true" />
          <img className="float-asset sun-smile" src="/illustrations/sun-smile.png" alt="" />
          <img className="float-asset cloud-smile" src="/illustrations/cloud-smile.png" alt="" />
          <span className="spark s1">✦</span>
          <span className="spark s2">✧</span>

          <div className="pair">
            <figure>
              <img src="/avatars/you.png" alt="" />
              <figcaption className="tag a">You</figcaption>
            </figure>
            <figure>
              <img src="/avatars/emily.png" alt="" />
              <figcaption className="tag b">Emily</figcaption>
            </figure>
          </div>

          <div className="sunday-count" aria-label={`${days} days together`}>
            <span className="d0">{digits[0]}</span>
            <span className="d1">{digits[1]}</span>
            <span className="d2">{digits[2]}</span>
          </div>
          <p className="sunday-sub">days together</p>
          <p className="sunday-script">
            as one <span>♥</span>
          </p>
        </section>

        <div className="sunday-section-head">
          <h2>Our Day Today</h2>
          <span aria-hidden="true">///</span>
        </div>

        <div className="carousel" role="list">
          {SUNDAY_CARDS.map((card, index) => (
            <button
              key={card.id}
              type="button"
              role="listitem"
              className={`day-card tone-${card.tone}${done[card.id] ? " done" : ""}${activeCard === index ? " focus" : ""}`}
              onClick={() => {
                setActiveCard(index);
                setDone((prev) => ({ ...prev, [card.id]: !prev[card.id] }));
              }}
            >
              <span className="day-tag">{card.tag}</span>
              <strong>{card.title}</strong>
              <em>{card.meta}</em>
            </button>
          ))}
        </div>
        <div className="dots" aria-hidden="true">
          {SUNDAY_CARDS.map((card, index) => (
            <i key={card.id} className={activeCard === index ? "on" : ""} />
          ))}
        </div>

        <section className="sunday-prompt">
          <img className="prompt-art" src="/illustrations/coffee-prompt.png" alt="" />
          <div>
            <h3>
              Daily Prompt <span>♥</span>
            </h3>
            <p>What’s one thing you’re grateful for about us today?</p>
            <div className="prompt-row">
              <input
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="Write your note..."
                aria-label="Gratitude note"
              />
              <button
                className="share"
                type="button"
                onClick={() => {
                  if (!note.trim()) {
                    setToast("A tiny thank-you still counts.");
                    return;
                  }
                  setToast("Sent with a soft ping.");
                  setNote("");
                }}
              >
                Share
              </button>
            </div>
            <div className="toast" aria-live="polite">
              {toast}
            </div>
          </div>
        </section>
      </div>

      <nav className="tabbar sunday-tabs" aria-label="Main">
        {(["Home", "Our Day", "Connect", "Grow", "Chats"] as const).map((label, index) => (
          <button key={label} type="button" className={`tab${index === 1 ? " active" : ""}`}>
            <span className="tab-glyph" aria-hidden="true">
              {index === 0 ? "⌂" : index === 1 ? "☀" : index === 2 ? "♡" : index === 3 ? "☘" : "💬"}
            </span>
            {label}
          </button>
        ))}
      </nav>
    </div>
  );
}

export function OurDay({ theme }: { theme: ThemeId }) {
  return theme === "paper-ink" ? <PaperScreen /> : <SundayScreen />;
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
