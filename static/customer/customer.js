document.addEventListener("DOMContentLoaded", () => {
  // Toggle sidebar visibility on smaller screens
  const sidebar = document.getElementById("sidebar");
  const menuBar = document.getElementById("menu_bar");
  const menuBarClose = document.getElementById("menu_bar_close");

  // Open sidebar
  menuBar.addEventListener("click", () => {
    sidebar.classList.add("active");
    menuBar.classList.add("d-none");
    menuBarClose.classList.remove("d-none");
  });

  // Close sidebar
  menuBarClose.addEventListener("click", () => {
    sidebar.classList.remove("active");
    menuBarClose.classList.add("d-none");
    menuBar.classList.remove("d-none");
  });
});
