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


import tf2_ros
import numpy
import geometry_msgs

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


def convert_to_matirx(lookup_tf):
    #Get translation and rotation (from Euler angles)
    pose = transformations.quaternion_matrix(numpy.array([lookup_tf.transform.rotation.x, lookup_tf.transform.rotation.y, lookup_tf.transform.rotation.z, lookup_tf.transform.rotation.w]))

    pose[0,3] = lookup_tf.transform.translation.x
    pose[1,3] = lookup_tf.transform.translation.y
    pose[2,3] = lookup_tf.transform.translation.z

    return pose 


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


# transformation code

tfBuffer = tf2_ros.Buffer()
listener = tf2_ros.TransformListener(tfBuffer)

rate = rospy.Rate(10.0)


flag1 = True
# extract tf of tag and end effector
while flag1:
    print("=-=-=-=-=-=-=-=-=-=-=-Looping for lookup=-=-=-=-=-=-=-=-=-=-=-=-")
    try:
        tag_EE = tfBuffer.lookup_transform('tag_0', 'panda_EE', rospy.Time())
        print("-==-=-=-=-=-=-=-=-=-=-=world to panda_link8=-=-=-=-=-=-=-=-=-=-=-=-")
        print(tag_EE)
        print()
        tag_EE_M = convert_to_matirx(tag_EE)
        print("converted matrix")
        print(tag_EE_M)
        print()
        flag1 = False
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
        rate.sleep()
        


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

    try:
        world_EE_tf = convert_to_transform(world_EE_M)
        print("=-=-=-=--=-=-=-=--=-world_EE_tf-=-=-=-=-=-=-=-=-=-=-=-=")
        print(world_EE_tf)
        print()
    except:
        print("!!!!!!!!!!!!!!!!!!! Converting error during convert to transform !!!!!!!!!!!!!!!!!!!!!!!!!")


    flat_ori = group.get_current_pose()
    print("-==-=-=-=-=-=-robot pose-==-=-=-=-=-=-=-=-")
    print(flat_ori)
    print()



    panda_pose = geometry_msgs.msg.Pose()
    panda_pose.orientation.w = world_EE_tf.transform.rotation.w
    panda_pose.orientation.x = world_EE_tf.transform.rotation.x
    panda_pose.orientation.y = world_EE_tf.transform.rotation.y
    panda_pose.orientation.z = world_EE_tf.transform.rotation.z

    panda_pose.position.x = world_EE_tf.transform.translation.x
    panda_pose.position.y = world_EE_tf.transform.translation.y
    panda_pose.position.z = world_EE_tf.transform.translation.z

    print("-=-==-=-=-=-=-=-=-=-=-Panda pose-=-=-=-=-=-=-=-=-=-=-")
    print(panda_pose)
    print()

    # # debug
    # panda_pose.position.x = 0.4
    # panda_pose.position.y = 0.0
    # panda_pose.position.z = 0.4

    group.set_pose_target(panda_pose)

    (plan_successful, trajecotry, planning_time, error_code) = group.plan()
    if plan_successful:
        plan = group.go(wait=True)
        print("-=-=--==-=-=-success-=-=-=-=-=-=-=-")
    else:
        print("-=-=-=-=-=-=-=-fail-=-=-=-=-=--=-=--")

    # # Calling `stop()` ensures that there is no residual movement
    group.stop()
    # # It is always good to clear your targets after planning with poses.
    # # Note: there is no equivalent function for clear_joint_value_targets()
    group.clear_pose_targets()

    rospy.sleep(1.)

    rate.sleep()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
