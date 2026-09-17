import { useCallback, useEffect, useState } from "react";

import { api } from "./api/client.js";
import Login from "./components/Login.jsx";
import Pagination from "./components/Pagination.jsx";
import TaskFilters from "./components/TaskFilters.jsx";
import TaskForm from "./components/TaskForm.jsx";
import TaskList from "./components/TaskList.jsx";
import { useAuth } from "./context/AuthContext.jsx";

const PAGE_SIZE = 5;

export default function App() {
  const { token, user, loading, logout } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ status: "", due_date: "" });
  const [editingTask, setEditingTask] = useState(null);
  const [error, setError] = useState("");

  const loadTasks = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.listTasks(token, { ...filters, page, page_size: PAGE_SIZE });
      setTasks(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err.message);
    }
  }, [token, filters, page]);

  useEffect(() => {
    if (!token) return;
    api.listUsers(token).then(setUsers).catch(() => setUsers([]));
  }, [token]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleFilterChange = (next) => {
    setFilters(next);
    setPage(1);
  };

  const handleCreateOrUpdate = async (data) => {
    try {
      if (editingTask) {
        await api.updateTask(token, editingTask.id, data);
        setEditingTask(null);
      } else {
        await api.createTask(token, data);
      }
      await loadTasks();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStart = async (task) => {
    await api.updateTask(token, task.id, { status: "in_progress" });
    loadTasks();
  };

  const handleStop = async (task) => {
    await api.updateTask(token, task.id, { status: "pending" });
    loadTasks();
  };

  const handleComplete = async (task) => {
    await api.completeTask(token, task.id);
    loadTasks();
  };

  const handleDelete = async (task) => {
    if (!confirm(`Delete "${task.title}"?`)) return;
    await api.deleteTask(token, task.id);
    loadTasks();
  };

  if (loading) return <div className="centered">Loading…</div>;
  if (!token || !user) return <Login />;

  return (
    <div className="app-shell">
      <header>
        <h1>Task Manager</h1>
        <div>
          <span>{user.full_name}</span>
          <button type="button" className="secondary" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      {error && (
        <p className="error" onClick={() => setError("")}>
          {error}
        </p>
      )}

      <main>
        <section className="panel">
          <h2>{editingTask ? "Edit task" : "New task"}</h2>
          <TaskForm
            users={users}
            initialTask={editingTask}
            onSubmit={handleCreateOrUpdate}
            onCancel={() => setEditingTask(null)}
          />
        </section>

        <section className="panel">
          <h2>Tasks</h2>
          <TaskFilters filters={filters} onChange={handleFilterChange} />
          <TaskList
            tasks={tasks}
            users={users}
            onEdit={setEditingTask}
            onStart={handleStart}
            onStop={handleStop}
            onComplete={handleComplete}
            onDelete={handleDelete}
          />
          <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPageChange={setPage} />
        </section>
      </main>
    </div>
  );
}
