console.log('JavaScript подключен');

// кнопка открытия и закрытия меню на телефонах
const menuToggle = document.getElementById('menu-toggle');
const menuClose = document.getElementById('menu-close');
const mobileMenu = document.getElementById('mobile-menu');

menuToggle.addEventListener('click', () => {
   mobileMenu.classList.remove('-translate-x-full');
});

menuClose.addEventListener('click', () => {
  mobileMenu.classList.add('-translate-x-full');
});

// кнопка поднятия вверх
document.addEventListener("DOMContentLoaded", function() {

    const backToTopButton = document.createElement("a");
    backToTopButton.href = "#";
    backToTopButton.id = "ui-to-top-custom";
    backToTopButton.className = "ui-to-top fa fa-angle-up";
    backToTopButton.setAttribute("aria-label", "Вернуться наверх");

    document.body.appendChild(backToTopButton);

    const button = document.getElementById("ui-to-top-custom");

    const minScroll = 500;
    const scrollSpeed = 800;

    window.addEventListener("scroll", function() {
        if (window.scrollY > minScroll) {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
        }
    });

    button.addEventListener("click", function(e) {
        e.preventDefault();

        if (document.documentElement.scrollTop === 0 && document.body.scrollTop === 0) {
            return;
        }

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });
});