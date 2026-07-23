document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("app-ready");

    const roleButtons = document.querySelectorAll("[data-role-option]");
    const roleInput = document.getElementById("rol");

    const selectRole = (selectedButton) => {
        const selectedRole = selectedButton.dataset.roleOption;

        roleButtons.forEach((option) => {
            const selected = option === selectedButton;
            option.classList.toggle("role-option--active", selected);
            option.setAttribute("aria-pressed", selected ? "true" : "false");
        });

        if (roleInput && selectedRole) {
            roleInput.value = selectedRole;
        }
    };

    if (roleButtons.length > 0) {
        const initialButton = Array.from(roleButtons).find(
            (button) => button.dataset.roleOption === roleInput?.value,
        ) || roleButtons[0];

        selectRole(initialButton);

        roleButtons.forEach((button) => {
            button.addEventListener("click", () => selectRole(button));
        });
    }

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
