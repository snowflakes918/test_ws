#!/usr/bin/env python

from turtle import home
import rospy
import tf2_ros
import numpy
import geometry_msgs
import pickle
import sys
import rospy
import moveit_commander
import moveit_msgs.msg
import tf_conversions

from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
from math import pi, tau, dist, fabs, cos
from pyrobotiq import PyRobotiqGripper

import tf.transformations as transformations
import mytools


# global variables

moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('pickup_node_python',anonymous=True)
gripper = PyRobotiqGripper()

## Instantiate a `RobotCommander`_ object.
robot = moveit_commander.RobotCommander()

## Instantiate a `PlanningSceneInterface`_ object.
scene = moveit_commander.PlanningSceneInterface()

## Instantiate a `MoveGroupCommander`_ object.
group_name = "panda_arm"
group = moveit_commander.MoveGroupCommander(group_name)
group.set_max_velocity_scaling_factor(0.1)
group.set_max_acceleration_scaling_factor(0.1)

# Create a DisplayTrajectory ROS publisher which is used to display trajectories in Rviz
display_trajectory_publisher = rospy.Publisher(
    "/move_group/display_planned_path",
    moveit_msgs.msg.DisplayTrajectory,
    queue_size=20,
)

# Initiate tf2 
tfBuffer = tf2_ros.Buffer()
listener = tf2_ros.TransformListener(tfBuffer)

rate = rospy.Rate(10.0)




def plan_and_execute(panda_pose):
    group.set_pose_target(panda_pose)

    waypoints = []
    waypoints.append(panda_pose)

    plan_successful = False
    (trajecotry, fraction) = group.compute_cartesian_path(waypoints, 0.005, 0.0)
    print("=-=-=-=-=-=-=fraction=-=-=-=-=-=-==-=-")
    print(fraction)

    if fraction > 0.7:
        plan_successful = True

    # Display trajectory
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(trajecotry)
    # Publish
    display_trajectory_publisher.publish(display_trajectory)

    # execute the plan
    if plan_successful:
        # group.execute(trajecotry, wait=True)
        print("-=-=--==-=-=-SUCCESS-=-=-=-=-=-=-=-")
    else:
        print("-=-=-=-=-=-=-=-FAIL-=-=-=-=-=--=-=--")

    # # Calling `stop()` ensures that there is no residual movement
    group.stop()
    group.clear_pose_targets()



def goto_home():
    # load the tf between tag to end effector
    home_pose = pickle.load(open("./src/siwei_pkg/pickle/home_tf.pickle", "rb"))


    # set up pose goal
    panda_pose = geometry_msgs.msg.Pose()
    panda_pose.orientation.w = home_pose.transform.rotation.w
    panda_pose.orientation.x = home_pose.transform.rotation.x
    panda_pose.orientation.y = home_pose.transform.rotation.y
    panda_pose.orientation.z = home_pose.transform.rotation.z

    panda_pose.position.x = home_pose.transform.translation.x
    panda_pose.position.y = home_pose.transform.translation.y
    panda_pose.position.z = home_pose.transform.translation.z

    plan_and_execute(panda_pose)


def calcuate_vial_frame():
    # load the tf between tag to end effector
    tag_EE_M = pickle.load(open("saved_tf.pickle", "rb"))

    # calculate robot pose from tag pose
    world_tag = tfBuffer.lookup_transform('world', 'tag_1', rospy.Time(), rospy.Duration(1.0))
    world_tag_M = mytools.convert_to_matirx(world_tag)
    world_EE_M = numpy.matmul(world_tag_M, tag_EE_M)
    world_EE_tf = mytools.convert_to_transform(world_EE_M)

    return world_EE_tf

def goto_vial(vial_frame):
    robot_pose = group.get_current_pose()

    # set up pose goal
    panda_pose = geometry_msgs.msg.Pose()
    panda_pose.orientation.w = vial_frame.transform.rotation.w
    panda_pose.orientation.x = vial_frame.transform.rotation.x
    panda_pose.orientation.y = vial_frame.transform.rotation.y
    panda_pose.orientation.z = vial_frame.transform.rotation.z

    panda_pose.position.x = vial_frame.transform.translation.x
    panda_pose.position.y = vial_frame.transform.translation.y
    panda_pose.position.z = vial_frame.transform.translation.z

    plan_and_execute(panda_pose)


def open_gripper():
    gripper.open()

def go_down():
    robot_pose = group.get_current_pose()

    # set up pose goal
    panda_pose = geometry_msgs.msg.Pose()
    panda_pose.position.z = robot_pose.transform.translation.z - 0.15 # go down 15 cm

    plan_and_execute(panda_pose)

def close_gripper():
    gripper.fully_close()


def go_up():
    robot_pose = group.get_current_pose()

    # set up pose goal
    panda_pose = geometry_msgs.msg.Pose()
    panda_pose.position.z = robot_pose.transform.translation.z + 0.15 # go up 15 cm

    plan_and_execute(panda_pose)


if __name__ == '__main__':
    # put the vial back
    put_back_frame = calcuate_vial_frame()
    goto_vial(put_back_frame)
    go_down()
    open_gripper()
    rospy.sleep(5.)
    go_up()
    close_gripper()
    goto_home()