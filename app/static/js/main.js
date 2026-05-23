document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("app-ready");

    const selectedClasses = [
        "border-secondary-container",
        "bg-blue-50",
        "text-primary",
        "shadow-[0_16px_36px_rgba(0,88,190,0.14)]",
        "-translate-y-0.5",
    ];
    const idleClasses = ["border-outline-variant", "bg-white", "text-slate-500", "shadow-sm"];

    document.querySelectorAll("[data-role-option]").forEach((button) => {
        button.addEventListener("click", () => {
            const selectedRole = button.dataset.roleOption;
            const roleInput = document.getElementById("rol");

            document.querySelectorAll("[data-role-option]").forEach((option) => {
                const selected = option === button;
                option.classList.toggle("is-selected", selected);
                option.setAttribute("aria-pressed", selected ? "true" : "false");
                option.classList.toggle("[&_.material-symbols-rounded]:bg-primary", selected);
                option.classList.toggle("[&_.material-symbols-rounded]:text-white", selected);
                option.classList.toggle("[&_.material-symbols-rounded]:bg-blue-50", !selected);
                option.classList.toggle("[&_.material-symbols-rounded]:text-secondary", !selected);
                selectedClasses.forEach((className) => option.classList.toggle(className, selected));
                idleClasses.forEach((className) => option.classList.toggle(className, !selected));
            });

            if (roleInput && selectedRole) {
                roleInput.value = selectedRole;
            }
        });
    });

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const inputId = button.getAttribute("aria-controls");
            const passwordInput = inputId ? document.getElementById(inputId) : null;

            if (!passwordInput) {
                return;
            }

            const isPassword = passwordInput.type === "password";
            const label = button.querySelector(".password-toggle-label");
            const icon = button.querySelector(".password-toggle-icon");
            const nextLabel = isPassword ? "Ocultar" : "Mostrar";

            passwordInput.type = isPassword ? "text" : "password";

            if (label) {
                label.textContent = nextLabel;
            } else {
                button.textContent = nextLabel;
            }

            if (icon) {
                icon.textContent = isPassword ? "visibility_off" : "visibility";
            }

            button.setAttribute(
                "aria-label",
                isPassword ? "Ocultar contraseña" : "Mostrar contraseña",
            );
        });
    });
});
