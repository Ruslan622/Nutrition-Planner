export default function WeightInput({ value, onChange }) {
  return (
    <div>
      <label htmlFor="weight">Weight (kg)</label>
      <input
        id="weight"
        type="number"
        min="30"
        max="300"
        step="0.1"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        placeholder="Enter your weight"
      />
    </div>
  );
}
