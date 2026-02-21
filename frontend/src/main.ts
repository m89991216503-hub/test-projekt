import { hasToken } from "./api";
import { renderLogin } from "./pages/login";
import { renderRegister } from "./pages/register";
import { renderProfile } from "./pages/profile";

type Page = "login" | "register";
let currentPage: Page = "login";

function router(): void {
  if (hasToken()) {
    renderProfile(() => router());
  } else if (currentPage === "register") {
    renderRegister(() => router(), () => { currentPage = "login"; router(); });
  } else {
    renderLogin(() => router(), () => { currentPage = "register"; router(); });
  }
}

router();
