import vgamepad as vg
from inputs import get_gamepad, UnpluggedError
import time
import XInput

# telemetria
from telemetria import registrar_drift

# escritura = False
recolectar_telemetria = False

block = True

target_control = vg.VX360Gamepad()

# --- LÓGICA DE VIBRACIÓN ---


def callback_vibracion(client, target, large_motor, small_motor, led_number, user_data):
    # XInput-Python usa valores de 0.0 a 1.0
    fuerza_L = large_motor / 255.0
    fuerza_S = small_motor / 255.0
    # Probamos enviar a todos los mandos conectados (0 al 3)
    # por si el ID de tu mando físico cambió al conectar el virtual
    XInput.set_vibration(0, fuerza_L, fuerza_S)


# Registramos la vibración en el mando virtual
target_control.register_notification(callback_function=callback_vibracion)

estado = {
    'LX': 0.0, 'LY': 0.0,
    'RX': 0.0, 'RY': 0.0,
    'LT': 0, 'RT': 0,
    'A_PULSADO': False,
    'R3_PRESIONADO': False
}

ultimo_valor_ry = 0.0
ultimo_tiempo = time.time()
umbral_velocidad = 0.1546

LIMITE_X_MIN = -0.060
LIMITE_X_MAX = 0.074

botones_map = {
    'BTN_SOUTH': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    'BTN_EAST': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    'BTN_WEST': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    'BTN_NORTH': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    'BTN_TL': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    'BTN_TR': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    'BTN_THUMBL': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    'BTN_THUMBR': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    'BTN_SELECT': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    'BTN_START': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
}


def procesar_control():
    global ultimo_valor_ry, ultimo_tiempo

    while True:
        # !IMPORTANTE: Esta llamada refresca el estado del driver, lo que permite
        # que get_gamepad() lance UnpluggedError si el mando se desconectó.
        # Sin esta línea, get_gamepad() se bloquea indefinidamente.
        # XInput.get_connected()[0]

        try:
            events = get_gamepad()
        except UnpluggedError:
            # Si esto falla, es que el hardware ya no responde
            print("\n[!] Error crítico: Mando físico desconectado.")
            break

        for event in events:
            ahora = time.time()
            dt = ahora - ultimo_tiempo

            # Lógica de Botones
            if event.code in botones_map:
                if event.code == 'BTN_THUMBR':
                    estado['R3_PRESIONADO'] = (event.state == 1)

                if event.code == 'BTN_SOUTH':
                    estado['A_PULSADO'] = (event.state == 1)

                if event.state == 1:
                    target_control.press_button(botones_map[event.code])
                else:
                    target_control.release_button(botones_map[event.code])

            # CRUCETA (D-PAD) - Nueva lógica
            elif event.code == 'ABS_HAT0X':
                # Izquierda / Derecha
                if event.state == -1:
                    target_control.press_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                    target_control.release_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                elif event.state == 1:
                    target_control.press_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                    target_control.release_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                else:
                    target_control.release_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                    target_control.release_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)

            elif event.code == 'ABS_HAT0Y':
                # Arriba / Abajo (Ojo: -1 suele ser Arriba en inputs)
                if event.state == -1:
                    target_control.press_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                    target_control.release_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                elif event.state == 1:
                    target_control.press_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                    target_control.release_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                else:
                    target_control.release_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                    target_control.release_button(
                        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)

            elif event.code == 'ABS_X':
                estado['LX'] = event.state / 32768.0
                target_control.left_joystick_float(
                    x_value_float=estado['LX'], y_value_float=estado['LY'])

            elif event.code == 'ABS_Y':
                estado['LY'] = event.state / 32768.0
                target_control.left_joystick_float(
                    x_value_float=estado['LX'], y_value_float=estado['LY'])

            elif event.code == 'ABS_RX':
                estado['RX'] = event.state / 32768.0
                target_control.right_joystick_float(
                    x_value_float=estado['RX'], y_value_float=estado['RY'])

            elif event.code == 'ABS_RY':
                valor_fisico = event.state / 32768.0
                valor_final = valor_fisico

                if block:
                    if valor_fisico > 0:
                        # Si está dentro del rango X establecido
                        if LIMITE_X_MIN <= estado['RX'] <= LIMITE_X_MAX:
                            # SOLO permite moverse si el R3 (Joystick) está espichado/presionado
                            if not estado['R3_PRESIONADO']:
                                valor_final = 0.0  # Bloqueado
                else:
                    if dt > 0:
                        cambio = valor_fisico - ultimo_valor_ry
                        velocidad = cambio / dt

                        if estado['A_PULSADO'] and recolectar_telemetria:
                            registrar_drift(estado, valor_fisico,
                                            velocidad, cambio, dt)

                        # NUEVA LÓGICA DE CORRECCIÓN:
                        # 1. valor_fisico > 0 (La palanca está en la mitad SUPERIOR)
                        # 2. velocidad <= umbral_velocidad (El movimiento es lento)
                        # 3. Condición de X (X está centrado)

                        if valor_fisico > 0 and cambio > 0 and abs(velocidad) <= umbral_velocidad:
                            if LIMITE_X_MIN <= estado['RX'] <= LIMITE_X_MAX:
                                valor_final = 0.0
                                # if escritura:
                                #     print(
                                #         f"Corrigiendo zona INFERIOR (Positiva): {valor_fisico:.4f}")

                estado['RY'] = valor_final
                target_control.right_joystick_float(
                    x_value_float=estado['RX'], y_value_float=estado['RY'])

                ultimo_valor_ry = valor_fisico
                ultimo_tiempo = ahora

            elif event.code == 'ABS_Z':
                target_control.left_trigger(value=event.state)
            elif event.code == 'ABS_RZ':
                target_control.right_trigger(value=event.state)

            target_control.update()


if __name__ == "__main__":
    try:
        procesar_control()
    except KeyboardInterrupt:
        print('Fin del programa')
    finally:
        XInput.set_vibration(0, 0, 0)
        target_control.reset()
        target_control.update()
