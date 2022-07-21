#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of the Willow Garage nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import rospy

import math
import tf2_ros
import geometry_msgs.msg
import turtlesim.srv

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
import tf_conversions

from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
from math import pi, tau, dist, fabs, cos


# initialization

moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('move_group_python',anonymous=True)

## Instantiate a `RobotCommander`_ object. This object is the outer-level interface to
## the robot:
robot = moveit_commander.RobotCommander()

## Instantiate a `PlanningSceneInterface`_ object.  This object is an interface
## to the world surrounding the robot:
scene = moveit_commander.PlanningSceneInterface()

## Instantiate a `MoveGroupCommander`_ object.  This object is an interface
## to one group of joints.  In this case the group is the joints in the Panda
## arm so we set ``group_name = panda_arm``. If you are using a different robot,
## you should change this value to the name of your robot arm planning group.
## This interface can be used to plan and execute motions on the Panda:
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





# transformation code

tfBuffer = tf2_ros.Buffer()
listener = tf2_ros.TransformListener(tfBuffer)

rate = rospy.Rate(10.0)


flag1 = True
# extract tf of tag and end effector
while flag1:
    print("Looping for lookup")
    try:
        trans_tag_EE = tfBuffer.lookup_transform('panda_EE', 'tag_0', rospy.Time())
        flag1 = False
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
        rate.sleep()
        
print("=-=-=-=-=-=-=-=-=-=-=-trans_tag_EE-===-=-=-=-=-=-=-=-==-=-=-=-")
print(trans_tag_EE)

while not rospy.is_shutdown():

    try:
        pose_tag = tfBuffer.lookup_transform('tag_0', 'world', rospy.Time())
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
        rate.sleep()
        continue

    flat_ori = group.get_current_pose()
    panda_pose = flat_ori.pose
    panda_pose.orientation.w = pose_tag.transform.rotation.w - trans_tag_EE.transform.rotation.w
    panda_pose.orientation.x = pose_tag.transform.rotation.x - trans_tag_EE.transform.rotation.x
    panda_pose.orientation.y = pose_tag.transform.rotation.y - trans_tag_EE.transform.rotation.y
    panda_pose.orientation.z = pose_tag.transform.rotation.z - trans_tag_EE.transform.rotation.z

    panda_pose.position.x = pose_tag.transform.translation.x - trans_tag_EE.transform.translation.x
    panda_pose.position.y = pose_tag.transform.translation.y - trans_tag_EE.transform.translation.y
    panda_pose.position.z = pose_tag.transform.translation.z - trans_tag_EE.transform.translation.z


    # debug

    # panda_pose.position.x = 0.4
    # panda_pose.position.y = 0.0
    # panda_pose.position.z = 0.4

    group.set_pose_target(panda_pose)
    plan = group.go(wait=True)
    # Calling `stop()` ensures that there is no residual movement
    group.stop()
    # It is always good to clear your targets after planning with poses.
    # Note: there is no equivalent function for clear_joint_value_targets()
    group.clear_pose_targets()

    rate.sleep()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
