export default function HeightInput({ value, onChange }) {
  return (
    <div>
      <label htmlFor="height">Height (cm)</label>
      <input
        id="height"
        type="number"
        min="100"
        max="250"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        placeholder="Enter your height"
      />
    </div>
  );
}
