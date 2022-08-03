#!/usr/bin/env python

from mmap import PROT_READ
import rospy
import tf2_ros
import numpy
import geometry_msgs
import rospy
from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
from math import pi, tau, dist, fabs, cos
import tf.transformations as transformations


# convertion matrix
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
