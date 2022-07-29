from logging.config import listen
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


# Global variables


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



def init():
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



def goto_home():
    # load the tf between tag to end effector
    tag_EE_M = pickle.load(open("home.pickle", "rb"))
    listener.







if __name__ = '__main__':
    init()
    goto_home()
    frame = calcuate_vial_frame()
    goto_vial(frame)
    open_gripper()
    go_down()
    close_gripper()
    sleep(30)
    open_gripper()
    go_up()