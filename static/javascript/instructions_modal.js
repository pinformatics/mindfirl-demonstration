document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("revealBtn");
  const section = document.getElementById("expandSection");

  btn.addEventListener("click", () => {
    section.classList.add("visible");
    section.classList.remove("hidden");
    btn.disabled = true; // optional: prevent toggling or hide button
  });
});
