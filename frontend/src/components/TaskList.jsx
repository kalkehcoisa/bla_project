const STATUS_LABELS = {
  pending: "Pending",
  in_progress: "In progress",
  done: "Done",
};

export default function TaskList({ tasks, users, onEdit, onStart, onStop, onComplete, onDelete }) {
  const userName = (id) => users.find((u) => u.id === id)?.full_name || "Unassigned";

  if (tasks.length === 0) {
    return <p className="empty-state">No tasks match the current filters.</p>;
  }

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <li key={task.id} className={`task-card status-${task.status}`}>
          <div className="task-main">
            <h3>{task.title}</h3>
            {task.description && <p>{task.description}</p>}
            <div className="task-meta">
              <span className="badge">{STATUS_LABELS[task.status]}</span>
              {task.due_date && <span>Due {task.due_date}</span>}
              <span>Assigned to {userName(task.assignee_id)}</span>
            </div>
          </div>
          <div className="task-actions">
            {task.status === "pending" && (
              <button type="button" onClick={() => onStart(task)}>
                Start
              </button>
            )}
            {task.status === "in_progress" && (
              <button type="button" className="secondary" onClick={() => onStop(task)}>
                Stop
              </button>
            )}
            {task.status !== "done" && (
              <button type="button" onClick={() => onComplete(task)}>
                Mark done
              </button>
            )}
            <button type="button" className="secondary" onClick={() => onEdit(task)}>
              Edit
            </button>
            <button type="button" className="danger" onClick={() => onDelete(task)}>
              Delete
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
