document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".main-nav");
  if (menuToggle) menuToggle.addEventListener("click", () => nav.classList.toggle("open"));

  const carousel = document.querySelector("[data-carousel]");
  if (carousel) {
    const slides = [...carousel.querySelectorAll(".carousel-slide")];
    const dots = carousel.querySelector(".carousel-dots");
    let index = 0;
    slides.forEach((_, i) => {
      const dot = document.createElement("button");
      dot.setAttribute("aria-label", `Go to slide ${i + 1}`);
      dot.addEventListener("click", () => show(i));
      dots.appendChild(dot);
    });
    const show = (i) => {
      index = (i + slides.length) % slides.length;
      slides.forEach((s, n) => s.classList.toggle("is-active", n === index));
      [...dots.children].forEach((d, n) => d.classList.toggle("active", n === index));
    };
    carousel.querySelector(".prev").addEventListener("click", () => show(index - 1));
    carousel.querySelector(".next").addEventListener("click", () => show(index + 1));
    show(0);
    setInterval(() => show(index + 1), 7000);
  }

  const chatbot = document.querySelector("[data-chatbot]");
  if (chatbot) {
    const toggle = chatbot.querySelector(".chatbot-toggle");
    const panel = chatbot.querySelector(".chatbot-panel");
    const close = chatbot.querySelector(".chatbot-close");
    const form = chatbot.querySelector(".chatbot-form");
    const input = form.querySelector("input");
    const messages = chatbot.querySelector(".chatbot-messages");
    const replies = [
      {keys:["withdraw","shaking","sweat","sick"], text:"Withdrawal can feel intense and deserves real support. If symptoms are severe, new, or worsening, contact a medical professional or urgent care. You do not have to manage this alone."},
      {keys:["panic","anxious","anxiety","overwhelm","racing"], text:"That sounds like a lot to carry. Try naming five things you can see, then place both feet on the floor. If you feel unsafe, contact someone you trust or call/text 988."},
      {keys:["trigger","angry","anger","urge","craving"], text:"An urge can be strong without being a command. If possible, create a little distance from the trigger, contact a supportive person, and focus on the next ten minutes rather than the whole day."},
      {keys:["lonely","alone","sad","depressed"], text:"You deserve connection, even if reaching out feels difficult. Consider sending one simple message: “I could use some company.” You can also explore a meeting or local resource on this site."}
    ];
    const add = (text, cls) => { const el = document.createElement("div"); el.className = cls; el.textContent = text; messages.appendChild(el); messages.scrollTop = messages.scrollHeight; };
    toggle.addEventListener("click", () => { panel.hidden = !panel.hidden; if (!panel.hidden) input.focus(); });
    close.addEventListener("click", () => panel.hidden = true);
    form.addEventListener("submit", e => {
      e.preventDefault(); const text = input.value.trim(); if (!text) return; add(text, "user-message"); input.value = "";
      setTimeout(() => {
        const lower = text.toLowerCase();
        const match = replies.find(r => r.keys.some(k => lower.includes(k)));
        add(match ? match.text : "Thank you for saying that out loud. I can help you find a grounding exercise, explore meetings, or locate professional support. What would feel like the most manageable next step?", "bot-message");
      }, 350);
    });
  }
});