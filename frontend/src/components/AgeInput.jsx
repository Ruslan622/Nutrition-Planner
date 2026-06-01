export default function AgeInput({ value, onChange }) {
  return (
    <div>
      <label htmlFor="age">Age (years)</label>
      <input
        id="age"
        type="number"
        min="18"
        max="100"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        placeholder="Enter your age"
      />
    </div>
  );
}
