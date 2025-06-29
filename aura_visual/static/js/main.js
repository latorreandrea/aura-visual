

document.addEventListener('DOMContentLoaded', function() {
  // Prima carica il contenuto essenziale
    setTimeout(function() {
        // Poi inizializza AOS con impostazioni ottimizzate
        AOS.init({
            duration: 800,         // Durata ridotta
            easing: 'ease-out',    // Easing più leggero
            once: true,            // Una sola animazione
            disable: 'mobile',     // Disabilita su mobile
            startEvent: 'load',    // Inizia al caricamento completo
            throttleDelay: 99      // Aumenta throttle delay
        });
    }, 100);
    // Selettori principali
    const selectHeader = document.querySelector('#header');
    const selectMobileNav = document.querySelector('.mobile-nav-toggle');
    const selectNavbarNav = document.querySelector('.navbar');

    // Funzione per gestire l'header durante lo scroll
    function headerScrolled() {
        if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled');
        } else {
        selectHeader.classList.remove('header-scrolled');
        }
    }
    
    // Controlla lo stato iniziale
    headerScrolled();
    
    // Controlla durante lo scroll
    document.addEventListener('scroll', headerScrolled);

    // Attiva il menu mobile
    if (selectMobileNav) {
        selectMobileNav.addEventListener('click', function() {
        selectNavbarNav.classList.toggle('navbar-mobile');
        this.classList.toggle('bi-list');
        this.classList.toggle('bi-x');
        });
  }

  // Attiva dropdown sul mobile
  const navDropdowns = document.querySelectorAll('.navbar .dropdown > a');
  
  navDropdowns.forEach(function(el) {
    el.addEventListener('click', function(event) {
      if (selectNavbarNav.classList.contains('navbar-mobile')) {
        event.preventDefault();
        this.nextElementSibling.classList.toggle('dropdown-active');
      }
    });
  });

  // Attivazione elemento navbar durante lo scroll
  const sections = document.querySelectorAll('section');
  const navLinks = document.querySelectorAll('.nav-link.scrollto');

  window.addEventListener('scroll', function() {
    let current = '';
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 80;
      const sectionHeight = section.offsetHeight;
      
      if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + current) {
        link.classList.add('active');
      }
    });
  });
});