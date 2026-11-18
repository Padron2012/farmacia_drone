# farmacia_drone

Mundo de simulación para **Ignition Gazebo Fortress + ROS2 Humble** (Ubuntu 22.04): una montaña, una casa sin techo, dos marcadores ArUco y un dron tipo Iris con cámara hacia abajo, IMU y viento.

## Contenido del mundo

| Elemento | Dónde está | Detalle |
|---|---|---|
| Montaña | origen (0, 0) | Malla 3D de 60×60 m, ~12 m de alto |
| Casa sin techo | (50, 0) | 6×6 m, paredes de 2.5 m, puerta de 1.2 m del lado de la montaña (-X) |
| ArUco 0 | (50, 0) | En el piso, **dentro** de la casa (se ve desde arriba) |
| ArUco 1 | (38, -8) | En el piso, entre la montaña y la casa |
| Dron (`iris`) | (42, 0), en el piso | 1.5 kg, 4 rotores, cámara abajo, IMU |
| Viento | todo el mundo | 3 m/s en +X, con variación y ruido |

Los ArUco son del diccionario `DICT_4X4_50`, ids **0** y **1**. La placa mide 0.8 m, pero incluye un borde blanco, así que el lado real del marcador es de ≈ **0.645 m** (úsalo en la estimación de pose).

## Estructura

```
farmacia_drone/
├── CMakeLists.txt
├── package.xml
├── correr.sh            # lanza solo Gazebo (sin ROS)
├── launch/
│   └── farmacia_drone.launch.py
├── world/
│   └── mundo.sdf        # (ajusta el nombre si el tuyo es distinto)
└── models/
    ├── mountain/        # model.sdf + mountain.obj
    ├── casa_sin_techo/
    ├── aruco_0/
    ├── aruco_1/
    └── iris/
```

## Cómo funciona

- **Mundo (`world/*.sdf`)**: lista los sistemas que corren (física, sensores, IMU, viento) y los modelos que se incluyen con `model://...`. Gazebo encuentra esos modelos gracias a la variable `IGN_GAZEBO_RESOURCE_PATH`, que apunta a la carpeta `models/`.
- **Dron (`models/iris`)**: el controlador `MulticopterVelocityControl` recibe una velocidad deseada (un `Twist`), calcula cuánto debe girar cada rotor y se lo manda a los 4 plugins `MulticopterMotorModel`, que convierten la velocidad de giro en empuje. Por eso el dron se maneja con **velocidades**, no con motores sueltos.
- **Marco de referencia**: las velocidades van en el marco del dron: `x` adelante, `y` izquierda, `z` arriba, y `angular.z` es el giro (yaw). Cada comando se queda aplicado hasta que mandas otro.
- **Límites**: aceleración máxima de 2 m/s² en cada eje.
- **Viento**: solo afecta a los links con `<enable_wind>true</enable_wind>` (el `base_link` del dron lo tiene). La fuerza es `0.2 × masa × (viento − velocidad del dron)`; sube el `force_approximation_scaling_factor` en el mundo para un viento más fuerte.
- **Sensores**: la cámara (`/camara_abajo`, 640×480, 30 Hz) y el IMU (`/imu`) son publicados por Gazebo; la odometría sale en `/model/iris/odometry`. El puente `ros_ign_bridge` los pasa a ROS2.

## Requisitos

```bash
sudo apt install ros-humble-ros-ign-bridge ros-humble-ros-ign-gazebo \
                 ros-humble-teleop-twist-keyboard
```

En `package.xml` agrega:

```xml
<exec_depend>ros_ign_bridge</exec_depend>
```

## Compilar con colcon

El `CMakeLists.txt` debe instalar las carpetas para que ROS las encuentre:

```cmake
cmake_minimum_required(VERSION 3.8)
project(farmacia_drone)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch world models
  DESTINATION share/${PROJECT_NAME})

ament_package()
```

Compila **desde la raíz del workspace** (`~/Farmacia`), no desde dentro del paquete:

```bash
cd ~/Farmacia
colcon build --symlink-install --packages-select farmacia_drone
source install/setup.bash
```

`--symlink-install` hace que los cambios que hagas a `world/` y `models/` se reflejen sin recompilar.

> Si ves carpetas `build/`, `install/` y `log/` dentro de `src/farmacia_drone/`, es porque se corrió `colcon build` desde ahí. Bórralas y compila desde `~/Farmacia`.

## Lanzar

### Opción A: con ROS2 (recomendada)

```bash
source ~/Farmacia/install/setup.bash
ros2 launch farmacia_drone farmacia_drone.launch.py
```

Abre Gazebo con el mundo y el puente a ROS2 al mismo tiempo.

### Opción B: solo Gazebo, sin ROS

```bash
cd ~/Farmacia/src/farmacia_drone
./correr.sh
```

## Volar el dron

El controlador **arranca apagado**: hay que activarlo primero.

### Desde ROS2 (con el puente corriendo)

```bash
# 1. Activar el controlador
ros2 topic pub --once /iris/enable std_msgs/msg/Bool "{data: true}"

# 2. Subir
ros2 topic pub --once /iris/gazebo/command/twist geometry_msgs/msg/Twist "{linear: {z: 1.0}}"

# 3. Avanzar
ros2 topic pub --once /iris/gazebo/command/twist geometry_msgs/msg/Twist "{linear: {x: 1.0}}"

# 4. Girar
ros2 topic pub --once /iris/gazebo/command/twist geometry_msgs/msg/Twist "{angular: {z: 0.5}}"

# 5. Hover (quedarse quieto en el aire)
ros2 topic pub --once /iris/gazebo/command/twist geometry_msgs/msg/Twist "{}"
```

Con el teclado:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=/iris/gazebo/command/twist
```

### Sin ROS (con `ign topic`)

```bash
ign topic -t /iris/enable -m ignition.msgs.Boolean -p "data: true"
ign topic -t /iris/gazebo/command/twist -m ignition.msgs.Twist -p "linear: {x:0 y:0 z:1.0}"
ign topic -t /iris/gazebo/command/twist -m ignition.msgs.Twist -p " "     # hover
```

## Sensores

| Dato | Topic en ROS2 | Tipo |
|---|---|---|
| Cámara hacia abajo | `/camara_abajo` | `sensor_msgs/msg/Image` |
| IMU | `/imu` | `sensor_msgs/msg/Imu` |
| Odometría | `/model/iris/odometry` | `nav_msgs/msg/Odometry` |

```bash
ros2 run rqt_image_view rqt_image_view          # ver la cámara
ros2 topic echo /model/iris/odometry            # posición y velocidad
ros2 topic echo /imu
```

Para detectar los ArUco, suscríbete a `/camara_abajo` con OpenCV (`cv2.aruco`, diccionario `DICT_4X4_50`). La cámara apunta hacia abajo, así que ve el piso cuando el dron vuela sobre los marcadores.

## Cambiar el viento en vivo

El nombre del mundo en el topic debe coincidir con el `<world name="...">` de tu `.sdf`:

```bash
ign topic -t "/world/mundo_montana/wind/" -m ignition.msgs.Wind \
  -p "linear_velocity: {x: 5, y: 0}, enable_wind: true"
```

## Archivo de launch

Guárdalo como `launch/farmacia_drone.launch.py`:

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('farmacia_drone')
    world = os.path.join(share, 'world', 'mundo.sdf')   # ajusta el nombre
    models = os.path.join(share, 'models')
    resource_path = models + ':' + os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')

    return LaunchDescription([
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', resource_path),

        ExecuteProcess(cmd=['ign', 'gazebo', '-r', world], output='screen'),

        Node(
            package='ros_ign_bridge',
            executable='parameter_bridge',
            output='screen',
            arguments=[
                # Gazebo -> ROS2  ([)
                '/camara_abajo@sensor_msgs/msg/Image[ignition.msgs.Image',
                '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU',
                '/model/iris/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
                # ROS2 -> Gazebo  (])
                '/iris/gazebo/command/twist@geometry_msgs/msg/Twist]ignition.msgs.Twist',
                '/iris/enable@std_msgs/msg/Bool]ignition.msgs.Boolean',
            ],
        ),
    ])
```

## Problemas comunes

| Error | Causa y solución |
|---|---|
| `Unable to find or download file` | Gazebo no encuentra el `.sdf`. Usa la ruta correcta al mundo (`world/...`). |
| `Unable to find file with URI [model://...]` | Falta `IGN_GAZEBO_RESOURCE_PATH`, o el nombre de la carpeta del modelo no coincide con el `model://` del mundo. |
| `A link named base_link has invalid inertia` | La inercia del `base_link` debe cumplir `ixx + iyy ≥ izz`. Con `izz = 0.07` es válida. |
| `Fragment Program ... failed to compile` (Ogre) | El shader del heightmap no compila en este equipo. La montaña ya va como **malla** (`.obj`) para evitarlo. |
| `libEGL warning: egl: failed to create dri2 screen` | Gazebo usa la gráfica integrada. Lanza con `__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json`. |
| El dron no responde a comandos | El controlador está apagado: manda `/iris/enable` con `data: true`. |
| Un topic de ROS2 no aparece | El puente no está corriendo, o el topic no está en su lista de argumentos. |

## Pendiente

- Reemplazar las formas simples del dron por los meshes reales (`iris.dae`, `propeller_*.dae`) de `iris_description`.
- Textura de pasto/roca para la montaña (hoy es de un solo color).
