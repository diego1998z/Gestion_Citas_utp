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

    document.querySelectorAll("[data-appointment-slot]").forEach((select) => {
        const form = select.closest("form");
        const fechaSelect = form?.querySelector("[data-appointment-date-select]");
        const fechaInput = form?.querySelector("[data-appointment-date]");
        const horaInput = form?.querySelector("[data-appointment-time]");
        const placeholderOption = select.querySelector("option[value='']");
        const timeOptions = Array.from(select.options).filter((option) => option.value);

        const filterTimeOptions = () => {
            const selectedDate = fechaSelect?.value || "";
            let visibleOptions = 0;

            timeOptions.forEach((option) => {
                const sameDate = option.dataset.fecha === selectedDate;
                option.hidden = !sameDate;
                option.disabled = !sameDate;

                if (sameDate) {
                    visibleOptions += 1;
                }
            });

            if (placeholderOption) {
                placeholderOption.textContent = selectedDate
                    ? "Seleccionar hora"
                    : "Primero seleccioná una fecha";
            }

            if (!selectedDate || select.selectedOptions[0]?.dataset.fecha !== selectedDate) {
                select.value = "";
            }

            select.disabled = !selectedDate || visibleOptions === 0;
        };

        const syncAppointmentSlot = () => {
            const selectedOption = select.options[select.selectedIndex];

            if (!selectedOption || !selectedOption.value) {
                if (fechaInput) fechaInput.value = "";
                if (horaInput) horaInput.value = "";
                return;
            }

            if (fechaInput) {
                fechaInput.value = selectedOption.dataset.fecha || "";
            }

            if (horaInput) {
                horaInput.value = selectedOption.dataset.hora || "";
            }
        };

        fechaSelect?.addEventListener("change", () => {
            filterTimeOptions();
            syncAppointmentSlot();
        });

        select.addEventListener("change", syncAppointmentSlot);
        filterTimeOptions();
        syncAppointmentSlot();
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
