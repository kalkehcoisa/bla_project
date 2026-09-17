import { useEffect, useState } from "react";

const EMPTY_TASK = { title: "", description: "", due_date: "", assignee_id: "" };

export default function TaskForm({ users, initialTask, onSubmit, onCancel }) {
  const [form, setForm] = useState(EMPTY_TASK);

  useEffect(() => {
    if (initialTask) {
      setForm({
        title: initialTask.title,
        description: initialTask.description || "",
        due_date: initialTask.due_date || "",
        assignee_id: initialTask.assignee_id || "",
      });
    } else {
      setForm(EMPTY_TASK);
    }
  }, [initialTask]);

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      due_date: form.due_date || null,
      assignee_id: form.assignee_id ? Number(form.assignee_id) : null,
    });
  };

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <input
        placeholder="Title"
        value={form.title}
        onChange={handleChange("title")}
        required
      />
      <textarea
        placeholder="Description"
        value={form.description}
        onChange={handleChange("description")}
        rows={3}
      />
      <div className="form-row">
        <label>
          Due date
          <input type="date" value={form.due_date} onChange={handleChange("due_date")} />
        </label>
      </div>
      <div className="form-row">
        <label>
          Assignee
          <select value={form.assignee_id} onChange={handleChange("assignee_id")}>
            <option value="">Unassigned</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.full_name}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="form-actions">
        <button type="submit">{initialTask ? "Save changes" : "Add task"}</button>
        {initialTask && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
