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
});