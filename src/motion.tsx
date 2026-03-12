import React from "react";
import { useCurrentFrame, interpolate, Easing } from "remotion";

/* ── Fade + Slide entrance ── */
export const FadeSlideIn: React.FC<{
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  from?: "left" | "right" | "top" | "bottom";
  distance?: number;
}> = ({ children, delay = 0, duration = 20, from = "bottom", distance = 40 }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const dx = from === "left" ? -distance : from === "right" ? distance : 0;
  const dy = from === "top" ? -distance : from === "bottom" ? distance : 0;

  return (
    <g
      opacity={progress}
      transform={`translate(${dx * (1 - progress)}, ${dy * (1 - progress)})`}
    >
      {children}
    </g>
  );
};

/* ── Scale entrance ── */
export const ScaleIn: React.FC<{
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  cx?: number;
  cy?: number;
}> = ({ children, delay = 0, duration = 20, cx = 960, cy = 540 }) => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [delay, delay + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.3)),
  });
  return (
    <g style={{ transformOrigin: `${cx}px ${cy}px`, transform: `scale(${s})` }}>
      {children}
    </g>
  );
};

/* ── Continuous float ── */
export const Float: React.FC<{
  children: React.ReactNode;
  amplitude?: number;
  speed?: number;
  phase?: number;
}> = ({ children, amplitude = 8, speed = 0.05, phase = 0 }) => {
  const frame = useCurrentFrame();
  const y = Math.sin(frame * speed + phase) * amplitude;
  return <g transform={`translate(0, ${y})`}>{children}</g>;
};

/* ── Horizontal drift ── */
export const Drift: React.FC<{
  children: React.ReactNode;
  amplitude?: number;
  speed?: number;
  phase?: number;
}> = ({ children, amplitude = 6, speed = 0.03, phase = 0 }) => {
  const frame = useCurrentFrame();
  const x = Math.sin(frame * speed + phase) * amplitude;
  return <g transform={`translate(${x}, 0)`}>{children}</g>;
};

/* ── Pulse opacity ── */
export const Pulse: React.FC<{
  children: React.ReactNode;
  min?: number;
  max?: number;
  speed?: number;
}> = ({ children, min = 0.7, max = 1, speed = 0.06 }) => {
  const frame = useCurrentFrame();
  const o = min + (max - min) * (0.5 + 0.5 * Math.sin(frame * speed));
  return <g opacity={o}>{children}</g>;
};

/* ── Flicker effect ── */
export const Flicker: React.FC<{
  children: React.ReactNode;
  speed?: number;
}> = ({ children, speed = 0.15 }) => {
  const frame = useCurrentFrame();
  const o = 0.6 + 0.4 * Math.sin(frame * speed) * Math.cos(frame * speed * 1.7);
  return <g opacity={o}>{children}</g>;
};

/* ── Typewriter text ── */
export const TypeLine: React.FC<{
  text: string;
  delay?: number;
  charsPerFrame?: number;
} & React.SVGProps<SVGTextElement>> = ({
  text,
  delay = 0,
  charsPerFrame = 0.8,
  ...props
}) => {
  const frame = useCurrentFrame();
  const chars = Math.floor(Math.max(0, (frame - delay) * charsPerFrame));
  return <text {...props}>{text.slice(0, chars)}</text>;
};

/* ── CountUp number ── */
export const CountUp: React.FC<{
  from?: number;
  to: number;
  delay?: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
} & React.SVGProps<SVGTextElement>> = ({
  from = 0,
  to,
  delay = 0,
  duration = 60,
  prefix = "",
  suffix = "",
  decimals = 0,
  ...props
}) => {
  const frame = useCurrentFrame();
  const value = interpolate(frame, [delay, delay + duration], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <text {...props}>
      {prefix}
      {value.toFixed(decimals)}
      {suffix}
    </text>
  );
};

/* ── Stagger children entrance ── */
export const StaggerChildren: React.FC<{
  children: React.ReactNode[];
  stagger?: number;
  duration?: number;
}> = ({ children, stagger = 8, duration = 20 }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {children.map((child, i) => {
        const progress = interpolate(
          frame,
          [i * stagger, i * stagger + duration],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );
        return (
          <g key={i} opacity={progress} transform={`translate(0, ${20 * (1 - progress)})`}>
            {child}
          </g>
        );
      })}
    </>
  );
};

/* ── Growing bar ── */
export const GrowBar: React.FC<{
  x: number;
  y: number;
  width: number;
  maxHeight: number;
  color: string;
  delay?: number;
  duration?: number;
}> = ({ x, y, width, maxHeight, color, delay = 0, duration = 30 }) => {
  const frame = useCurrentFrame();
  const h = interpolate(frame, [delay, delay + duration], [0, maxHeight], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return <rect x={x} y={y - h} width={width} height={h} fill={color} rx={4} />;
};
