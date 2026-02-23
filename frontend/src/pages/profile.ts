import { getProfile, changePassword, removeToken, sendEmail } from "../api";

export async function renderProfile(onLogout: () => void): Promise<void> {
  const app = document.getElementById("app")!;
  app.innerHTML = `<div class="card"><p>Загрузка...</p></div>`;

  try {
    const profile = await getProfile();
    const createdDate = new Date(profile.created_at).toLocaleDateString("ru-RU");

    app.innerHTML = `
      <div class="card">
        <h1>Профиль</h1>
        <label for="profile-email">E-mail</label>
        <input type="email" id="profile-email" value="${profile.email}" disabled />
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
          <input type="text" id="email-subject" placeholder="Тема письма" maxlength="255" required />
          <label for="email-body">Текст письма</label>
          <textarea id="email-body" rows="6" placeholder="Введите текст письма..." required></textarea>
          <button type="submit" id="email-submit-btn">Отправить</button>
          <p id="email-error" class="error"></p>
          <p id="email-success" class="success"></p>
        </form>
        <hr />
        <button id="logout-btn" class="btn-secondary">Выйти</button>
      </div>
    `;

    document.getElementById("logout-btn")!.addEventListener("click", () => {
      removeToken();
      onLogout();
    });

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
  } catch {
    removeToken();
    onLogout();
  }
}
