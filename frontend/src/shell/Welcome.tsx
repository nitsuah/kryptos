import { useEffect, useRef } from "react";

const STARTS: { id: string; label: string; hint: string }[] = [
  { id: "lab", label: "Watch K1 decode", hint: "See what a solved section looks like (Lab)." },
  { id: "ledger", label: "See what is ruled out", hint: "Every cipher family tried so far (Ledger)." },
  { id: "attacks", label: "Browse the attacks", hint: "The queue of ideas to test (Attacks)." },
];

export default function Welcome({ onClose, onStart }: { onClose: () => void; onStart: (id: string) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const close = useRef(onClose);
  close.current = onClose;

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    ref.current?.focus();
    // Capture phase: Esc closes the card and arrow keys stay off the ring.
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close.current();
      else if (e.key === "Tab") {
        const items = Array.from(ref.current?.querySelectorAll("button") ?? []);
        const at = items.indexOf(document.activeElement as HTMLButtonElement);
        const to = e.shiftKey ? (at <= 0 ? items.length - 1 : at - 1) : (at + 1) % items.length;
        e.preventDefault();
        items[to]?.focus();
      } else if (!["ArrowLeft", "ArrowRight", "[", "]"].includes(e.key)) return;
      e.stopPropagation();
    };
    window.addEventListener("keydown", onKey, true);
    return () => {
      window.removeEventListener("keydown", onKey, true);
      previous?.focus?.();
    };
  }, []);

  return (
    <div className="welcome-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="welcome" role="dialog" aria-modal="true" aria-labelledby="welcome-title" tabIndex={-1} ref={ref}>
        <h2 id="welcome-title">What is Kryptos?</h2>
        <p>
          Kryptos is Jim Sanborn's sculpture at CIA headquarters. It carries four encrypted passages. Three are
          solved; the fourth, K4, is 97 letters and still unsolved. This site is a workstation for testing ideas
          about K4 and recording what has been ruled out.
        </p>
        <ul>
          {STARTS.map((s) => (
            <li key={s.id}>
              <button type="button" onClick={() => onStart(s.id)}>
                {s.label}
              </button>
              <span className="muted small">{s.hint}</span>
            </li>
          ))}
        </ul>
        <button type="button" className="link-button" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
}
