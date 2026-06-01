export default function GoalDropdown({ value, onChange }) {
  return (
    <div>
      <label htmlFor="goal">Goal</label>
      <select
        id="goal"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Select a goal</option>
        <option value="loss">Weight Loss</option>
        <option value="maintenance">Maintenance</option>
        <option value="gain">Weight Gain</option>
      </select>
    </div>
  );
}
