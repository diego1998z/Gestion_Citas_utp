document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("app-ready");

    document.querySelectorAll("[data-role-option]").forEach((button) => {
        button.addEventListener("click", () => {
            const selected_role = button.dataset.roleOption;
            const role_input = document.getElementById("rol");

            document.querySelectorAll("[data-role-option]").forEach((option) => {
                option.classList.toggle("is-selected", option === button);
            });

            if (role_input && selected_role) {
                role_input.value = selected_role;
            }
        });
    });

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const input_id = button.getAttribute("aria-controls");
            const password_input = input_id ? document.getElementById(input_id) : null;

            if (!password_input) {
                return;
            }

            const is_password = password_input.type === "password";
            password_input.type = is_password ? "text" : "password";
            button.textContent = is_password ? "Ocultar" : "Mostrar";
            button.setAttribute(
                "aria-label",
                is_password ? "Ocultar contraseña" : "Mostrar contraseña",
            );
        });
    });
});
