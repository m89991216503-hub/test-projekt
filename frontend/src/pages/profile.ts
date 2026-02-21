import { getProfile, changePassword, removeToken } from "../api";

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
  } catch {
    removeToken();
    onLogout();
  }
}
