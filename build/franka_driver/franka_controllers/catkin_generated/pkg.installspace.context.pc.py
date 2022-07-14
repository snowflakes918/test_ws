# generated from catkin/cmake/template/pkg.context.pc.in
CATKIN_PACKAGE_PREFIX = ""
PROJECT_PKG_CONFIG_INCLUDE_DIRS = "${prefix}/include;/home/difadmin/libfranka-0.8.0/include".split(';') if "${prefix}/include;/home/difadmin/libfranka-0.8.0/include" != "" else []
PROJECT_CATKIN_DEPENDS = "controller_interface;dynamic_reconfigure;eigen_conversions;franka_hw;geometry_msgs;hardware_interface;tf;tf_conversions;message_runtime;moveit_msgs;moveit_core;moveit_visual_tools;moveit_ros_planning_interface;pluginlib;realtime_tools;roscpp".replace(';', ' ')
PKG_CONFIG_LIBRARIES_WITH_PREFIX = "-lfranka_controllers;/home/difadmin/libfranka-0.8.0/build/libfranka.so.0.8.0".split(';') if "-lfranka_controllers;/home/difadmin/libfranka-0.8.0/build/libfranka.so.0.8.0" != "" else []
PROJECT_NAME = "franka_controllers"
PROJECT_SPACE_DIR = "/home/difadmin/test_ws/install"
PROJECT_VERSION = "0.7.0"
