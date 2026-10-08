import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'my_bot'
    pkg_share = get_package_share_directory(package_name)

    # robot_state_publisher with our URDF, forced onto simulation time
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Which world to load; default is our Jetty empty world
    world = LaunchConfiguration('world')
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_share, 'worlds', 'empty.world'),
        description='World to load')

    # Gazebo: -r starts the physics at once, -v4 logs in detail;
    # on_exit_shutdown stops this whole launch when Gazebo closes
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r -v4 ', world],
                          'on_exit_shutdown': 'true'}.items()
    )

    # Spawn the URDF from /robot_description as model 'rover', base_link 0.1 m up
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'rover',
                   '-z', '0.1'],
        output='screen')

    return LaunchDescription([
        rsp,
        world_arg,
        gazebo,
        spawn_entity,
    ])
