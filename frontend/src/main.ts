import { hasToken } from "./api";
import { renderLogin } from "./pages/login";
import { renderProfile } from "./pages/profile";

function router(): void {
  if (hasToken()) {
    renderProfile(() => router());
  } else {
    renderLogin(() => router());
  }
}

router();
