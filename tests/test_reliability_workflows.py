import os
import smtplib
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class SettingsTests(unittest.TestCase):
    def test_int_env_falls_back_to_default_for_empty_or_invalid_values(self):
        from config.settings import _int_env

        for value in ("", "abc", "587.0"):
            with self.subTest(value=value):
                with patch.dict(os.environ, {"SMTP_PORT": value}):
                    self.assertEqual(_int_env("SMTP_PORT", 587), 587)


class ReminderServiceTests(unittest.TestCase):
    def test_send_pending_reminders_continues_after_per_cita_failure(self):
        from app.services.mail_service import MailConfigurationError
        from app.services import reminder_service

        citas = [
            {"id_cita": 101, "paciente_email": "missing@example.test"},
            {"id_cita": 202, "paciente_email": "ok@example.test"},
        ]
        cita_model = MagicMock()
        cita_model.listar_pendientes_recordatorio.return_value = citas

        with patch.object(reminder_service, "CitaModel", return_value=cita_model), patch.object(
            reminder_service,
            "send_appointment_notification",
            side_effect=[MailConfigurationError("SMTP no está configurado."), None],
        ) as send_notification:
            sent = reminder_service.send_pending_reminders()

        self.assertEqual(sent, 1)
        self.assertEqual(send_notification.call_count, 2)
        cita_model.marcar_notificada.assert_called_once_with(202)
        cita_model.registrar_notificacion_fallida.assert_called_once_with(101, "SMTP no está configurado.")

    def test_send_pending_reminders_continues_after_smtp_failure(self):
        from app.services import reminder_service

        citas = [
            {"id_cita": 301, "paciente_email": "first@example.test"},
            {"id_cita": 302, "paciente_email": "second@example.test"},
        ]
        cita_model = MagicMock()
        cita_model.listar_pendientes_recordatorio.return_value = citas

        with patch.object(reminder_service, "CitaModel", return_value=cita_model), patch.object(
            reminder_service,
            "send_appointment_notification",
            side_effect=[smtplib.SMTPException("temporary failure"), None],
        ):
            sent = reminder_service.send_pending_reminders()

        self.assertEqual(sent, 1)
        cita_model.marcar_notificada.assert_called_once_with(302)
        cita_model.registrar_notificacion_fallida.assert_called_once_with(301, "No se pudo enviar el correo SMTP.")


class MailServiceTests(unittest.TestCase):
    def test_send_appointment_notification_fails_gracefully_when_smtp_config_missing(self):
        from app.services.mail_service import MailConfigurationError, send_appointment_notification

        cita = {"paciente_email": "patient@example.test", "fecha": "2026-06-25", "hora": "09:00", "medico": "Dr. Test"}

        with patch("app.services.mail_service.Config.SMTP_HOST", ""), patch(
            "app.services.mail_service.Config.SMTP_FROM", ""
        ), patch("app.services.mail_service.smtplib.SMTP") as smtp:
            with self.assertRaises(MailConfigurationError):
                send_appointment_notification(cita)

        smtp.assert_not_called()


class CitaNotificationControllerTests(unittest.TestCase):
    def test_notificar_does_not_send_smtp_for_ineligible_cita(self):
        from app import create_app
        from app.controllers import cita_controller

        app = create_app()
        app.config.update(TESTING=True)
        cita_model = MagicMock()
        cita_model.obtener_por_id.return_value = {"id_cita": 404, "estado": "CANCELADA"}
        cita_model.es_notificable.return_value = False

        with app.test_client() as client:
            with client.session_transaction() as session:
                session["id_usuario"] = 1
                session["rol"] = "RECEPCIONISTA"

            with patch.object(cita_controller, "cita_model", cita_model), patch.object(
                cita_controller,
                "send_appointment_notification",
            ) as send_notification:
                response = client.post("/citas/404/notificar")

        self.assertEqual(response.status_code, 302)
        send_notification.assert_not_called()
        cita_model.marcar_notificada.assert_not_called()
        cita_model.registrar_notificacion_fallida.assert_not_called()


class DashboardControllerTests(unittest.TestCase):
    def test_general_dashboard_uses_model_data(self):
        from app import create_app
        from app.controllers import home_controller

        app = create_app()
        app.config.update(TESTING=True)
        model = MagicMock()
        model.obtener_dashboard_operativo.return_value = {
            "resumen_citas": {
                "citas_hoy": 7,
                "pendientes_hoy": 3,
                "canceladas_24h": 2,
                "pendientes_notificacion": 4,
            },
            "total_pacientes": 11,
            "disponibilidad": {"medicos_disponibles": 5, "especialidades_disponibles": 4},
            "proximas_citas": [{"id_cita": 99}],
            "actividad": [{"tipo_evento": "NO_ASISTIO", "paciente": "Demo Patient", "actor": "Recepción"}],
            "medicos_sin_horario": 1,
            "pacientes_contacto_incompleto": 2,
        }

        with app.test_request_context("/"):
            with patch.object(home_controller, "cita_model", model):
                dashboard = home_controller._crear_dashboard_general()

        model.obtener_dashboard_operativo.assert_called_once_with()
        self.assertEqual(dashboard["resumen"][0]["valor"], 7)
        self.assertEqual(dashboard["resumen"][1]["valor"], 11)
        self.assertEqual(dashboard["resumen"][2]["valor"], 5)
        self.assertEqual(dashboard["resumen"][3]["valor"], 2)
        self.assertEqual(dashboard["proximas_citas"], [{"id_cita": 99}])
        self.assertIn("No Asistio para Demo Patient", dashboard["actividad_reciente"][0])
        self.assertIn("1 médico(s) activo(s) sin horario", dashboard["alertas_admin"][0])

    def test_medico_dashboard_uses_model_data_for_current_doctor(self):
        from app import create_app
        from app.controllers import home_controller

        app = create_app()
        app.config.update(TESTING=True)
        medico_model = MagicMock()
        cita_model = MagicMock()
        paciente_model = MagicMock()
        medico_model.obtener_id_medico_por_usuario.return_value = 42
        cita_model.listar_por_medico.return_value = [
            {"id_cita": 1, "estado": "PENDIENTE", "fecha": "2026-06-25", "hora": "09:00"},
            {"id_cita": 2, "estado": "CONFIRMADA", "fecha": "2026-06-25", "hora": "10:00"},
            {"id_cita": 3, "estado": "ATENDIDA", "fecha": "2026-06-24", "hora": "08:00"},
        ]
        paciente_model.listar_por_medico.return_value = [{"id_paciente": 10}, {"id_paciente": 20}]

        with app.test_request_context("/"):
            with patch.object(home_controller, "medico_model", medico_model), patch.object(
                home_controller, "cita_model", cita_model
            ), patch.object(home_controller, "paciente_model", paciente_model):
                dashboard = home_controller._crear_dashboard_medico({"id_usuario": 9, "rol": "MEDICO"})

        medico_model.obtener_id_medico_por_usuario.assert_called_once_with(9)
        cita_model.listar_por_medico.assert_called_once_with(42)
        paciente_model.listar_por_medico.assert_called_once_with(42)
        self.assertEqual(dashboard["resumen"][0]["valor"], 2)
        self.assertEqual(dashboard["resumen"][1]["valor"], 2)
        self.assertEqual(dashboard["resumen"][2]["valor"], 1)
        self.assertEqual([cita["id_cita"] for cita in dashboard["proximas_citas"]], [1, 2])


class CitaAuditEventTests(unittest.TestCase):
    def test_marcar_atendida_inserts_audit_event(self):
        self._assert_estado_final_inserts_audit_event("marcar_atendida", "ATENDIDA", 77)

    def test_marcar_no_asistio_inserts_audit_event(self):
        self._assert_estado_final_inserts_audit_event("marcar_no_asistio", "NO_ASISTIO", 88)

    def _assert_estado_final_inserts_audit_event(self, method_name, expected_event, actor_id):
        from app.models import cita_model

        cursor = MagicMock()
        cursor.rowcount = 1
        context = MagicMock()
        context.__enter__.return_value = cursor

        with patch.object(cita_model, "transaction", return_value=context):
            getattr(cita_model.CitaModel(), method_name)(123, actor_id)

        self.assertEqual(cursor.execute.call_count, 2)
        update_params = cursor.execute.call_args_list[0].args[1]
        insert_params = cursor.execute.call_args_list[1].args[1]
        self.assertEqual(update_params, (expected_event, 123))
        self.assertEqual(insert_params[0], 123)
        self.assertEqual(insert_params[1], actor_id)
        self.assertEqual(insert_params[3], expected_event)


class CitaSeguimientoControllerTests(unittest.TestCase):
    def test_medico_without_matching_cita_does_not_create_follow_up(self):
        from app import create_app
        from app.controllers import cita_controller

        app = create_app()
        app.config.update(TESTING=True)
        cita_model = MagicMock()
        cita_model.obtener_por_id_y_medico.return_value = None
        medico_model = MagicMock()
        medico_model.obtener_id_medico_por_usuario.return_value = 42

        with app.test_client() as client:
            with client.session_transaction() as session:
                session["id_usuario"] = 9
                session["rol"] = "MEDICO"

            with patch.object(cita_controller, "cita_model", cita_model), patch.object(
                cita_controller, "medico_model", medico_model
            ):
                response = client.post(
                    "/citas/123/seguimiento",
                    data={"fecha": "2026-06-30", "hora": "09:00", "motivo_consulta": "Control"},
                )

        self.assertEqual(response.status_code, 404)
        medico_model.obtener_id_medico_por_usuario.assert_called_once_with(9)
        cita_model.obtener_por_id_y_medico.assert_called_once_with(123, 42)
        cita_model.crear_seguimiento.assert_not_called()


class HistorialObservationTests(unittest.TestCase):
    def test_actualizar_observacion_updates_existing_historial_without_insert(self):
        from app.models import historial_cita_model

        cursor = MagicMock()
        cursor.rowcount = 1
        context = MagicMock()
        context.__enter__.return_value = cursor

        with patch.object(historial_cita_model, "transaction", return_value=context):
            historial_cita_model.HistorialCitaModel().actualizar_observacion(55, "Nueva observación")

        cursor.execute.assert_called_once()
        statement = cursor.execute.call_args.args[0]
        params = cursor.execute.call_args.args[1]
        self.assertIn("UPDATE historial_cita", statement)
        self.assertNotIn("INSERT INTO historial_cita", statement)
        self.assertEqual(params, ("Nueva observación", "Nueva observación", 55))


class SidebarTemplateTests(unittest.TestCase):
    def test_sidebar_citas_link_targets_citas_index(self):
        template = Path("app/views/partials/sidebar.html").read_text(encoding="utf-8")

        self.assertIn("url_for('citas.index')", template)
        self.assertNotIn("url_for('citas.programar')", template)


if __name__ == "__main__":
    unittest.main()
