export default function TaskFilters({ filters, onChange }) {
  const handleChange = (field) => (e) => onChange({ ...filters, [field]: e.target.value });

  return (
    <div className="filters">
      <select value={filters.status} onChange={handleChange("status")}>
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="in_progress">In progress</option>
        <option value="done">Done</option>
      </select>
      <label>
        Due date
        <input type="date" value={filters.due_date} onChange={handleChange("due_date")} />
      </label>
      {(filters.status || filters.due_date) && (
        <button
          type="button"
          className="secondary"
          onClick={() => onChange({ status: "", due_date: "" })}
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
