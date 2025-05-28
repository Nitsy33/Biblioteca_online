document.addEventListener('DOMContentLoaded', function () {
    const filtro = document.getElementById('filtro-genero');
    const libros = document.querySelectorAll('.libro-item');

    filtro.addEventListener('change', function () {
        const seleccion = filtro.value.toLowerCase();

        libros.forEach(libro => {
            const generos = libro.dataset.generos.toLowerCase();
            if (seleccion === 'todos' || generos.includes(seleccion)) {
                libro.style.display = 'block';
            } else {
                libro.style.display = 'none';
            }
        });
    });
});
