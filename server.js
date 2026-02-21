const express = require("express");
const app = express();
const PORT = 3000;

app.use(express.json());

app.post("/api/login", (req, res) => {
  const { email, password } = req.body;
  if (email === "user@example.com" && password === "password") {
    res.json({ success: true, message: "Вход выполнен успешно" });
  } else {
    res.status(401).json({ success: false, message: "Неверный e-mail или пароль" });
  }
});

app.get("/", (req, res) => {
  res.send(`<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Вход</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }
    .card { background: white; padding: 2rem 2.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 380px; }
    h1 { margin: 0 0 1.5rem; font-size: 1.5rem; color: #111; text-align: center; }
    label { display: block; margin-bottom: 0.25rem; font-size: 0.875rem; color: #444; }
    input { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; font-size: 1rem; outline: none; margin-bottom: 1rem; }
    input:focus { border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,0.2); }
    button { width: 100%; padding: 0.6rem; background: #2563eb; color: white; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    #message { margin-top: 1rem; text-align: center; font-size: 0.9rem; min-height: 1.2em; }
    .error { color: #dc2626; }
    .success { color: #16a34a; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Вход</h1>
    <form id="loginForm">
      <label for="email">E-mail</label>
      <input type="email" id="email" placeholder="you@example.com" required>
      <label for="password">Пароль</label>
      <input type="password" id="password" placeholder="Введите пароль" required>
      <button type="submit">Войти</button>
      <p id="message"></p>
    </form>
  </div>
  <script>
    document.getElementById("loginForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const msg = document.getElementById("message");
      msg.className = "";
      msg.textContent = "";
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;
      try {
        const res = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        msg.textContent = data.message;
        msg.className = data.success ? "success" : "error";
      } catch {
        msg.textContent = "Ошибка соединения";
        msg.className = "error";
      }
    });
  </script>
</body>
</html>`);
});

app.listen(PORT, () => {
  console.log("Server running at http://localhost:" + PORT);
});
