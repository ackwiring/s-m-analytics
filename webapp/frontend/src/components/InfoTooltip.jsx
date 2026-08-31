import React, { useState, useRef, useLayoutEffect } from "react";
import { createPortal } from "react-dom";

/**
 * Lightweight hover tooltip wrapper - no external dependency, matches the
 * app's navy/orange/teal styling. Wrap any element(s) in <InfoTooltip text="...">.
 *
 * Renders via a portal to document.body with viewport-computed coordinates so it
 * is never clipped by an ancestor's `overflow` (e.g. the pipeline node row's
 * overflow-x-auto, which implicitly clips the vertical axis too).
 */
export default function InfoTooltip({ text, children, position = "top", wrapperClassName = "" }) {
  const [visible, setVisible] = useState(false);
  const [coords, setCoords] = useState(null);
  const anchorRef = useRef(null);

  const updatePosition = () => {
    const el = anchorRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const gap = 8;
    let top, left, transform;
    switch (position) {
      case "bottom":
        top = rect.bottom + gap;
        left = rect.left + rect.width / 2;
        transform = "translate(-50%, 0)";
        break;
      case "left":
        top = rect.top + rect.height / 2;
        left = rect.left - gap;
        transform = "translate(-100%, -50%)";
        break;
      case "right":
        top = rect.top + rect.height / 2;
        left = rect.right + gap;
        transform = "translate(0, -50%)";
        break;
      default:
        top = rect.top - gap;
        left = rect.left + rect.width / 2;
        transform = "translate(-50%, -100%)";
    }
    setCoords({ top, left, transform });
  };

  useLayoutEffect(() => {
    if (!visible) return;
    updatePosition();
    const onChange = () => updatePosition();
    window.addEventListener("scroll", onChange, true);
    window.addEventListener("resize", onChange);
    return () => {
      window.removeEventListener("scroll", onChange, true);
      window.removeEventListener("resize", onChange);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible]);

  const arrowClass = {
    top: "top-full left-1/2 -translate-x-1/2 border-t-[#0a192f] border-x-transparent border-b-transparent",
    bottom: "bottom-full left-1/2 -translate-x-1/2 border-b-[#0a192f] border-x-transparent border-t-transparent",
    left: "left-full top-1/2 -translate-y-1/2 border-l-[#0a192f] border-y-transparent border-r-transparent",
    right: "right-full top-1/2 -translate-y-1/2 border-r-[#0a192f] border-y-transparent border-l-transparent",
  }[position];

  if (!text) return children;

  return (
    <>
      <span
        ref={anchorRef}
        className={`relative inline-block ${wrapperClassName}`}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        onFocus={() => setVisible(true)}
        onBlur={() => setVisible(false)}
      >
        {children}
      </span>
      {visible && coords && createPortal(
        <span
          role="tooltip"
          style={{ position: "fixed", top: coords.top, left: coords.left, transform: coords.transform, zIndex: 9999 }}
          className="pointer-events-none block w-max max-w-[260px] whitespace-normal rounded-md border border-black bg-[#0a192f] px-3 py-2 text-[11px] font-normal leading-snug text-white shadow-xl"
        >
          {text}
          <span className={`absolute h-0 w-0 border-4 ${arrowClass}`} />
        </span>,
        document.body
      )}
    </>
  );
}
