const sidebar = document.querySelector("#sidebar");
const toggler = document.querySelector(".toggler-btn");
const sidebarItems = document.querySelectorAll(".sidebar-item");

toggler.addEventListener("click", function () {
  sidebar.classList.toggle("collapsed");

  if (sidebar.classList.contains("collapsed")) {
    sidebarLogo.style.marginLeft = "39.5px";
  } else {
    toggler.style.backgroundColor = "transparent";
    sidebarLogo.style.marginLeft = "0";
  }
});

sidebarItems.forEach((item) => {
  item.addEventListener("click", function () {
    sidebarItems.forEach((i) => i.classList.remove("active"));
    this.classList.add("active");
  });
});