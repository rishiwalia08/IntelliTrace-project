function RiskBadge({ level }) {
  const palette = {
    HIGH: "bg-red-100 text-red-700 border-red-200",
    MEDIUM: "bg-amber-100 text-amber-700 border-amber-200",
    LOW: "bg-emerald-100 text-emerald-700 border-emerald-200",
  };

  const tone = palette[level] || palette.LOW;

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${tone}`}>
      {level}
    </span>
  );
}

export default RiskBadge;
