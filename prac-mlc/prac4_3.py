import time
import sys
import random
import math
import brickpi
import time

#ROBOTICS
interface = brickpi.Interface()
interface.initialize()
motors = [0, 1]

k_p = 480.0
k_i = 400.0
k_d = 5.0

LENGTH = 15.0   #15 FOR 40CM
ANGLE = 20.5 #FOR 360
ANGLEPRECETIMETER = LENGTH / 40.0
ANGLEPERDEGREE = ANGLE / (2*math.pi)

left_coefficient = 1.035


def rotate(rotation):
    angle = rotation * ANGLEPERDEGREE
    interface.increaseMotorAngleReferences(motors, [-left_coefficient * angle, angle])
    motorAngles = interface.getMotorAngles(motors)
    initialValues = [motorAngles[0][0], motorAngles[1][0]]
    while not interface.motorAngleReferencesReached(motors):
        time.sleep(0.1)
    #time.sleep(0.1)

def goLine(distance):
    angle = distance * ANGLEPRECETIMETER
    interface.increaseMotorAngleReferences(motors, [left_coefficient * angle, angle])
    motorAngles = interface.getMotorAngles(motors)
    initialValues = [motorAngles[0][0], motorAngles[1][0]]
    while not interface.motorAngleReferencesReached(motors):
        time.sleep(0.1)
    #time.sleep(0.1)

#Initialization
interface.motorEnable(motors[0])
interface.motorEnable(motors[1])

motorParams0 = interface.MotorAngleControllerParameters()
motorParams0.maxRotationAcceleration = 6
motorParams0.maxRotationSpeed = 12
motorParams0.feedForwardGain = 255/20.0
motorParams0.minPWM = 18.0
motorParams0.pidParameters.minOutput = -255
motorParams0.pidParameters.maxOutput = 255
motorParams0.pidParameters.k_p = k_p
motorParams0.pidParameters.k_i = k_i
motorParams0.pidParameters.K_d = k_d

motorParams1 = interface.MotorAngleControllerParameters()
motorParams1.maxRotationAcceleration = 6.0
motorParams1.maxRotationSpeed = 12
motorParams1.feedForwardGain = 255/20.0
motorParams1.minPWM = 18.0
motorParams1.pidParameters.minOutput = -255
motorParams1.pidParameters.maxOutput = 255
motorParams1.pidParameters.k_p = k_p
motorParams1.pidParameters.k_i = k_i
motorParams1.pidParameters.K_d = k_d


interface.setMotorAngleControllerParameters(motors[0],motorParams0)
interface.setMotorAngleControllerParameters(motors[1],motorParams1)

#interface.startLogging("./log2_" + str(k_p) + ".txt"
'''
goLine(40)
rotate(90)
goLine(40)
rotate(90)
goLine(40)
rotate(90)
goLine(40)
rotate(90)
'''
NOP = 100 #numbef of particle
SIGMA_E = 1
SIGMA_F = 0.01
SIGMA_G = 0.02
D = 150

line1 = (100, 100, 100, 800) # (x0, y0, x1, y1)
line2 = (100, 100, 800, 100)  # (x0, y0, x1, y1)


print "drawLine:" + str(line1)
print "drawLine:" + str(line2)

class Dot(object):
    def __init__(self, x,y,theta,w):
        self.x = x
        self.y = y
        self.theta = theta
        self.w = w

#P = [] #particle

#for i in range(NOP):
    #P.append(Dot(0,0,0,1.0/NOP))
    



origin = Dot(0,0,0,1.0)
def compute_coord(x, y, wx, wy):
    dx = wx - x
    dy = wy - y
    alpha = math.atan2(dy, dx)
    dist = math.sqrt(dx*dx + dy*dy)
    return (alpha, dist)

def compute_angle_turn(curr_angle, dest_angle):
    print "cur:"+str(curr_angle/(math.pi)*180)
    print "des:"+str(dest_angle/(math.pi)*180)
    angle_diff = dest_angle - curr_angle
    if angle_diff > math.pi:
        angle_diff = -(math.pi*2 - angle_diff)
    if angle_diff < -math.pi:
        angle_diff = math.pi*2 + angle_diff
    return angle_diff,dest_angle

def get_average_point(P):
    avg_x = 0.0
    avg_y = 0.0
    avg_theta = 0.0
    for i in range(len(P)):
        avg_x += P[i].x*P[i].w
        avg_y += P[i].y*P[i].w
        avg_theta += P[i].theta*P[i].w
    return (avg_x, avg_y, avg_theta)

def update_points(D,angle_diff):
    for k in range(NOP):            
            P[k].x += (D+random.gauss(0, SIGMA_E))*math.cos(P[k].theta)
            P[k].y += (D+random.gauss(0, SIGMA_E))*math.sin(P[k].theta)
            P[k].theta += angle_diff + random.gauss(0,SIGMA_F)
            

def navigateToWaypoint():
    while 1:
        inputStr = raw_input("input destination:  ")
        if inputStr == "exit":
            print "mission completed"
            return 
        wx,wy = inputStr.split(',')
        wx = float(wx)
        wy = float(wy)
        navigateToWaypointAux(wx, wy)
    
def navigateToWaypointAux(wx, wy):
    curr_x, curr_y, curr_theta = origin.x,origin.y,origin.theta
    (alpha, dist) = compute_coord(curr_x, curr_y, wx, wy)
    angle_diff,dest_angle = compute_angle_turn(curr_theta, alpha)
    print angle_diff/(math.pi)*180
    rotate(angle_diff)
    goLine(dist)
    origin.x = wx
    origin.y = wy
    origin.theta = dest_angle
    print origin.x,origin.y,origin.theta



navigateToWaypoint()
#interface.stopLogging()
interface.terminate()
    

        
    
    
    