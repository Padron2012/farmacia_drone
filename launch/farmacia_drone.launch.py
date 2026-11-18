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