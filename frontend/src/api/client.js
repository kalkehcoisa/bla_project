const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

async function request(path, { method = "GET", body, token, form } = {}) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body && !form) headers["Content-Type"] = "application/json";

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: form ? body : body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  register: (data) => request("/auth/register", { method: "POST", body: data }),

  login: (email, password) => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    return request("/auth/login", { method: "POST", body: form, form: true });
  },

  me: (token) => request("/users/me", { token }),
  listUsers: (token) => request("/users/", { token }),

  listTasks: (token, params = {}) => {
    const query = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v != null))
    );
    return request(`/tasks/?${query.toString()}`, { token });
  },

  createTask: (token, data) => request("/tasks/", { method: "POST", body: data, token }),
  updateTask: (token, id, data) =>
    request(`/tasks/${id}`, { method: "PATCH", body: data, token }),
  completeTask: (token, id) => request(`/tasks/${id}/complete`, { method: "POST", token }),
  deleteTask: (token, id) => request(`/tasks/${id}`, { method: "DELETE", token }),
};
