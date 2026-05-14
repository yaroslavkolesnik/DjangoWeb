function applyTheme(theme) {
  var html  = document.documentElement;
  var sunD  = document.getElementById('theme-icon-sun');
  var moonD = document.getElementById('theme-icon-moon');
  var sunM  = document.getElementById('theme-icon-sun-mobile');
  var moonM = document.getElementById('theme-icon-moon-mobile');

  if (theme === 'dark') {
    html.classList.add('dark');
    if (sunD)  sunD.classList.remove('hidden');
    if (moonD) moonD.classList.add('hidden');
    if (sunM)  sunM.classList.remove('hidden');
    if (moonM) moonM.classList.add('hidden');
  } else {
    html.classList.remove('dark');
    if (sunD)  sunD.classList.add('hidden');
    if (moonD) moonD.classList.remove('hidden');
    if (sunM)  sunM.classList.add('hidden');
    if (moonM) moonM.classList.remove('hidden');
  }
}

document.addEventListener('DOMContentLoaded', function () {
  var saved  = localStorage.getItem('theme');
  var system = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  applyTheme(saved || system);

  function handleToggle() {
    var next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem('theme', next); } catch(e) {}
  }

  var btn  = document.getElementById('dark-mode-toggle');
  var btnM = document.getElementById('dark-mode-toggle-mobile');
  if (btn)  btn.addEventListener('click', handleToggle);
  if (btnM) btnM.addEventListener('click', handleToggle);
});

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

// слайдер на главной странице
document.addEventListener('DOMContentLoaded', function () {
    const track = document.getElementById('slider-track');

    if (!track) return;

    const prevBtn = document.getElementById('prev-slide');
    const nextBtn = document.getElementById('next-slide');
    const dots = document.querySelectorAll('.slider-dot');

    let currentIndex = 0;
    const totalSlides = dots.length;

    function updateSlider() {
        const offset = -currentIndex * 100;
        track.style.transform = `translateX(${offset}%)`;

        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('bg-white');
                dot.classList.remove('bg-white/50');
            } else {
                dot.classList.remove('bg-white');
                dot.classList.add('bg-white/50');
            }
        });
    }

    if (totalSlides > 0) {
        nextBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % totalSlides;
            updateSlider();
        });

        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
            updateSlider();
        });

        dots.forEach(dot => {
            dot.addEventListener('click', (e) => {
                currentIndex = parseInt(e.target.dataset.index);
                updateSlider();
            });
        });

        setInterval(() => {
            currentIndex = (currentIndex + 1) % totalSlides;
            updateSlider();
        }, 5000);

        updateSlider();
    }
});

// смена картинок на странице товара
window.changeMainImage = function(src) {
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.style.opacity = 0;
        setTimeout(() => {
            mainImage.src = src;
            mainImage.style.opacity = 1;
        }, 150);
    } else {
        console.error('Элемент #mainImage не найден!');
    }
}