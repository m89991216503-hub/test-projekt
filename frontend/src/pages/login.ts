import { login } from "../api";

export function renderLogin(onSuccess: () => void, onRegister: () => void): void {
  const app = document.getElementById("app")!;
  app.innerHTML = `
    <div class="card">
      <h1>Вход</h1>
      <form id="login-form">
        <label for="login-input">E-mail или логин</label>
        <input type="text" id="login-input" placeholder="you@example.com или admin" required />
        <label for="password">Пароль</label>
        <input type="password" id="password" placeholder="Пароль" required />
        <button type="submit">Войти</button>
        <p id="error" class="error"></p>
      </form>
      <p style="text-align:center;margin-top:16px">Нет аккаунта? <a href="#" class="link" id="go-register">Зарегистрироваться</a></p>
    </div>
  `;

  const form = document.getElementById("login-form") as HTMLFormElement;
  const errorEl = document.getElementById("error")!;

  document.getElementById("go-register")!.addEventListener("click", (e) => {
    e.preventDefault();
    onRegister();
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    const loginValue = (document.getElementById("login-input") as HTMLInputElement).value;
    const password = (document.getElementById("password") as HTMLInputElement).value;
    try {
      await login(loginValue, password);
      onSuccess();
    } catch (err: any) {
      errorEl.textContent = err.message || "Ошибка входа";
    }
  });
}
