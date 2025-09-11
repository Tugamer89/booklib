const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");
const authAction = document.getElementById("authAction");
const submitButton = document.getElementById("submitButton");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const confirmGroup = document.getElementById("confirmPasswordGroup");
const confirmPassword = document.getElementById("confirmPassword");
const passwordMismatch = document.getElementById("passwordMismatch");

function switchMode(mode) {
    authAction.value = mode;
    localStorage.setItem("authMode", mode);

    if (mode === "login") {
        loginTab.classList.add("border-blue-600", "text-blue-700", "bg-blue-100");
        registerTab.classList.remove("border-green-600", "text-green-700", "bg-green-100");
        usernameInput.classList.remove("focus:ring-green-500");
        passwordInput.classList.remove("focus:ring-green-500");
        usernameInput.classList.add("focus:ring-blue-500");
        passwordInput.classList.add("focus:ring-blue-500");
        confirmGroup.classList.add("hidden");
        submitButton.textContent = "Accedi";
        submitButton.style.backgroundColor = "#2563eb";
    } else {
        registerTab.classList.add("border-green-600", "text-green-700", "bg-green-100");
        loginTab.classList.remove("border-blue-600", "text-blue-700", "bg-blue-100");
        usernameInput.classList.remove("focus:ring-blue-500");
        passwordInput.classList.remove("focus:ring-blue-500");
        usernameInput.classList.add("focus:ring-green-500");
        passwordInput.classList.add("focus:ring-green-500");
        confirmGroup.classList.remove("hidden");
        submitButton.textContent = "Registrati";
        submitButton.style.backgroundColor = "#16a34a";
    }

    passwordMismatch.classList.add("hidden");
}

loginTab.addEventListener("click", () => switchMode("login"));
registerTab.addEventListener("click", () => switchMode("register"));

document.getElementById("authForm").addEventListener("submit", function(e) {
    if (authAction.value === "register") {
        const pw = document.querySelector("input[name='password']").value;
        if (confirmPassword.value !== pw) {
            e.preventDefault();
            passwordMismatch.classList.remove("hidden");
        } else {
            passwordMismatch.classList.add("hidden");
        }
    }
});

const savedMode = localStorage.getItem("authMode") || "login"
switchMode(savedMode);
