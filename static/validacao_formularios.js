
document.addEventListener("DOMContentLoaded", function () {
    const formularios = document.querySelectorAll(
        "form[data-validar-cadastro]"
    );

    formularios.forEach(function (formulario) {
        let enviando = false;

        formulario.addEventListener("submit", function (evento) {
            if (enviando) {
                evento.preventDefault();
                return;
            }

            const campos = formulario.querySelectorAll(
                'input[type="text"], textarea'
            );

            campos.forEach(function (campo) {
                campo.value = campo.value.trim();
            });

            if (!formulario.checkValidity()) {
                evento.preventDefault();
                formulario.reportValidity();
                return;
            }

            enviando = true;
        });
    });
});
