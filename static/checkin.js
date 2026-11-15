
document.addEventListener("DOMContentLoaded", function () {
    const formularios = document.querySelectorAll("form[data-checkin]");

    formularios.forEach(function (formulario) {
        formulario.addEventListener("submit", function (evento) {
            if (formulario.dataset.enviando === "true") {
                evento.preventDefault();
                return;
            }

            formulario.dataset.enviando = "true";

            const botao = formulario.querySelector('button[type="submit"]');

            if (botao) {
                botao.disabled = true;
                botao.textContent = "Registrando presença...";
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const formularios = document.querySelectorAll("form[data-envio-unico]");

    formularios.forEach(function (formulario) {
        formulario.addEventListener("submit", function (evento) {
            if (formulario.dataset.enviando === "true") {
                evento.preventDefault();
                return;
            }

            formulario.dataset.enviando = "true";

            const botao = formulario.querySelector('button[type="submit"]');

            if (botao) {
                botao.disabled = true;
            }
        });
    });
});