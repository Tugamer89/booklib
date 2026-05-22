## 2024-05-22 - Password Toggle Accessibility Pattern

**Learning:** The application uses an interactive eye icon for toggling password visibility across auth forms, but it was implemented using a `<span>` element. This completely prevents keyboard-only users and screen readers from interacting with or understanding the toggle, breaking an essential part of the login/registration UX.
**Action:** Always use `<button type="button">` for interactive UI toggles instead of generic elements, and include a descriptive `aria-label` (e.g., "Toggle password visibility") for icon-only actions.
