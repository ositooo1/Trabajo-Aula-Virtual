/* =========================================================
   AULA VIRTUAL
   Funciones generales del frontend
========================================================= */


/* =========================================================
   1. SESIÓN
========================================================= */

/*
    Devuelve el token guardado después del login.

    Si no existe, devuelve null.
*/
function getToken() {
    return localStorage.getItem('token');
}


/*
    Devuelve los datos del usuario guardados
    en localStorage.

    Se utiliza try/catch para evitar que la aplicación
    se rompa si por algún motivo el contenido guardado
    no es un JSON válido.
*/
function getUser() {

    const userData = localStorage.getItem('user');

    if (!userData) {
        return null;
    }

    try {
        return JSON.parse(userData);
    } catch (error) {

        console.error(
            'Error al leer los datos del usuario:',
            error
        );

        localStorage.removeItem('user');

        return null;
    }
}


/*
    Elimina los datos de la sesión local
    y envía al usuario al login.
*/
function logout() {

    localStorage.removeItem('token');
    localStorage.removeItem('user');

    window.location.href = '/login';
}


/* =========================================================
   2. MODAL GENERAL
========================================================= */

/*
    Devuelve la instancia del modal Bootstrap
    definido en base.html.

    Esto permite reutilizar UN SOLO modal para:
    - crear cursos
    - editar cursos
    - crear evaluaciones
    - agregar contenidos
    - etc.
*/
function getAppModal() {

    const modalElement =
        document.getElementById('appModal');

    if (!modalElement) {

        console.error(
            'No se encontró el modal #appModal'
        );

        return null;
    }

    return bootstrap.Modal.getOrCreateInstance(
        modalElement
    );
}


/*
    Abre el modal general.

    titulo:
        texto que aparecerá arriba.

    contenido:
        HTML que irá dentro del modal.
*/
function showModal(titulo, contenido) {

    const titleElement =
        document.getElementById('modalTitle');

    const bodyElement =
        document.getElementById('modalBody');

    if (!titleElement || !bodyElement) {

        console.error(
            'No se encontraron los elementos del modal.'
        );

        return;
    }


    titleElement.textContent = titulo;

    bodyElement.innerHTML = contenido;


    const modal = getAppModal();

    if (modal) {
        modal.show();
    }
}


/*
    Cierra el modal Bootstrap.
*/
function closeModal() {

    const modal = getAppModal();

    if (modal) {
        modal.hide();
    }
}


/* =========================================================
   3. ALERTAS
========================================================= */

/*
    Muestra mensajes visuales dentro del elemento:

        <div id="alerts"></div>

    Ejemplos:

        showAlert(
            'Curso creado correctamente',
            'success'
        );

        showAlert(
            'No se pudo crear el curso',
            'error'
        );
*/
function showAlert(message, type = 'info') {

    const container =
        document.getElementById('alerts');

    if (!container) {

        console.warn(
            'No existe un contenedor #alerts'
        );

        return;
    }


    /*
        Traducimos nuestros nombres simples
        a las clases de Bootstrap.
    */

    const alertTypes = {
        success: 'success',
        error: 'danger',
        warning: 'warning',
        info: 'info'
    };


    const bootstrapType =
        alertTypes[type] || 'info';


    const alert = document.createElement('div');


    alert.className =
        `alert alert-${bootstrapType} ` +
        `alert-dismissible fade show`;


    alert.setAttribute(
        'role',
        'alert'
    );


    /*
        Usamos textContent para el mensaje.

        Esto es importante porque evita interpretar
        texto recibido como HTML.
    */

    const messageText =
        document.createElement('span');

    messageText.textContent = message;


    /*
        Botón X de Bootstrap.
    */

    const closeButton =
        document.createElement('button');

    closeButton.type = 'button';

    closeButton.className = 'btn-close';

    closeButton.setAttribute(
        'data-bs-dismiss',
        'alert'
    );

    closeButton.setAttribute(
        'aria-label',
        'Cerrar'
    );


    alert.appendChild(messageText);

    alert.appendChild(closeButton);


    container.appendChild(alert);


    /*
        Después de unos segundos quitamos
        automáticamente el mensaje.

        Si el usuario ya lo cerró manualmente,
        simplemente no hacemos nada.
    */

    setTimeout(() => {

        if (alert.parentNode) {

            const bootstrapAlert =
                bootstrap.Alert.getOrCreateInstance(
                    alert
                );

            bootstrapAlert.close();
        }

    }, 4000);
}


/* =========================================================
   4. PETICIONES A LA API
========================================================= */

/*
    Función general para comunicarnos con Flask.

    Ejemplos:

        api('/courses');

        api(
            '/courses',
            'POST',
            {
                name: 'Programación'
            }
        );

        api(
            '/courses/2',
            'PUT',
            datos
        );
*/
async function api(
    endpoint,
    method = 'GET',
    data = null
) {

    const config = {

        method: method,

        headers: {}

    };


    /*
        Si existe token, lo mandamos al backend.

        Flask espera:

        Authorization: Bearer TOKEN
    */

    const token = getToken();

    if (token) {

        config.headers['Authorization'] =
            'Bearer ' + token;

    }


    /*
        Solamente agregamos Content-Type
        cuando realmente estamos enviando datos.
    */

    if (data !== null) {

        config.headers['Content-Type'] =
            'application/json';

        config.body =
            JSON.stringify(data);

    }


    try {

        const response =
            await fetch(
                '/api' + endpoint,
                config
            );


        /*
            Si el backend devuelve 401 significa
            que la sesión ya no es válida.

            Limpiamos los datos locales y volvemos
            al login.
        */

        if (response.status === 401) {

            logout();

            return null;
        }


        /*
            No asumimos automáticamente que
            siempre llegará JSON.

            Esto evita errores si en algún momento
            Flask devuelve una respuesta vacía.
        */

        const contentType =
            response.headers.get(
                'content-type'
            ) || '';


        let result = {};


        if (
            contentType.includes(
                'application/json'
            )
        ) {

            result =
                await response.json();

        } else {

            const text =
                await response.text();

            if (text) {

                result = {
                    message: text
                };

            }

        }


        /*
            Si Flask responde con 400, 403,
            404, 500, etc., lo mostramos.
        */

        if (!response.ok) {

            showAlert(
                result.message ||
                'Ocurrió un error.',
                'error'
            );

            return null;
        }


        /*
            Si todo salió correctamente,
            devolvemos los datos al HTML
            que hizo la petición.
        */

        return result;


    } catch (error) {

        console.error(
            'Error de conexión con la API:',
            error
        );


        showAlert(
            'No se pudo conectar con el servidor.',
            'error'
        );


        return null;
    }
}


/*5. NAVEGACIÓN.*/

/*
    Marca automáticamente como activo el enlace correspondiente a la pantalla actual.

    Por ejemplo:

        /dashboard -> Dashboard activo.
        /courses   -> Mis Cursos activo.
*/
function updateActiveNavigation() {

    const currentPath =
        window.location.pathname;


    const links =
        document.querySelectorAll(
            '.sidebar-link'
        );


    links.forEach(link => {

        const href =
            link.getAttribute('href');


        /*Primero quitamos cualquier clase active anterior.n*/

        link.classList.remove(
            'active'
        );


        /*Inicio solamente se activa en, "/". */

        if (
            href === '/' &&
            currentPath === '/'
        ) {

            link.classList.add(
                'active'
            );

            return;
        }


        /* Para el resto aceptamos también subrutas.*/

        if (
            href !== '/' &&
            currentPath.startsWith(href)
        ) {

            link.classList.add(
                'active'
            );

        }

    });
}

/* Se ejecuta cuando termina de cargarse el HTML. */
document.addEventListener(
    'DOMContentLoaded',
    updateActiveNavigation
);