import { register } from "../api";

const MAIL_DOMAIN = "school-pro100.ru";

export function renderRegister(onSuccess: () => void, onLogin: () => void): void {
  const app = document.getElementById("app")!;
  app.innerHTML = `
    <div class="card">
      <h1>Регистрация</h1>
      <form id="register-form">
        <label for="username">Логин</label>
        <input type="text" id="username" placeholder="только a-z, 0-9, точка, дефис (3–30 символов)" required minlength="3" maxlength="30" pattern="[a-z0-9._-]+" />
        <p id="mail-preview" class="hint" style="margin-top:-8px"></p>
        <label for="email">E-mail</label>
        <input type="email" id="email" placeholder="you@example.com" required />
        <label for="password">Пароль</label>
        <input type="password" id="password" placeholder="Минимум 6 символов" required minlength="6" />
        <label for="password-confirm">Подтвердите пароль</label>
        <input type="password" id="password-confirm" placeholder="Повторите пароль" required />
        <button type="submit">Зарегистрироваться</button>
        <p id="error" class="error"></p>
      </form>
      <p style="text-align:center;margin-top:16px">Уже есть аккаунт? <a href="#" class="link" id="go-login">Войти</a></p>
    </div>
  `;

  document.getElementById("go-login")!.addEventListener("click", (e) => {
    e.preventDefault();
    onLogin();
  });

  const usernameInput = document.getElementById("username") as HTMLInputElement;
  const mailPreview = document.getElementById("mail-preview")!;

  usernameInput.addEventListener("input", () => {
    const val = usernameInput.value.trim();
    if (val.length >= 3) {
      mailPreview.textContent = `Ваш почтовый адрес: ${val}@${MAIL_DOMAIN}`;
    } else {
      mailPreview.textContent = "";
    }
  });

  const form = document.getElementById("register-form") as HTMLFormElement;
  const errorEl = document.getElementById("error")!;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    const username = usernameInput.value.trim();
    const email = (document.getElementById("email") as HTMLInputElement).value;
    const password = (document.getElementById("password") as HTMLInputElement).value;
    const confirm = (document.getElementById("password-confirm") as HTMLInputElement).value;
    if (password !== confirm) {
      errorEl.textContent = "Пароли не совпадают";
      return;
    }
    try {
      await register(username, email, password);
      onSuccess();
    } catch (err: any) {
      errorEl.textContent = err.message || "Ошибка регистрации";
    }
  });
}
