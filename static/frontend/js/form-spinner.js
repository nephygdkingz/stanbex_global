document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("form.js-submit-spinner").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      const btn = form.querySelector('button[type="submit"]');
      if (btn && !btn.classList.contains("loading")) {
        btn.classList.add("loading");

        // Hide text if exists
        const textSpan = btn.querySelector(".btn-text");
        if (textSpan) {
          textSpan.style.display = "none";
        }

        // Add spinner only once
        const spinner = document.createElement("span");
        spinner.className = "spinner-border spinner-border-sm me-2";
        spinner.setAttribute("role", "status");
        spinner.setAttribute("aria-hidden", "true");
        btn.prepend(spinner);

        // Disable button
        btn.disabled = true;
      }

      // Submit form
      form.submit();
    });
  });
});
