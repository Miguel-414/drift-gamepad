# Corrector de Drift - Gamepad Xbox

## Descripción

Proyecto de software para corregir el **drift** de un control Xbox mediante análisis de velocidad de movimiento. Desarrollado como solución alternativa a la reparación física cuando la limpieza no fue suficiente.

Alcance: Esta solución está personalizada para el drift específico de mi control (joystick derecho, eje Y). No es un corrector universal aplicable a todos los gamepads.

## Problema Parcialmente Solucionado

El drift del joystick se caracterizaba por:

- Movimientos mayormente lentos e involuntarios en la zona superior del eje Y
- Patrón repetitivo en un rango específico del eje X
- Detectable mediante la **velocidad de cambio del movimiento**

## Requisitos

### Librerías Python

- `vgamepad` - Emulación de gamepad virtual
- `inputs` - Lectura de eventos del gamepad físico
- `XInput` - Control de vibración

### Software Adicional

- [HidHide](https://github.com/nefarius/HidHide) - Para ocultar el control físico de Windows y mostrar solo el virtual

## Telemetría

Con el fin de pulir los valores añadi la opcion de guardar telemetria para poder analizar el comportamiento del drift

El sistema registra automáticamente datos técnicos en `test/log_telemetria_drift.csv` cuando se presiona el botón A, incluyendo:

- Valor físico del joystick
- Velocidad de cambio
- Diferencia de tiempo entre frames
