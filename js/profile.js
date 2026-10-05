import { getCredentials } from './api/login.js';
import { putUpdate, getAllUsers, logoutUser } from './api/profile.js';

document.addEventListener("DOMContentLoaded", async () => {
  const user = await getCredentials();
  if (!user) { window.location.href = "login.html"; return; }

  const form = document.querySelector("#profile-form"), message = document.querySelector("#profile-message");
  const passwordForm = document.querySelector("#password-form"), passwordMessage = document.querySelector("#password-message");

  function show(u) {
    document.querySelector("#profile-name").textContent = u.name.split(" ")[0];
    document.querySelector("#member-since").textContent = new Date(u.created_at).toLocaleDateString(undefined, { month: "long", year: "numeric" });
    form.uid.value = u.uid; form.name.value = u.name; form.email.value = u.email; form.phone.value = u.phone;
  }
  show(user);
  document.querySelector(".profile-page").hidden = false;

  form.addEventListener("submit", async e => {
    e.preventDefault();
    message.textContent = "Saving…";
    try {
      show(await putUpdate({ name: form.name.value, email: form.email.value, phone: form.phone.value }));
      message.textContent = "Your information has been saved.";
      if (user.is_admin) loadMembers();
    } catch (err) { message.textContent = err.message; }
  });

  passwordForm.addEventListener("submit", async e => {
    e.preventDefault();
    if (passwordForm.new_password.value !== passwordForm.confirm.value) { passwordMessage.textContent = "New passwords do not match."; return; }
    passwordMessage.textContent = "Updating…";
    try {
      await putUpdate({ current_password: passwordForm.current_password.value, new_password: passwordForm.new_password.value });
      passwordForm.reset(); passwordMessage.textContent = "Password updated.";
    } catch (err) { passwordMessage.textContent = err.message; }
  });

  document.querySelector("#logout").addEventListener("click", logoutUser);

  // Admins see everyone registered in the database
  async function loadMembers() {
    const rows = document.querySelector("#members-table tbody");
    rows.innerHTML = "";
    for (const m of await getAllUsers()) {
      const tr = document.createElement("tr");
      [m.name, m.uid, m.email || "—", m.phone || "—", m.role].forEach(value => {
        const td = document.createElement("td"); td.textContent = value; tr.appendChild(td);
      });
      rows.appendChild(tr);
    }
  }
  if (user.is_admin) {
    document.querySelector("#members").hidden = false;
    loadMembers().catch(err => { document.querySelector("#members-message").textContent = err.message; });
  }
});
