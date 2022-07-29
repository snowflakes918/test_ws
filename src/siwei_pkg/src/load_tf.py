#!/usr/bin/env python

from mmap import PROT_READ
import os
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


# initialization

moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('move_group_python',anonymous=True)
gripper = PyRobotiqGripper()

## Instantiate a `RobotCommander`_ object. This object is the outer-level interface to
## the robot:
robot = moveit_commander.RobotCommander()

## Instantiate a `PlanningSceneInterface`_ object.  This object is an interface
## to the world surrounding the robot:
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

## BEGIN_SUB_TUTORIAL basic_info
##
## Getting Basic Information
## ^^^^^^^^^^^^^^^^^^^^^^^^^
# We can get the name of the reference frame for this robot:
planning_frame = group.get_planning_frame()
print("============ Reference frame: %s" % planning_frame)

# We can also print the name of the end-effector link for this group:
eef_link = group.get_end_effector_link()
print("============ End effector: %s" % eef_link)

# We can get a list of all the groups in the robot:
group_names = robot.get_group_names()
print("============ Robot Groups:", robot.get_group_names())

# Sometimes for debugging it is useful to print the entire state of the
# robot:
print("============ Printing robot state")
print(robot.get_current_state())
print("")

print("============ Printing robot pose")
start_pose = group.get_current_pose()
print(start_pose)
print("")

tfBuffer = tf2_ros.Buffer()
listener = tf2_ros.TransformListener(tfBuffer)

rate = rospy.Rate(10.0)


# transform method
def convert_to_transform(matrix):
    br = tf2_ros.TransformBroadcaster()

    t = geometry_msgs.msg.TransformStamped()

    t.header.stamp = rospy.Time.now()
    t.header.frame_id = "world"
    t.child_frame_id = "panda_EE"
    t.transform.translation.x = matrix[0,3]
    t.transform.translation.y = matrix[1,3]
    t.transform.translation.z = matrix[2,3]
    q = transformations.quaternion_from_matrix(matrix)
    t.transform.rotation.x = q[0]
    t.transform.rotation.y = q[1]
    t.transform.rotation.z = q[2]
    t.transform.rotation.w = q[3]

    return t


def convert_to_matirx(lookup_tf):
    #Get translation and rotation (from Euler angles)
    pose = transformations.quaternion_matrix(numpy.array([lookup_tf.transform.rotation.x, lookup_tf.transform.rotation.y, lookup_tf.transform.rotation.z, lookup_tf.transform.rotation.w]))

    pose[0,3] = lookup_tf.transform.translation.x
    pose[1,3] = lookup_tf.transform.translation.y
    pose[2,3] = lookup_tf.transform.translation.z

    return pose 


def is_equal(panda_pose, robot_pose):

    if not panda_pose.orientation.w == robot_pose.pose.orientation.w:
        return False

    if not panda_pose.orientation.x == robot_pose.pose.orientation.x:
        return False

    if not panda_pose.orientation.y == robot_pose.pose.orientation.y:
        return False

    if not panda_pose.orientation.z == robot_pose.pose.orientation.z:
        return False

    if not panda_pose.position.x == robot_pose.pose.position.x:
        return False

    if not panda_pose.position.y == robot_pose.pose.position.y:
        return False

    if not panda_pose.position.z == robot_pose.pose.position.z:
        return False

    return True



# load pickle from disk
tag_EE_M = pickle.load(open("save.pickle", "rb"))

print("-=-=--=-=-=-=--=-=-=-=-=-=-tag_EE_M-=-==-=-=-=-=-=-=-=-=-")
print(tag_EE_M)

while not rospy.is_shutdown():

    # parent: world; child: tag_0
    try:
        world_tag = tfBuffer.lookup_transform('world', 'tag_0', rospy.Time())
        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=world to tag_0=-=-=-=-=-=-=-=-=-=-==-=-=")
        print(world_tag)
        print()
        world_tag_M = convert_to_matirx(world_tag)
        print("converted matrix")
        print(world_tag_M)
        print()
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
        rate.sleep()
        continue


    world_EE_M = numpy.matmul(world_tag_M, tag_EE_M)  
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-world_EE_M=-=-=-=--=-=-=-=-=-=-=-=-=-=-")
    print(world_EE_M)
    print()


    world_EE_tf = convert_to_transform(world_EE_M)

    flat_ori = group.get_current_pose()
    print("-==-=-=-=-=-=-robot pose-==-=-=-=-=-=-=-=-")
    print(flat_ori)
    print()

    # set up pose goal
    panda_pose = geometry_msgs.msg.Pose()
    panda_pose.orientation.w = world_EE_tf.transform.rotation.w
    panda_pose.orientation.x = world_EE_tf.transform.rotation.x
    panda_pose.orientation.y = world_EE_tf.transform.rotation.y
    panda_pose.orientation.z = world_EE_tf.transform.rotation.z

    # panda_pose.orientation.w = flat_ori.pose.orientation.w
    # panda_pose.orientation.x = flat_ori.pose.orientation.x
    # panda_pose.orientation.y = flat_ori.pose.orientation.y
    # panda_pose.orientation.z = flat_ori.pose.orientation.z

    panda_pose.position.x = world_EE_tf.transform.translation.x
    panda_pose.position.y = world_EE_tf.transform.translation.y
    panda_pose.position.z = world_EE_tf.transform.translation.z

    print("-=-==-=-=-=-=-=-=-=-=-Panda pose-=-=-=-=-=-=-=-=-=-=-")
    print(panda_pose)
    print()

    if is_equal(panda_pose, flat_ori):
        print("=-=-=--==-=--=-=--=-=- I break !!!! =-=--=-=-=-=-=-=-=-=-")
        break;


    # # debug
    # panda_pose.position.x = 0.4
    # panda_pose.position.y = 0.0
    # panda_pose.position.z = 0.4

    group.set_pose_target(panda_pose)

    waypoints = []

    waypoints.append(panda_pose)

    plan_successful = False
    (trajecotry, fraction) = group.compute_cartesian_path(waypoints, 0.005, 0.0)
    print("=-=-=-=-=-=-=fraction=-=-=-=-=-=-==-=-")
    print(fraction)

    if fraction > 0.7:
        plan_successful = True

    #(plan_successful, trajecotry, planning_time, error_code) = group.plan()
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(trajecotry)
    # Publish
    display_trajectory_publisher.publish(display_trajectory)


    if plan_successful:
        # group.execute(trajecotry, wait=True)
        print("-=-=--==-=-=-success-=-=-=-=-=-=-=-")
    else:
        print("-=-=-=-=-=-=-=-fail-=-=-=-=-=--=-=--")

    # # Calling `stop()` ensures that there is no residual movement
    group.stop()
    # # It is always good to clear your targets after planning with poses.
    # # Note: there is no equivalent function for clear_joint_value_targets()
    group.clear_pose_targets()

    rospy.sleep(5.)

    rate.sleep()


target_pose_E = pickle.load(open("target.pickle", "rb"))
target_pose = convert_to_transform(target_pose_E)


group.set_pose_target(panda_pose)

waypoints = []

waypoints.append(panda_pose)

plan_successful = False
(trajecotry, fraction) = group.compute_cartesian_path(waypoints, 0.005, 0.0)
print("=-=-=-=-=-=-=fraction=-=-=-=-=-=-==-=-")
print(fraction)

if fraction > 0.7:
    plan_successful = True

#(plan_successful, trajecotry, planning_time, error_code) = group.plan()
display_trajectory = moveit_msgs.msg.DisplayTrajectory()
display_trajectory.trajectory_start = robot.get_current_state()
display_trajectory.trajectory.append(trajecotry)
# Publish
display_trajectory_publisher.publish(display_trajectory)
