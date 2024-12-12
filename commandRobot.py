#!/usr/bin/env python3
import sys
import pickle
import rospy
import moveit_commander
import geometry_msgs.msg
from draw import drawStroke
import copy
import moveit_msgs.msg
import math
from std_msgs.msg import String
import numpy as np
import sensor_msgs.msg
import time as t
import tkinter

global current 
current = None


def callback(msg):
    global current
    current = np.array(msg.position) #grab current joint states
   
def main():
    global current

    stroke = drawStroke() #list of way points
    
    print(stroke)

    moveit_commander.roscpp_initialize(sys.argv) #from move it documentation python api, initialization
    rospy.init_node('move_group_python_interface_tutorial')
    robot_description = "my_gen3/robot_description"
    robot = moveit_commander.RobotCommander(robot_description=robot_description)
    group_name = "arm"
    group = moveit_commander.MoveGroupCommander(robot_description=robot_description, ns="my_gen3", name=group_name)

    group.set_max_velocity_scaling_factor(1)
    group.set_max_acceleration_scaling_factor(1)  # max speed

    
    
    rospy.Subscriber('/my_gen3/joint_states', sensor_msgs.msg.JointState, callback) #subscribe to current joint states
   
    #pose

    waypoints = []

    for i in range(len(stroke)):
        row = stroke.iloc[i] 
        p = geometry_msgs.msg.Pose()
        p.position.x = row["x"]
        p.position.y = row["y"]
        p.position.z = 0.243 #manually set z dir and w 
        p.orientation.w = 1
        waypoints.append(p)

        group.set_pose_target(p)
        print(str((i+1)/len(stroke) *100) + "%") #progress update

        success, plan, time, error = group.plan() #plan trajectory
        
        flag = False 
        ledStatus = True 

        if len(plan.joint_trajectory.points) > 0 and current is not None:
            # compare current joint states from subcriber with all joint states in the plan for the next pose
            current = current %(2*np.pi)

            for point in plan.joint_trajectory.points:
                pos = np.array(point.positions)
                pos = pos % (2*np.pi) #fix wrapping around 0 -2pi range
                diff = np.arctan2(np.sin(pos - current), np.cos(pos - current))
                diff = np.abs(diff) 

                if any(diff >= np.pi/6): # will cause out of plane motion if greater. 
                    flag = True # out of plane motion flag
                    break

            if flag:
                print("Caused joint to move more than pi/6")
                root = tkinter.Tk()
                root.withdraw()  
                tkinter.messagebox.showinfo("Warning", "Turn off LED, click done when LED is off") #stop until user presses okay
                ledStatus = False
                root.destroy()

        
        if success:
            group.go(wait =True) #execute

            if ledStatus is False: 
                root = tkinter.Tk()
                root.withdraw()  # Hide the root window
                tkinter.messagebox.showinfo("Warning", "Turn LED ON, click done when LED is on") # stop until user presses okay
                ledStatus = True
                root.destroy()

        else:
            print("unreachable point") # if plan success flag is unsuccessful 
            break

        if ((i+1)/len(stroke) == 1): #shut down when finished
            rospy.signal_shutdown("done")

    rospy.spin() # keep node running
    


if __name__ == "__main__":
    main()
