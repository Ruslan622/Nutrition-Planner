export default function MacroRingsChart({
  proteinPercent,
  fatsPercent,
  carbsPercent,
}) {
  // Ring radii for concentric circles
  const outerR = 90; // Protein (outer)
  const middleR = 68; // Fats (middle)
  const innerR = 46; // Carbs (inner)

  const outerCircumference = 2 * Math.PI * outerR;
  const middleCircumference = 2 * Math.PI * middleR;
  const innerCircumference = 2 * Math.PI * innerR;

  // Calculate stroke-dasharray for each ring
  const proteinDash = (proteinPercent / 100) * outerCircumference;
  const fatsDash = (fatsPercent / 100) * middleCircumference;
  const carbsDash = (carbsPercent / 100) * innerCircumference;

  return (
    <div className="macro-chart-container">
      <div className="chart-wrapper">
        <svg viewBox="0 0 220 220" className="macro-chart-svg">
          {/* Background rings */}
          <circle cx="110" cy="110" r={outerR} className="chart-bg-outer" />
          <circle cx="110" cy="110" r={middleR} className="chart-bg-middle" />
          <circle cx="110" cy="110" r={innerR} className="chart-bg-inner" />

          {/* Progress rings */}
          <circle
            cx="110"
            cy="110"
            r={outerR}
            className="chart-segment protein"
            style={{
              strokeDasharray: `${proteinDash} ${outerCircumference}`,
            }}
          />
          <circle
            cx="110"
            cy="110"
            r={middleR}
            className="chart-segment fats"
            style={{
              strokeDasharray: `${fatsDash} ${middleCircumference}`,
            }}
          />
          <circle
            cx="110"
            cy="110"
            r={innerR}
            className="chart-segment carbs"
            style={{
              strokeDasharray: `${carbsDash} ${innerCircumference}`,
            }}
          />
        </svg>
      </div>

      {/* Legend */}
      <div className="macro-legend">
        <div className="legend-item">
          <span className="legend-dot protein"></span>
          <span>Protein {Math.round(proteinPercent)}%</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot fats"></span>
          <span>Fats {Math.round(fatsPercent)}%</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot carbs"></span>
          <span>Carbs {Math.round(carbsPercent)}%</span>
        </div>
      </div>
    </div>
  );
}
