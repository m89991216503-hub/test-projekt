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

export async function login(loginValue: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/login", {
    method: "POST",
    body: JSON.stringify({ login: loginValue, password }),
  });
  setToken(data.access_token);
  return data.access_token;
}

export async function register(username: string, email: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
  setToken(data.access_token);
  return data.access_token;
}

export async function getProfile(): Promise<{
  username: string;
  email: string;
  mail_address: string;
  created_at: string;
  is_admin: boolean;
}> {
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

export async function getEmailTemplate(): Promise<{ subject: string; body: string }> {
  return request("/email/template");
}

export async function getProcessedTemplate(): Promise<{ subject: string; body: string }> {
  return request("/email/template/processed");
}

export async function getAdminTemplate(): Promise<{ subject: string; body: string; ai_prompt: string }> {
  return request("/admin/template");
}

export async function saveAdminTemplate(subject: string, body: string, ai_prompt: string): Promise<string> {
  const data = await request<{ message: string }>("/admin/template", {
    method: "PUT",
    body: JSON.stringify({ subject, body, ai_prompt }),
  });
  return data.message;
}

export interface MailItem {
  id: number;
  direction: string;
  from_addr: string;
  to_addr: string;
  subject: string;
  created_at: string;
  is_read: boolean;
}

export interface MailDetail extends MailItem {
  body: string;
}

export async function getInbox(): Promise<MailItem[]> {
  return request("/mailbox/inbox");
}

export async function getSent(): Promise<MailItem[]> {
  return request("/mailbox/sent");
}

export async function getMailMessage(id: number): Promise<MailDetail> {
  return request(`/mailbox/${id}`);
}

export async function fetchInbox(): Promise<{ fetched: number }> {
  return request("/mailbox/fetch", { method: "POST" });
}
