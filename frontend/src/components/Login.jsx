import { useState } from "react";

import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(form.email, form.password);
      } else {
        await register(form);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-card">
      <h1>Task Manager</h1>
      <div className="tabs">
        <button
          className={mode === "login" ? "active" : ""}
          onClick={() => setMode("login")}
          type="button"
        >
          Sign in
        </button>
        <button
          className={mode === "register" ? "active" : ""}
          onClick={() => setMode("register")}
          type="button"
        >
          Create account
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {mode === "register" && (
          <input
            placeholder="Full name"
            value={form.full_name}
            onChange={handleChange("full_name")}
            required
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange("email")}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange("password")}
          minLength={8}
          required
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {mode === "login" ? "Sign in" : "Create account"}
        </button>
      </form>

      <p className="hint">Demo credentials: demo@example.com / demo1234</p>
    </div>
  );
}
