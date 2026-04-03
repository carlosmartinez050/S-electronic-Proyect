
// Función para obtener CSRF token
function getCookie(name) {
    // Para csrftoken, primero busca en el input hidden del DOM
    if (name === 'csrftoken') {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) {
            return token.value;
        }
    }
    
    // Si no está en el DOM, busca en las cookies
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}








// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }



const iconoCarrito = document.getElementById("icon-carrito");
const contenedorTransparente = document.getElementById("content-modal-trasparent");

iconoCarrito.addEventListener("click", () => {
    cargarCarrito();
});


function cargarCarrito() {
    fetch('/ver_carrito/')
        .then(response => response.text())
        .then(html => {
            document.getElementById("content-cart").innerHTML = html;
            contenedorTransparente.classList.remove("hidden");
            
            // Agregar eventos a los inputs después de cargar el HTML
            agregarEventosInputs();

            const mensaje = document.getElementById("mensaje-descuento");
            if (mensaje) {
                setTimeout(() => {
                    mensaje.remove(); // lo elimina del DOM
                }, 6000);
            }


            const btnCompletar = document.getElementById("btn-procces-envio");
            if (btnCompletar) {
                btnCompletar.addEventListener("click", finalizarCompra);
                console.log("se clikeo el boton")
            }

            // Agregar evento al botón cerrar carrito (móvil)
            const btnCerrar = document.querySelector(".btn-cerrar");
            if (btnCerrar) {
                btnCerrar.addEventListener("click", () => {
                    contenedorTransparente.classList.add("hidden");
                });
            }
        })
        .catch(error => console.error("Error al cargar el carrito:", error));
}


contenedorTransparente.addEventListener("click", (event) => {
   if (event.target === contenedorTransparente){
        contenedorTransparente.classList.add("hidden");
   }
 
});


function agregarProducto(productoId) {
    console.log("Intentando agregar producto:", productoId);
    
    fetch(`/agregar_al_carrito/${productoId}/`, {
        method: 'POST',  
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    }) 
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log("Producto agregado al carrito:", productoId);
            cargarCarrito();
        }
    })
    .catch(error => console.error("Error al agregar producto:", error));
}






// function agregarProducto(productoId) {
//     fetch(`/agregar_al_carrito/${productoId}/`, {
//         method: 'POST',  
//         headers: {
//             'X-Requested-With': 'XMLHttpRequest',
//             'X-CSRFToken': getCookie('csrftoken')
//         }
//     }) 
//     .then(response => response.json()) 
//     .then(data => {
//         if (data.success) {
//             console.log("Producto agregado al carrito:", productoId);
//             cargarCarrito();
//         }
//     })
//     .catch(error => console.error("Error al agregar producto:", error));
// }


function agregarEventosInputs() {
    const valorCantidadInput = document.querySelectorAll(".cantidad-input");
    
    let debounceTimer = null;

    valorCantidadInput.forEach(input => {
        input.addEventListener('input', function() {
            const productoId = this.dataset.productoId;
            const valor = this.value;

            // Cancela el timer anterior si el usuario sigue escribiendo
            clearTimeout(debounceTimer);

            // Solo ejecuta cuando el usuario para 500ms
            debounceTimer = setTimeout(() => {
                actualizarCantidad(productoId, valor);
            }, 500);
        });
    });

      // los botones de eliminar
    const botonesEliminar = document.querySelectorAll(".btn-eliminar");

    botonesEliminar.forEach(boton => {
        boton.addEventListener("click", function() {
            eliminarProducto(this.dataset.productoId);
        });
    });
}



function actualizarCantidad(productoId, nuevaCantidad) {
    const formData = new FormData();
    formData.append('cantidad', nuevaCantidad);
    
    fetch(`/agregar_al_carrito/${productoId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar el carrito completo para recalcular descuentos
            cargarCarrito();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Si hay error, recargar el carrito completo
        cargarCarrito();
    });

}



function eliminarProducto(productoId) {
    fetch(`/eliminar_producto/${productoId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Eliminar el li del DOM
            document.querySelector(`.btn-eliminar[data-producto-id="${productoId}"]`).closest("li").remove();

            // Actualizar totales
            document.getElementById("total-articulos").textContent = data.total_articulos;
            document.getElementById("total-precio").textContent = data.total_precio.toFixed(2);
        }
    })
    .catch(err => console.error("Error al eliminar producto:", err));
}


function aplicarDescuento() {
    fetch('/aplicar_descuento/', {
        method: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')}
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cargarCarrito();
        }
    });
}


function finalizarCompra() {
    fetch('/finalizar_compra/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("✅ ¡Compra finalizada con éxito!");
            cargarCarrito(); // carrito vacío otra vez
        }
    });
}







// evento para cerrar con el boton cerrar carrito
const btnCerrarCarrito = document.getElementById("btn-cerrar-carrito");

btnCerrarCarrito.addEventListener("click", () => {
    contenedorTransparente.classList.add("hidden");
});









//! document.addEventListener('DOMContentLoaded', ()=>{
//         fetch('http://127.0.0.1:8000/ver_carrito/')
//   .then(respuesta => {
//     console.log(respuesta)
    
//   })
//   .catch(error => {
//     console.log(error)
  
//   });
// })


// iconoCarrito.addEventListener("click", () => {
//     contenedorTransparente.classList.toggle("hidden");


// });

// contenedorTransparente.addEventListener("click", (event) => {
//    if (event.target === contenedorTransparente){
//         contenedorTransparente.classList.add("hidden");
//    }
 
// });




// // iconoCarrito.addEventListener("click", () => {
// //     contenedorTransparente.classList.add("hidden");
// // });

// // iconoCarrito.addEventListener("click", () => {
// //     contenedorTransparente.classList.remove("hidden");
// // });



