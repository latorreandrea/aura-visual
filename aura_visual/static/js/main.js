document.addEventListener('DOMContentLoaded', function() {
  // First load the essential content
    setTimeout(function() {
        // Then initialize AOS with optimized settings
        AOS.init({
            duration: 800,         // Reduced duration
            easing: 'ease-out',    // Lighter easing
            once: true,            // Single animation only
            disable: 'mobile',     // Disable on mobile
            startEvent: 'load',    // Start on complete load
            throttleDelay: 99      // Increase throttle delay
        });
    }, 100);
    // Main selectors
    const selectHeader = document.querySelector('#header');
    const selectMobileNav = document.querySelector('.mobile-nav-toggle');
    const selectNavbarNav = document.querySelector('.navbar');

    // Function to handle header during scroll
    function headerScrolled() {
        if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled');
        } else {
        selectHeader.classList.remove('header-scrolled');
        }
    }
    
    // Check initial state
    headerScrolled();
    
    // Check during scroll
    document.addEventListener('scroll', headerScrolled);

    // Activate mobile menu
    if (selectMobileNav) {
        selectMobileNav.addEventListener('click', function() {
        selectNavbarNav.classList.toggle('navbar-mobile');
        this.classList.toggle('bi-list');
        this.classList.toggle('bi-x');
        });
  }

    // Function to close mobile navbar
  function closeMobileNav() {
    selectNavbarNav.classList.remove('navbar-mobile');
    selectMobileNav.classList.add('bi-list');
    selectMobileNav.classList.remove('bi-x');
  }

  // Close mobile navbar when clicking on a menu item
  const navbarLinks = document.querySelectorAll('.navbar .nav-link.scrollto');
  
  navbarLinks.forEach(function(link) {
    link.addEventListener('click', function() {
      // If mobile navbar is open, close it
      if (selectNavbarNav.classList.contains('navbar-mobile')) {
        closeMobileNav();
      }
    });
  });

  // Activate dropdown on mobile
  const navDropdowns = document.querySelectorAll('.navbar .dropdown > a');
  
  navDropdowns.forEach(function(el) {
    el.addEventListener('click', function(event) {
      if (selectNavbarNav.classList.contains('navbar-mobile')) {
        event.preventDefault();
        this.nextElementSibling.classList.toggle('dropdown-active');
      }
    });
  });

  // Activate navbar element during scroll
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
