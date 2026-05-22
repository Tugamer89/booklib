## $(date +%Y-%m-%d) - Fix Open Redirect in Referer

**Vulnerability:** Open Redirect in `routes/books.py` due to blind trust of `referer` header during `/add`, `/edit`, `/delete` actions.
**Learning:** `request.headers.get("referer")` can be manipulated by an attacker. Redirecting directly to it can lead to phishing attacks, where a user submits an action and gets redirected to a malicious site.
**Prevention:** Use `urllib.parse.urlparse` to validate the `netloc` of the referer URL against the application's `request.url.netloc`.
