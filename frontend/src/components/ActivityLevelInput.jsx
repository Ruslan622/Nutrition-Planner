export default function ActivityLevelInput({ value, onChange }) {
  return (
    <div>
      <label htmlFor="activity_level">Activity Level</label>
      <select
        id="activity_level"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      >
        <option value="">Select activity level</option>
        <option value="1">Sedentary (little or no exercise)</option>
        <option value="2">Light (exercise 1-3 days/week)</option>
        <option value="3">Moderate (exercise 3-5 days/week)</option>
        <option value="4">Active (exercise 6-7 days/week)</option>
        <option value="5">Very Active (intense exercise daily)</option>
      </select>
    </div>
  );
}
