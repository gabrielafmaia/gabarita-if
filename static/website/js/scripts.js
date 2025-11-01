document.addEventListener("DOMContentLoaded", function () {
  const navLinks = document.querySelectorAll('.sb-topnav .nav-link[href^="#"]');

  const sections = Array.from(navLinks)
    .map((link) => {
      const id = link.getAttribute("href");
      const section = document.querySelector(id);
      return { link, section };
    })
    .filter((item) => item.section !== null);

  function setActiveLink(currentId) {
    navLinks.forEach((link) => {
      link.classList.remove("active");
      if (link.getAttribute("href") === `#${currentId}`) {
        link.classList.add("active");
      }
    });
  }

  window.addEventListener("scroll", () => {
    let currentSectionId = "";
    const navHeight = document.querySelector(".sb-topnav").offsetHeight;
    const scrollPosition = window.scrollY + navHeight + 20;

    sections.forEach(({ section }) => {
      if (section.offsetTop <= scrollPosition) {
        currentSectionId = section.id;
      }
    });

    if (!currentSectionId && sections.length > 0) {
      currentSectionId = sections[0].section.id;
      if (window.scrollY < 10) {
        setActiveLink("");
        return;
      }
    }

    setActiveLink(currentSectionId);
  });

  window.dispatchEvent(new Event("scroll"));
});
