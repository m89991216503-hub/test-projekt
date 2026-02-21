import { register } from "../api";

export function renderRegister(onSuccess: () => void, onLogin: () => void): void {
  const app = document.getElementById("app")!;
  app.innerHTML = `
    <div class="card">
      <h1>Регистрация</h1>
      <form id="register-form">
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

  const form = document.getElementById("register-form") as HTMLFormElement;
  const errorEl = document.getElementById("error")!;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    const email = (document.getElementById("email") as HTMLInputElement).value;
    const password = (document.getElementById("password") as HTMLInputElement).value;
    const confirm = (document.getElementById("password-confirm") as HTMLInputElement).value;
    if (password !== confirm) {
      errorEl.textContent = "Пароли не совпадают";
      return;
    }
    try {
      await register(email, password);
      onSuccess();
    } catch (err: any) {
      errorEl.textContent = err.message || "Ошибка регистрации";
    }
  });
}
