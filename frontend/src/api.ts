const API_BASE = "/api";

function getToken(): string | null {
  return localStorage.getItem("token");
}

export function setToken(token: string): void {
  localStorage.setItem("token", token);
}

export function removeToken(): void {
  localStorage.removeItem("token");
}

export function hasToken(): boolean {
  return !!getToken();
}

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const resp = await fetch(API_BASE + url, { ...options, headers });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${resp.status}`);
  }
  return resp.json();
}

export async function login(email: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data.access_token;
}

export async function register(email: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data.access_token;
}

export async function getProfile(): Promise<{ email: string; created_at: string }> {
  return request("/me");
}

export async function changePassword(oldPassword: string, newPassword: string): Promise<string> {
  const data = await request<{ message: string }>("/me/password", {
    method: "PUT",
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
  });
  return data.message;
}

export async function sendEmail(to: string, subject: string, body: string): Promise<string> {
  const data = await request<{ message: string }>("/email/send", {
    method: "POST",
    body: JSON.stringify({ to, subject, body }),
  });
  return data.message;
}
