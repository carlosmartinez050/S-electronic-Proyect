// ======= MENU HAMBURGUESA (MOBILE) ======

const btnHamburguesa = document.getElementById('btn-menu-hamburguesa');
const menuMovil      = document.getElementById('menu-movil');
const btnCerrar      = document.getElementById('btn-cerrar-menu');

/* Abrir */
btnHamburguesa.addEventListener('click', () => {
    menuMovil.classList.add('activo');
});

/* Cerrar con la X */
btnCerrar.addEventListener('click', () => {
    menuMovil.classList.remove('activo');
});

/* Cerrar si el usuario hace click fuera del menú */
menuMovil.addEventListener('click', (e) => {
    if (e.target === menuMovil) {
        menuMovil.classList.remove('activo');
    }
});


// ======= CONTENEDOR INPUT (APARECE AL HACER CLIC EN ICONO) ======

iconoBuscar = document.getElementById('container-logo-search-input');
categoriasPadre = document.querySelectorAll('.tags-label');


iconoBuscar.addEventListener('click', () => {
    const contenedorInput = document.getElementById('container-search-input');
    categoriasPadre.forEach(cat => {
        cat.classList.toggle('oculto');
    }); console.log(categoriasPadre);

    contenedorInput.classList.toggle('active');     // Muestra u oculta el contenedor del input de búsqueda
});

// JS PARA EL INPUT DE BÚSQUEDA EN EL HEADER (DESKTOP)
const inputBusqueda = document.getElementById('input-search');

inputBusqueda.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Evita que el formulario se envíe automáticamente
        this.form.submit();    // Envía el formulario manualmente
    } else if (event.key === 'Escape') {
        this.value = '';       // Limpia el input si se presiona Escape
    }
});


// JS PARA EL INPUT DE BÚSQUEDA EN EL HEADER (MOBILE)
const inputBusquedaMobile = document.getElementById('input-search-mobile');
const iconoLupaMobile = document.getElementById('icon-search-mobile');

iconoLupaMobile.addEventListener('click', () => {
    if (inputBusquedaMobile.value.trim() !== '') {
        inputBusquedaMobile.form.submit(); // Envía el formulario si el input no está vacío
    }
});


// ══════════════════════════════════════════
// USER DROPDOWN
// ══════════════════════════════════════════

const iconoUsuario = document.getElementById('icon-usuario');
const userDropdown = document.getElementById('user-dropdown');
const userDropdownWrapper = document.getElementById('user-dropdown-wrapper');

// Abrir/cerrar al hacer clic en el ícono
iconoUsuario.addEventListener('click', (e) => {
    e.stopPropagation(); // Evita que el click se propague al document
    userDropdown.classList.toggle('active');
});

// Cerrar al hacer clic fuera del dropdown
document.addEventListener('click', (e) => {
    if (!userDropdownWrapper.contains(e.target)) {
        userDropdown.classList.remove('active');
    }
});

