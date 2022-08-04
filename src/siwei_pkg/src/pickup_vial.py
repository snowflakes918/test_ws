#!/usr/bin/env python

import csv
from email import header
from multiprocessing.connection import wait
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
    # print("=-=-=-=-=-=-=fraction=-=-=-=-=-=-==-=-")
    # print(fraction)

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
        group.execute(trajecotry, wait=True)
        # print("-=-=--==-=-=-SUCCESS-=-=-=-=-=-=-=-")
    else:
        print("-=-=-=-=-=-=-=-FAIL-=-=-=-=-=--=-=--")

    # # Calling `stop()` ensures that there is no residual movement
    group.stop()
    group.clear_pose_targets()


def goto_home1():
    joint_position = [-0.3042415636565341, -0.516771066715793, 0.23751219045310307, -1.9972557551605137, 0.10984729260846328, 1.5081504631572298, 0.6868139929042922]
    group.go(joint_position, wait=True)
    group.stop()

def goto_home2():
    joint_position = [-0.34463144525266226, 0.3495718096281662, 0.22345331240551683, -1.2203279933427509, 0.036560375945434716, 1.21377803489897, 0.290615091152732]
    group.go(joint_position, wait=True)
    group.stop()

def goto_home3():
    joint_position = [-0.27561389103205225, -1.063369343777398, 0.14180338345826177, -2.6073108657035737, 0.11509165027569186, 1.9262957933770377, 0.42931716665211644]
    group.go(joint_position, wait=True)
    group.stop()

def goto_home4():
    joint_position = [-0.3042415636565341, -0.516771066715793, 0.23751219045310307, -1.9972557551605137, 0.10984729260846328, 1.5081504631572298, 0.6868139929042922]
    group.go(joint_position, wait=True)
    group.stop()

def goto_home5():
    joint_position = [-0.3042415636565341, -0.516771066715793, 0.23751219045310307, -1.9972557551605137, 0.10984729260846328, 1.5081504631572298, 0.6868139929042922]
    group.go(joint_position, wait=True)
    group.stop()



def goto_home():
    # load the tf between tag to end effector
    home_pose = pickle.load(open("./src/siwei_pkg/pickle/home_tf1.pickle", "rb"))


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


    world_tag = tfBuffer.lookup_transform('world', 'tag_1', rospy.Time(), rospy.Duration(1.0)) 

    orientation_list = [
                        world_tag.transform.rotation.w, 
                        world_tag.transform.rotation.x, 
                        world_tag.transform.rotation.y, 
                        world_tag.transform.rotation.z, 
                        ]

    (r, p, y) = transformations.euler_from_quaternion(orientation_list)

    world_tag_str = [
                        world_tag.transform.translation.x, 
                        world_tag.transform.translation.y, 
                        world_tag.transform.translation.z, 
                        r,
                        p,
                        y
                        ]

    with open('./data/home_tag_pose_data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(world_tag_str)


def calcuate_vial_frame():
    # load the tf between tag to end effector
    tag_EE_M = pickle.load(open("./src/siwei_pkg/pickle/vial_tf.pickle", "rb"))

    # calculate robot pose from tag pose
    world_tag = tfBuffer.lookup_transform('world', 'tag_1', rospy.Time(), rospy.Duration(1.0))
    world_tag_M = mytools.convert_to_matirx(world_tag)
    world_EE_M = numpy.matmul(world_tag_M, tag_EE_M)
    world_EE_tf = mytools.convert_to_transform(world_EE_M)

    orientation_list = [
                        world_tag.transform.rotation.w, 
                        world_tag.transform.rotation.x, 
                        world_tag.transform.rotation.y, 
                        world_tag.transform.rotation.z
                        ]

    (r, p, y) = transformations.euler_from_quaternion(orientation_list)

    world_tag_str = [
                        world_tag.transform.translation.x, 
                        world_tag.transform.translation.y, 
                        world_tag.transform.translation.z, 
                        r,
                        p,
                        y
                        ]


    with open('./data/tag_pose_data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(world_tag_str)

    return world_EE_tf


def goto_vial(vial_frame):

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

    current_pose = group.get_current_pose()

    orientation_list = [
                    current_pose.pose.orientation.w, 
                    current_pose.pose.orientation.x, 
                    current_pose.pose.orientation.y, 
                    current_pose.pose.orientation.z, 
                    ]

    (r, p, y) = transformations.euler_from_quaternion(orientation_list)

    current_pose_str = [
                        current_pose.pose.position.x, 
                        current_pose.pose.position.y, 
                        current_pose.pose.position.z, 
                        r,
                        p,
                        y
                        ]
    

    with open('./data/vial_robot_pose_data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(current_pose_str)


def header_printer():
    header = ['x', 'y', 'z', 'rx', 'ry', 'rz']

    with open('./data/vial_robot_pose_data.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    with open('./data/tag_pose_data.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    with open('./data/home_tag_pose_data.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

def open_gripper():
    gripper.open()

def go_down():
    robot_pose = group.get_current_pose()
    print("robot_pose")
    print(robot_pose)

    # set up pose goal
    panda_pose = robot_pose.pose
    panda_pose.position.z -= 0.1 # go down 10 cm

    plan_and_execute(panda_pose)

def close_gripper():
    gripper.fully_close()

def go_up():
    robot_pose = group.get_current_pose()
    print("robot_pose")
    print(robot_pose)

    # set up pose goal
    panda_pose = robot_pose.pose
    panda_pose.position.z += 0.1 # go down 10 cm

    plan_and_execute(panda_pose)



if __name__ == '__main__':
    
    # header_printer()
    # for i in range(10):
    #     goto_home()
    #     rospy.sleep(1.0)
    #     vial_frame = calcuate_vial_frame()    
    #     goto_vial(vial_frame)
    #     rospy.sleep(2.0)

    
    vial_frames = []
    goto_home1()
    vial_frames.append(mytools.convert_to_matirx(calcuate_vial_frame()))
    rospy.sleep(1.0)
    goto_home2()
    vial_frames.append(mytools.convert_to_matirx(calcuate_vial_frame()))
    rospy.sleep(1.0)   
    goto_home3()
    vial_frames.append(mytools.convert_to_matirx(calcuate_vial_frame()))   
    rospy.sleep(1.0)  
    # goto_home4()     
    # vial_frame.append(calcuate_vial_frame())
    # goto_home5()          
    # vial_frame.append(calcuate_vial_frame())
    
    mat = [[0 for _ in range(4)] for _ in range(4)]
    # mat = numpy.matrix(mat)

    for m in vial_frames:
        mat += m

    average_vial_frame = mat / 3

    average_vial_frame = mytools.convert_to_transform(average_vial_frame)

    goto_vial(average_vial_frame)
    # open_gripper()
    go_down()


    



