import {
  getProfile,
  changePassword,
  removeToken,
  sendEmail,
  getProcessedTemplate,
  getAdminTemplate,
  saveAdminTemplate,
} from "../api";
import { renderMailbox } from "./mailbox";

export async function renderProfile(onLogout: () => void): Promise<void> {
  const app = document.getElementById("app")!;
  app.innerHTML = `<div class="card"><p>Загрузка...</p></div>`;

  try {
    const profile = await getProfile();
    const createdDate = new Date(profile.created_at).toLocaleDateString("ru-RU");

    if (profile.is_admin) {
      await renderAdminProfile(app, profile.email, createdDate, onLogout);
    } else {
      await renderUserProfile(app, profile.email, createdDate, onLogout);
    }
  } catch {
    removeToken();
    onLogout();
  }
}

async function renderAdminProfile(
  app: HTMLElement,
  email: string,
  createdDate: string,
  onLogout: () => void
): Promise<void> {
  const template = await getAdminTemplate().catch(() => ({ subject: "", body: "", ai_prompt: "" }));

  app.innerHTML = `
    <div class="card">
      <h1>Профиль <span style="font-size:0.75rem;background:#2563eb;color:#fff;padding:2px 8px;border-radius:12px;vertical-align:middle">Администратор</span></h1>
      <label for="profile-email">E-mail</label>
      <input type="email" id="profile-email" value="${email}" disabled />
      <p class="hint">Зарегистрирован: ${createdDate}</p>
      <hr />
      <h2>Сменить пароль</h2>
      <form id="password-form">
        <label for="old-password">Текущий пароль</label>
        <input type="password" id="old-password" placeholder="Текущий пароль" required />
        <label for="new-password">Новый пароль</label>
        <input type="password" id="new-password" placeholder="Новый пароль (мин. 6 символов)" required />
        <label for="confirm-password">Подтверждение</label>
        <input type="password" id="confirm-password" placeholder="Повторите новый пароль" required />
        <button type="submit">Сменить пароль</button>
        <p id="pwd-error" class="error"></p>
        <p id="pwd-success" class="success"></p>
      </form>
      <hr />
      <h2>Шаблон письма</h2>
      <p class="hint">Этот шаблон будет предзаполнять форму отправки письма у всех пользователей.</p>
      <form id="template-form">
        <label for="tmpl-subject">Тема шаблона</label>
        <input type="text" id="tmpl-subject" placeholder="Тема письма" maxlength="255" value="${escapeHtml(template.subject)}" />
        <label for="tmpl-body">Текст шаблона</label>
        <textarea id="tmpl-body" rows="6" placeholder="Текст письма...">${escapeHtml(template.body)}</textarea>
        <label for="tmpl-ai-prompt">AI-промт (инструкция для нейросети DeepSeek)</label>
        <textarea id="tmpl-ai-prompt" rows="4" placeholder="Например: Перепиши письмо в официальном деловом стиле, исправь ошибки, сделай текст более убедительным.">${escapeHtml(template.ai_prompt)}</textarea>
        <p class="hint">Если промт задан, шаблон будет обработан нейросетью перед подстановкой в форму пользователя.</p>
        <button type="submit" id="tmpl-submit-btn">Сохранить шаблон</button>
        <p id="tmpl-error" class="error"></p>
        <p id="tmpl-success" class="success"></p>
      </form>
      <hr />
      <h2>Почтовый ящик</h2>
      <div id="mailbox-container"></div>
      <hr />
      <button id="logout-btn" class="btn-secondary">Выйти</button>
    </div>
  `;

  document.getElementById("logout-btn")!.addEventListener("click", () => {
    removeToken();
    onLogout();
  });

  attachPasswordForm();
  await renderMailbox(document.getElementById("mailbox-container")!);

  const templateForm = document.getElementById("template-form") as HTMLFormElement;
  const tmplError = document.getElementById("tmpl-error")!;
  const tmplSuccess = document.getElementById("tmpl-success")!;
  const tmplSubmitBtn = document.getElementById("tmpl-submit-btn") as HTMLButtonElement;

  templateForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    tmplError.textContent = "";
    tmplSuccess.textContent = "";
    const subject = (document.getElementById("tmpl-subject") as HTMLInputElement).value;
    const body = (document.getElementById("tmpl-body") as HTMLTextAreaElement).value;
    const aiPrompt = (document.getElementById("tmpl-ai-prompt") as HTMLTextAreaElement).value;
    tmplSubmitBtn.disabled = true;
    tmplSubmitBtn.textContent = "Сохранение...";
    try {
      const msg = await saveAdminTemplate(subject, body, aiPrompt);
      tmplSuccess.textContent = msg;
    } catch (err: any) {
      tmplError.textContent = err.message || "Ошибка сохранения шаблона";
    } finally {
      tmplSubmitBtn.disabled = false;
      tmplSubmitBtn.textContent = "Сохранить шаблон";
    }
  });
}

async function renderUserProfile(
  app: HTMLElement,
  email: string,
  createdDate: string,
  onLogout: () => void
): Promise<void> {
  app.innerHTML = `
    <div class="card">
      <h1>Профиль</h1>
      <label for="profile-email">E-mail</label>
      <input type="email" id="profile-email" value="${email}" disabled />
      <p class="hint">Зарегистрирован: ${createdDate}</p>
      <hr />
      <h2>Сменить пароль</h2>
      <form id="password-form">
        <label for="old-password">Текущий пароль</label>
        <input type="password" id="old-password" placeholder="Текущий пароль" required />
        <label for="new-password">Новый пароль</label>
        <input type="password" id="new-password" placeholder="Новый пароль (мин. 6 символов)" required />
        <label for="confirm-password">Подтверждение</label>
        <input type="password" id="confirm-password" placeholder="Повторите новый пароль" required />
        <button type="submit">Сменить пароль</button>
        <p id="pwd-error" class="error"></p>
        <p id="pwd-success" class="success"></p>
      </form>
      <hr />
      <h2>Отправить письмо</h2>
      <form id="email-form">
        <label for="email-to">Кому (e-mail)</label>
        <input type="email" id="email-to" placeholder="recipient@example.com" required />
        <label for="email-subject">Тема</label>
        <input type="text" id="email-subject" placeholder="AI обрабатывает шаблон..." maxlength="255" required value="" />
        <label for="email-body">Текст письма</label>
        <textarea id="email-body" rows="6" placeholder="AI обрабатывает шаблон..." required></textarea>
        <button type="submit" id="email-submit-btn" disabled>Отправить</button>
        <p id="email-error" class="error"></p>
        <p id="email-success" class="success"></p>
      </form>
      <hr />
      <h2>Почтовый ящик</h2>
      <div id="mailbox-container"></div>
      <hr />
      <button id="logout-btn" class="btn-secondary">Выйти</button>
    </div>
  `;

  document.getElementById("logout-btn")!.addEventListener("click", () => {
    removeToken();
    onLogout();
  });

  attachPasswordForm();
  await renderMailbox(document.getElementById("mailbox-container")!);

  // Load AI-processed template asynchronously
  getProcessedTemplate()
    .then((t) => {
      const subjectEl = document.getElementById("email-subject") as HTMLInputElement | null;
      const bodyEl = document.getElementById("email-body") as HTMLTextAreaElement | null;
      const submitBtn = document.getElementById("email-submit-btn") as HTMLButtonElement | null;
      if (subjectEl) subjectEl.value = t.subject;
      if (bodyEl) bodyEl.value = t.body;
      if (submitBtn) submitBtn.disabled = false;
    })
    .catch(() => {
      const submitBtn = document.getElementById("email-submit-btn") as HTMLButtonElement | null;
      if (submitBtn) submitBtn.disabled = false;
    });

  const emailForm = document.getElementById("email-form") as HTMLFormElement;
  const emailErrorEl = document.getElementById("email-error")!;
  const emailSuccessEl = document.getElementById("email-success")!;
  const emailSubmitBtn = document.getElementById("email-submit-btn") as HTMLButtonElement;

  emailForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    emailErrorEl.textContent = "";
    emailSuccessEl.textContent = "";
    const to = (document.getElementById("email-to") as HTMLInputElement).value.trim();
    const subject = (document.getElementById("email-subject") as HTMLInputElement).value.trim();
    const body = (document.getElementById("email-body") as HTMLTextAreaElement).value.trim();
    emailSubmitBtn.disabled = true;
    emailSubmitBtn.textContent = "Отправка...";
    try {
      const msg = await sendEmail(to, subject, body);
      emailSuccessEl.textContent = msg;
      emailForm.reset();
    } catch (err: any) {
      emailErrorEl.textContent = err.message || "Ошибка отправки письма";
    } finally {
      emailSubmitBtn.disabled = false;
      emailSubmitBtn.textContent = "Отправить";
    }
  });
}

function attachPasswordForm(): void {
  const form = document.getElementById("password-form") as HTMLFormElement;
  const errorEl = document.getElementById("pwd-error")!;
  const successEl = document.getElementById("pwd-success")!;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    successEl.textContent = "";
    const oldPwd = (document.getElementById("old-password") as HTMLInputElement).value;
    const newPwd = (document.getElementById("new-password") as HTMLInputElement).value;
    const confirmPwd = (document.getElementById("confirm-password") as HTMLInputElement).value;
    if (newPwd !== confirmPwd) {
      errorEl.textContent = "Пароли не совпадают";
      return;
    }
    if (newPwd.length < 6) {
      errorEl.textContent = "Новый пароль должен быть не менее 6 символов";
      return;
    }
    try {
      const msg = await changePassword(oldPwd, newPwd);
      successEl.textContent = msg;
      form.reset();
    } catch (err: any) {
      errorEl.textContent = err.message || "Ошибка смены пароля";
    }
  });
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
