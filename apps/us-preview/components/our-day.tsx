"use client";

import { useEffect, useState } from "react";

import layerManifest from "./layer-manifest.json";

export type ThemeId = "paper-ink" | "sunday-morning";

type LayerInfo = {
  file: string;
  leftPct: number;
  topPct: number;
  widthPct: number;
  heightPct: number;
  anim?: string;
};

function PaperLayered() {
  const [note, setNote] = useState("");
  const [toast, setToast] = useState("");
  const layers = Object.entries(layerManifest.layers as Record<string, LayerInfo>);

  function share() {
    if (!note.trim()) {
      setToast("Even one word is enough.");
      return;
    }
    setToast("Shared softly with Jakub.");
    setNote("");
  }

  return (
    <div className="phone living paper-ink">
      <div className="living-stage">
        <div className="art-wrap layered-hero">
          <img className="mock-exact" src="/mockups/layers/paper-top-clean.png" alt="" />
          {layers.map(([name, layer]) => (
            <img
              key={name}
              className={`cut-layer anim-${layer.anim ?? "float"}`}
              src={layer.file}
              alt=""
              style={{
                left: `${layer.leftPct}%`,
                top: `${layer.topPct}%`,
                width: `${layer.widthPct}%`,
                height: `${layer.heightPct}%`
              }}
            />
          ))}
        </div>

        <section className="live-prompt paper-ink">
          <div className="live-prompt-head">
            <span aria-hidden="true">🌿</span>
            <h3>Daily Prompt</h3>
          </div>
          <p>What is one small thing you appreciate about your partner today?</p>
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

        <img className="mock-nav" src="/mockups/paper-ink-nav.png" alt="" />
      </div>
    </div>
  );
}

function SundayLiving() {
  const [note, setNote] = useState("");
  const [toast, setToast] = useState("");

  useEffect(() => {
    setNote("");
    setToast("");
  }, []);

  function share() {
    if (!note.trim()) {
      setToast("A tiny thank-you still counts.");
      return;
    }
    setToast("Sent with a soft ping.");
    setNote("");
  }

  return (
    <div className="phone living sunday-morning">
      <div className="living-stage">
        <div className="art-wrap">
          <img className="mock-exact" src="/mockups/sunday-top.png" alt="" />
          <div className="fx" aria-hidden="true">
            <span className="orb o1" />
            <span className="orb o2" />
            <span className="spark sp1">✦</span>
            <span className="spark sp2">✧</span>
          </div>
        </div>

        <section className="live-prompt sunday-morning">
          <div className="live-prompt-head">
            <span aria-hidden="true">♡</span>
            <h3>Daily Prompt</h3>
          </div>
          <p>What’s one thing you’re grateful for about us today?</p>
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

        <img className="mock-nav" src="/mockups/sunday-nav.png" alt="" />
      </div>
    </div>
  );
}

export function OurDay({ theme }: { theme: ThemeId }) {
  return theme === "paper-ink" ? <PaperLayered /> : <SundayLiving />;
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
