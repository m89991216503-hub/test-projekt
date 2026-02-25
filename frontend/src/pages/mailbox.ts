import { getInbox, getSent, getMailMessage, fetchInbox, sendEmail, MailItem } from "../api";

type Tab = "inbox" | "sent" | "compose";

export async function renderMailbox(container: HTMLElement): Promise<void> {
  container.innerHTML = `<p class="hint">Загрузка почты...</p>`;

  let inbox: MailItem[] = [];
  let sent: MailItem[] = [];

  try {
    [inbox, sent] = await Promise.all([getInbox(), getSent()]);
  } catch {
    container.innerHTML = `<p class="hint mb-empty">Не удалось загрузить почту</p>`;
    return;
  }

  renderUI(container, inbox, sent, "inbox");
}

function renderUI(container: HTMLElement, inbox: MailItem[], sent: MailItem[], active: Tab): void {
  const unread = inbox.filter((m) => !m.is_read).length;

  container.innerHTML = `
    <div class="mb-tabs">
      <button class="mb-tab ${active === "inbox" ? "mb-tab--active" : ""}" data-tab="inbox">
        Входящие${unread > 0 ? ` <span class="mb-badge">${unread}</span>` : ""}
      </button>
      <button class="mb-tab ${active === "sent" ? "mb-tab--active" : ""}" data-tab="sent">Исходящие</button>
      <button class="mb-tab ${active === "compose" ? "mb-tab--active" : ""}" data-tab="compose">Написать</button>
    </div>

    <div id="mb-inbox" class="${active !== "inbox" ? "mb-hidden" : ""}">
      <div class="mb-toolbar">
        <button id="mb-refresh-btn" class="btn-sm">&#x27F3; Обновить</button>
        <span id="mb-refresh-info" class="hint" style="margin-left:10px;margin-bottom:0"></span>
      </div>
      <div id="mb-inbox-list">${msgList(inbox, "inbox")}</div>
    </div>

    <div id="mb-sent" class="${active !== "sent" ? "mb-hidden" : ""}">
      <div id="mb-sent-list">${msgList(sent, "sent")}</div>
    </div>

    <div id="mb-compose" class="${active !== "compose" ? "mb-hidden" : ""}">
      <form id="mb-form">
        <label>Кому (e-mail)</label>
        <input type="email" id="mb-to" placeholder="recipient@example.com" required />
        <label>Тема</label>
        <input type="text" id="mb-subject" placeholder="Тема письма" maxlength="255" required />
        <label>Текст письма</label>
        <textarea id="mb-body" rows="6" placeholder="Введите текст письма..." required></textarea>
        <button type="submit" id="mb-send-btn">Отправить</button>
        <p id="mb-send-error" class="error"></p>
        <p id="mb-send-success" class="success"></p>
      </form>
    </div>
  `;

  attachTabs(container, inbox, sent);
  attachRefresh(container);
  attachExpansion(container);
  attachCompose(container, sent);
}

function msgList(items: MailItem[], dir: "inbox" | "sent"): string {
  if (items.length === 0) return `<p class="hint mb-empty">Нет писем</p>`;
  return items.map((m) => {
    const date = new Date(m.created_at).toLocaleDateString("ru-RU");
    const unread = dir === "inbox" && !m.is_read;
    const addr = dir === "inbox" ? `От: ${esc(m.from_addr)}` : `Кому: ${esc(m.to_addr)}`;
    return `
      <div class="mb-row${unread ? " mb-row--unread" : ""}" data-id="${m.id}">
        <span class="mb-dot">${unread ? "●" : ""}</span>
        <span class="mb-from">${addr}</span>
        <span class="mb-subject">${esc(m.subject)}</span>
        <span class="mb-date">${date}</span>
      </div>
      <div class="mb-detail mb-hidden" id="mb-d-${m.id}">
        <p class="mb-meta">Загрузка...</p>
      </div>`;
  }).join("");
}

function attachTabs(container: HTMLElement, inbox: MailItem[], sent: MailItem[]): void {
  container.querySelectorAll<HTMLButtonElement>(".mb-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab as Tab;
      renderUI(container, inbox, sent, tab);
    });
  });
}

function attachRefresh(container: HTMLElement): void {
  const btn = container.querySelector<HTMLButtonElement>("#mb-refresh-btn");
  const info = container.querySelector<HTMLElement>("#mb-refresh-info");
  if (!btn || !info) return;

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.textContent = "Загрузка...";
    info.textContent = "";
    try {
      const res = await fetchInbox();
      let inbox: MailItem[] = [];
      let sent: MailItem[] = [];
      [inbox, sent] = await Promise.all([getInbox(), getSent()]);
      info.textContent = res.fetched > 0 ? `Получено новых: ${res.fetched}` : "Нет новых писем";
      renderUI(container, inbox, sent, "inbox");
    } catch (err: any) {
      info.textContent = err.message || "Ошибка обновления";
      btn.disabled = false;
      btn.textContent = "⟳ Обновить";
    }
  });
}

function attachExpansion(container: HTMLElement): void {
  container.querySelectorAll<HTMLElement>(".mb-row").forEach((row) => {
    row.addEventListener("click", async () => {
      const id = Number(row.dataset.id);
      const detail = container.querySelector<HTMLElement>(`#mb-d-${id}`);
      if (!detail) return;

      const isOpen = !detail.classList.contains("mb-hidden");
      if (isOpen) {
        detail.classList.add("mb-hidden");
        return;
      }

      detail.classList.remove("mb-hidden");
      row.classList.remove("mb-row--unread");
      row.querySelector<HTMLElement>(".mb-dot")!.textContent = "";

      try {
        const msg = await getMailMessage(id);
        const date = new Date(msg.created_at).toLocaleString("ru-RU");
        detail.innerHTML = `
          <p class="mb-meta">
            <strong>От:</strong> ${esc(msg.from_addr)}<br>
            <strong>Кому:</strong> ${esc(msg.to_addr)}<br>
            <strong>Дата:</strong> ${date}<br>
            <strong>Тема:</strong> ${esc(msg.subject)}
          </p>
          <pre class="mb-body">${esc(msg.body)}</pre>`;
      } catch (err: any) {
        detail.innerHTML = `<p class="error">${err.message || "Ошибка загрузки"}</p>`;
      }
    });
  });
}

function attachCompose(container: HTMLElement, sentCache: MailItem[]): void {
  const form = container.querySelector<HTMLFormElement>("#mb-form");
  if (!form) return;

  const errEl = container.querySelector<HTMLElement>("#mb-send-error")!;
  const okEl = container.querySelector<HTMLElement>("#mb-send-success")!;
  const btn = container.querySelector<HTMLButtonElement>("#mb-send-btn")!;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errEl.textContent = "";
    okEl.textContent = "";
    const to = (container.querySelector("#mb-to") as HTMLInputElement).value.trim();
    const subject = (container.querySelector("#mb-subject") as HTMLInputElement).value.trim();
    const body = (container.querySelector("#mb-body") as HTMLTextAreaElement).value.trim();

    btn.disabled = true;
    btn.textContent = "Отправка...";
    try {
      await sendEmail(to, subject, body);
      okEl.textContent = "Письмо отправлено";
      form.reset();
      const [inbox, sent] = await Promise.all([getInbox(), getSent()]);
      renderUI(container, inbox, sent, "sent");
    } catch (err: any) {
      errEl.textContent = err.message || "Ошибка отправки";
      btn.disabled = false;
      btn.textContent = "Отправить";
    }
  });
}

function esc(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
