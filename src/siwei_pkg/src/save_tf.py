#!/usr/bin/env python

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

import tf.transformations as transformations


# initialization

moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('move_group_python',anonymous=True)

## Instantiate a `RobotCommander`_ object. This object is the outer-level interface to
## the robot:
robot = moveit_commander.RobotCommander()

## Instantiate a `PlanningSceneInterface`_ object.  This object is an interface
## to the world surrounding the robot:
scene = moveit_commander.PlanningSceneInterface()

## Instantiate a `MoveGroupCommander`_ object.

group_name = "panda_arm"
group = moveit_commander.MoveGroupCommander(group_name)

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


def convert_to_matirx(lookup_tf):
    #Get translation and rotation (from Euler angles)
    pose = transformations.quaternion_matrix(numpy.array([lookup_tf.transform.rotation.x, lookup_tf.transform.rotation.y, lookup_tf.transform.rotation.z, lookup_tf.transform.rotation.w]))

    pose[0,3] = lookup_tf.transform.translation.x
    pose[1,3] = lookup_tf.transform.translation.y
    pose[2,3] = lookup_tf.transform.translation.z

    return pose 


# transformation code

tfBuffer = tf2_ros.Buffer()
listener = tf2_ros.TransformListener(tfBuffer)

rate = rospy.Rate(10.0)

parent_frame = 'world'
child_frame = 'tag_1'


tf_to_save = tfBuffer.lookup_transform(parent_frame, child_frame, rospy.Time(), rospy.Duration(2.))
print("-==-=-=-=-=-=-=-=-=-=-= M_to_save =-=-=-=-=-=-=-=-=-=-=-=-")
print(tf_to_save)
print()
M_to_save = convert_to_matirx(tf_to_save)
print("converted matrix")
print(M_to_save)
print()



# pickle the matrix 
pickle.dump(M_to_save, open("./src/siwei_pkg/pickle/vial_tf.pickle", "wb")) 
