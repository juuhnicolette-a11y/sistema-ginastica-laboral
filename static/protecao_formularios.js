
document.addEventListener("DOMContentLoaded", function () {
    const formularios = document.querySelectorAll(
        "form[data-proteger-alteracoes]"
    );

    formularios.forEach(function (formulario) {
        let alterado = false;
        let enviando = false;

        formulario.addEventListener("input", function () {
            alterado = true;
        });

        formulario.addEventListener("change", function () {
            alterado = true;
        });

        formulario.addEventListener("submit", function () {
            if (formulario.checkValidity()) {
                enviando = true;
            }
        });

        window.addEventListener("beforeunload", function (evento) {
            if (alterado && !enviando) {
                evento.preventDefault();
                evento.returnValue = "";
            }
        });
    });
});
