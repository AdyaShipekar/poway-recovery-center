document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#login-form"), message = document.querySelector("#login-message");
  form.addEventListener("submit", e => { e.preventDefault(); message.textContent = "Demo login successful. No credentials were transmitted."; });
  document.querySelector("#guest-login").addEventListener("click", () => { message.textContent = "You are continuing as a guest."; });
});