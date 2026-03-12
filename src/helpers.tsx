import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

const W = 1920;
const H = 1080;

/* ── Investing / finance color palette ── */
export { W, H };

export const C = {
  bg: "#0d1117",
  bgLight: "#161b22",
  panel: "#1c2333",
  green: "#2ea043",
  greenLight: "#3fb950",
  greenDark: "#1a7f37",
  red: "#da3633",
  gold: "#d4a017",
  goldLight: "#e8c547",
  blue: "#388bfd",
  blueDim: "#1f6feb",
  text: "#e6edf3",
  textDim: "#8b949e",
  textMuted: "#484f58",
  white: "#ffffff",
  dollarGreen: "#85bb65",
};

/* ── Full-screen SVG wrapper ── */
export const Scene: React.FC<{
  bg?: string;
  children: React.ReactNode;
}> = ({ bg = C.bg, children }) => (
  <div style={{ position: "absolute", width: W, height: H, background: bg }}>
    <svg width={W} height={H} style={{ position: "absolute" }}>
      {children}
    </svg>
  </div>
);

/* ── Large statistic display ── */
export const StatCard: React.FC<{
  value: string;
  label: string;
  sublabel?: string;
  color?: string;
  y?: number;
}> = ({ value, label, sublabel, color = C.green, y = H * 0.3 }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });
  const cx = W / 2;
  const cardH = sublabel ? 420 : 340;
  const cy = y - 60 + cardH / 2;

  return (
    <>
      <rect
        x={80} y={y - 60} width={W - 160} height={cardH}
        rx={20} fill={C.panel} stroke={color} strokeWidth={2} opacity={0.9}
        style={{ transformOrigin: `${cx}px ${cy}px`, transform: `scale(${scale})` }}
      />
      <text x={W / 2} y={y + 80} textAnchor="middle"
        fontSize={120} fontFamily="Arial, sans-serif" fontWeight="bold" fill={color}
        style={{ transformOrigin: `${cx}px ${cy}px`, transform: `scale(${scale})` }}
      >
        {value}
      </text>
      <text x={W / 2} y={y + 160} textAnchor="middle"
        fontSize={42} fontFamily="Arial, sans-serif" fill={C.text}
        style={{ transformOrigin: `${cx}px ${cy}px`, transform: `scale(${scale})` }}
      >
        {label}
      </text>
      {sublabel && (
        <text x={W / 2} y={y + 220} textAnchor="middle"
          fontSize={32} fontFamily="Arial, sans-serif" fill={C.textDim}
          style={{ transformOrigin: `${cx}px ${cy}px`, transform: `scale(${scale})` }}
        >
          {sublabel}
        </text>
      )}
    </>
  );
};

/* ── Section title ── */
export const SectionTitle: React.FC<{
  title: string;
  subtitle?: string;
  color?: string;
}> = ({ title, subtitle, color = C.green }) => {
  const frame = useCurrentFrame();
  const lineW = interpolate(frame, [0, 30], [0, 600], {
    extrapolateRight: "clamp",
  });
  const textOp = interpolate(frame, [10, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <>
      <rect x={(W - lineW) / 2} y={H * 0.42} width={lineW} height={4} fill={color} rx={2} />
      <text x={W / 2} y={H * 0.5} textAnchor="middle"
        fontSize={72} fontFamily="Arial, sans-serif" fontWeight="bold"
        fill={C.text} opacity={textOp}
      >
        {title}
      </text>
      {subtitle && (
        <text x={W / 2} y={H * 0.58} textAnchor="middle"
          fontSize={36} fontFamily="Arial, sans-serif" fill={C.textDim} opacity={textOp}
        >
          {subtitle}
        </text>
      )}
    </>
  );
};

/* ── Animated bar chart ── */
export const BarChart: React.FC<{
  data: { label: string; value: number; color: string }[];
  maxValue: number;
  x?: number;
  y?: number;
  chartW?: number;
  chartH?: number;
  delay?: number;
}> = ({ data, maxValue, x = 200, y = 150, chartW = W - 400, chartH = H - 350, delay = 0 }) => {
  const frame = useCurrentFrame();
  const barW = Math.min(120, (chartW - 40) / data.length - 20);
  const gap = (chartW - barW * data.length) / (data.length + 1);

  return (
    <g>
      {/* Axis */}
      <line x1={x} y1={y} x2={x} y2={y + chartH} stroke={C.textMuted} strokeWidth={2} />
      <line x1={x} y1={y + chartH} x2={x + chartW} y2={y + chartH} stroke={C.textMuted} strokeWidth={2} />

      {data.map((d, i) => {
        const barH = (d.value / maxValue) * (chartH - 40);
        const grow = interpolate(
          frame,
          [delay + i * 8, delay + i * 8 + 30],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );
        const bx = x + gap + i * (barW + gap);
        const by = y + chartH - barH * grow;

        return (
          <g key={i}>
            <rect x={bx} y={by} width={barW} height={barH * grow} fill={d.color} rx={6} />
            <text x={bx + barW / 2} y={y + chartH + 30} textAnchor="middle"
              fontSize={22} fill={C.textDim} fontFamily="Arial, sans-serif"
            >
              {d.label}
            </text>
            {grow > 0.8 && (
              <text x={bx + barW / 2} y={by - 12} textAnchor="middle"
                fontSize={24} fill={C.text} fontWeight="bold" fontFamily="Arial, sans-serif"
                opacity={interpolate(grow, [0.8, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
              >
                ${d.value >= 1000 ? `${(d.value / 1000).toFixed(0)}K` : d.value.toLocaleString()}
              </text>
            )}
          </g>
        );
      })}
    </g>
  );
};

/* ── Dollar bill icon ── */
export const DollarBill: React.FC<{
  x: number;
  y: number;
  scale?: number;
  opacity?: number;
}> = ({ x, y, scale = 1, opacity = 1 }) => (
  <g transform={`translate(${x},${y}) scale(${scale})`} opacity={opacity}>
    <rect x={-50} y={-25} width={100} height={50} rx={6} fill={C.dollarGreen} />
    <text x={0} y={8} textAnchor="middle" fontSize={28} fontWeight="bold"
      fill="#2d5016" fontFamily="Arial, sans-serif"
    >
      $10
    </text>
  </g>
);

/* ── Stick figure ── */
export const StickFigure: React.FC<{
  x: number;
  y: number;
  scale?: number;
  color?: string;
  emotion?: "neutral" | "happy" | "shocked" | "thinking";
}> = ({ x, y, scale = 1, color = C.text, emotion = "neutral" }) => {
  const headR = 22;
  return (
    <g transform={`translate(${x},${y}) scale(${scale})`}>
      <circle cx={0} cy={-60} r={headR} fill="none" stroke={color} strokeWidth={3} />
      <line x1={0} y1={-38} x2={0} y2={20} stroke={color} strokeWidth={3} />
      {emotion === "happy" ? (
        <>
          <line x1={0} y1={-20} x2={-30} y2={-45} stroke={color} strokeWidth={3} />
          <line x1={0} y1={-20} x2={30} y2={-45} stroke={color} strokeWidth={3} />
        </>
      ) : emotion === "shocked" ? (
        <>
          <line x1={0} y1={-20} x2={-35} y2={-30} stroke={color} strokeWidth={3} />
          <line x1={0} y1={-20} x2={35} y2={-30} stroke={color} strokeWidth={3} />
        </>
      ) : (
        <>
          <line x1={0} y1={-20} x2={-30} y2={5} stroke={color} strokeWidth={3} />
          <line x1={0} y1={-20} x2={30} y2={5} stroke={color} strokeWidth={3} />
        </>
      )}
      <line x1={0} y1={20} x2={-20} y2={60} stroke={color} strokeWidth={3} />
      <line x1={0} y1={20} x2={20} y2={60} stroke={color} strokeWidth={3} />
      {emotion === "happy" && (
        <path d={`M -8,-55 Q 0,-48 8,-55`} fill="none" stroke={color} strokeWidth={2} />
      )}
      {emotion === "shocked" && (
        <circle cx={0} cy={-55} r={5} fill="none" stroke={color} strokeWidth={2} />
      )}
    </g>
  );
};

/* ── Growth line chart ── */
export const GrowthLine: React.FC<{
  points: { x: number; y: number }[];
  color: string;
  x?: number;
  y?: number;
  w?: number;
  h?: number;
  drawDuration?: number;
  delay?: number;
}> = ({ points, color, x = 200, y = 100, w = W - 400, h = H - 300, drawDuration = 60, delay = 0 }) => {
  const frame = useCurrentFrame();
  if (points.length < 2) return null;

  const maxX = Math.max(...points.map((p) => p.x));
  const maxY = Math.max(...points.map((p) => p.y));

  const scaled = points.map((p) => ({
    sx: x + (p.x / maxX) * w,
    sy: y + h - (p.y / maxY) * h,
  }));

  const pathD = scaled
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.sx} ${p.sy}`)
    .join(" ");

  const totalLen = scaled.reduce((sum, p, i) => {
    if (i === 0) return 0;
    const prev = scaled[i - 1];
    return sum + Math.hypot(p.sx - prev.sx, p.sy - prev.sy);
  }, 0);

  const progress = interpolate(frame, [delay, delay + drawDuration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <path
      d={pathD}
      fill="none"
      stroke={color}
      strokeWidth={4}
      strokeLinecap="round"
      strokeDasharray={totalLen}
      strokeDashoffset={totalLen * (1 - progress)}
    />
  );
};

/* ── Text wrapping helper ── */
export const wrapText = (text: string, maxChars: number): string[] => {
  const words = text.split(" ");
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    if ((current + " " + word).trim().length > maxChars) {
      if (current) lines.push(current);
      current = word;
    } else {
      current = current ? current + " " + word : word;
    }
  }
  if (current) lines.push(current);
  return lines;
};
