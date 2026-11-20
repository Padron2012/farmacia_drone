# 🚁 Farmacia Drone

Simulación de un dron Iris utilizando **ROS 2 Humble** y **Gazebo Sim**.

## Requisitos

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Sim
- Paquete `ros_gz_bridge`

## 1. Ejecutar la simulación

Abre una terminal y ejecuta:

```bash
cd ~/Farmacia/src/farmacia_drone

colcon build
source install/setup.bash

ros2 launch farmacia_drone farmacia_drone.launch.py
o
./correr.sh 
```

Espera a que Gazebo termine de cargar el mundo y aparezca el dron Iris.

**Mantén esta terminal abierta.**

## 2. Iniciar el bridge ROS 2 ↔ Gazebo

Abre una segunda terminal.

Ejecuta:

```bash
source /opt/ros/humble/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/iris/gazebo/command/twist@geometry_msgs/msg/Twist]ignition.msgs.Twist \
/iris/enable@std_msgs/msg/Bool]ignition.msgs.Boolean
```

Este bridge permite enviar comandos de velocidad desde ROS 2 hacia Gazebo.

Deberías observar mensajes similares a:

```text
Creating ROS->GZ Bridge:
[/iris/gazebo/command/twist ...]

Creating ROS->GZ Bridge:
[/iris/enable ...]
```

**Mantén esta terminal abierta mientras utilizas el dron.**

## 3. Habilitar el controlador del Iris

Abre una tercera terminal.

Primero, carga ROS 2:

```bash
source /opt/ros/humble/setup.bash
```

Después, habilita el controlador:

```bash
ros2 topic pub --once /iris/enable std_msgs/msg/Bool "{data: true}"
```

Este comando habilita el controlador de velocidad del dron.

## 4. Controlar el movimiento del Iris

Utiliza el tópico:

```text
/iris/gazebo/command/twist
```

Tipo de mensaje:

```text
geometry_msgs/msg/Twist
```

### Movimiento hacia adelante

```bash
ros2 topic pub /iris/gazebo/command/twist geometry_msgs/msg/Twist \
"{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

### Movimiento lateral

```bash
ros2 topic pub /iris/gazebo/command/twist geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: 0.5, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

### Movimiento vertical

```bash
ros2 topic pub /iris/gazebo/command/twist geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: 0.0, z: 0.5}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

### Rotación sobre el eje Z

```bash
ros2 topic pub /iris/gazebo/command/twist geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}"
```

### Detener el movimiento

Para enviar una velocidad deseada de cero:

```bash
ros2 topic pub --once /iris/gazebo/command/twist geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

Para detener la publicación continua de comandos, utiliza `Ctrl + C`.

## 5. Referencia de los parámetros Twist

| Parámetro   | Función                     |
| ----------- | --------------------------- |
| `linear.x`  | Movimiento adelante / atrás |
| `linear.y`  | Movimiento lateral          |
| `linear.z`  | Movimiento vertical         |
| `angular.x` | Rotación sobre X            |
| `angular.y` | Rotación sobre Y            |
| `angular.z` | Rotación sobre Z            |

Los valores representan velocidades deseadas. Las direcciones dependen de la orientación del dron y de la configuración del controlador.

## 6. Verificar los tópicos

Listar los tópicos disponibles:

```bash
ros2 topic list
```

Consultar información del tópico de velocidad:

```bash
ros2 topic info /iris/gazebo/command/twist
```

Consultar la odometría del dron:

```bash
gz topic -e -t /model/iris/odometry
```

## Resumen de terminales

| Terminal | Función                   | Comando                                               |
| -------- | ------------------------- | ----------------------------------------------------- |
| 1        | Iniciar simulación        | `ros2 launch farmacia_drone farmacia_drone.launch.py` |
| 2        | Conectar ROS 2 con Gazebo | `ros2 run ros_gz_bridge parameter_bridge ...`         |
| 3        | Habilitar controlador     | `ros2 topic pub --once /iris/enable ...`              |
| 3        | Enviar movimientos        | `ros2 topic pub /iris/gazebo/command/twist ...`       |

**Importante:** las tres terminales deben permanecer abiertas mientras se utiliza la simulación. Comienza con velocidades pequeñas para evitar movimientos bruscos.
