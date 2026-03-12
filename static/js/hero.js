// ============================================
// HERO CAROUSEL - JavaScript
// ============================================

// Esperar a que el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    
    // ===== VARIABLES ===== //
    const slides = document.querySelectorAll('.hero-slide');  // Todos los slides
    const prevBtn = document.querySelector('.hero-prev');      // Botón anterior
    const nextBtn = document.querySelector('.hero-next');      // Botón siguiente
    
    let currentSlide = 0;           // Slide actual (empieza en 0)
    let autoplayInterval;           // Variable para el intervalo automático
    const autoplayDelay = 4000;     // 5 segundos entre cambios
    
    
    // ===== FUNCIÓN: Mostrar un slide específico =====
    function showSlide(index) {
        // Quitar clase 'active' de todos los slides
        slides.forEach(slide => {
            slide.classList.remove('active');
        });
        
        // Agregar clase 'active' al slide correspondiente
        slides[index].classList.add('active');
        
        // Actualizar el slide actual
        currentSlide = index;
    }
    
    
    // ===== FUNCIÓN: Siguiente slide =====
    function nextSlide() {
        // Si estamos en el último slide, volver al primero
        if (currentSlide >= slides.length - 1) {
            showSlide(0);
        } else {
            showSlide(currentSlide + 1);
        }
    }
    
    
    // ===== FUNCIÓN: Slide anterior =====
    function prevSlide() {
        // Si estamos en el primer slide, ir al último
        if (currentSlide <= 0) {
            showSlide(slides.length - 1);
        } else {
            showSlide(currentSlide - 1);
        }
    }
    
    
    // ===== FUNCIÓN: Iniciar autoplay =====
    function startAutoplay() {
        autoplayInterval = setInterval(nextSlide, autoplayDelay);
    }
    
    
    // ===== FUNCIÓN: Detener autoplay =====
    function stopAutoplay() {
        clearInterval(autoplayInterval);
    }
    
    
    // ===== EVENT LISTENERS =====
    
    // Botón "Siguiente"
    nextBtn.addEventListener('click', function() {
        nextSlide();
        stopAutoplay();   // Detener autoplay al hacer clic
        startAutoplay();  // Reiniciar autoplay
    });
    
    // Botón "Anterior"
    prevBtn.addEventListener('click', function() {
        prevSlide();
        stopAutoplay();
        startAutoplay();
    });
    
    
    // ===== INICIAR AUTOPLAY =====
    startAutoplay();
});