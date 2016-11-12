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
AnglePerCentimeter = LENGTH / 40.0
AnglePerRadius = ANGLE / (2*math.pi) 
left_coefficient = 1.035
D = 150

#-------------------------------Initialization----------------------------------------
interface.motorEnable(motors[0])
interface.motorEnable(motors[1])

#Left motor
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

#Right motor
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


# -------------------------------------Movement function-------------------------------------
def rotate(rotation):
    angle = rotation * AnglePerRadius
    interface.increaseMotorAngleReferences(motors, [-left_coefficient * angle, angle])
    motorAngles = interface.getMotorAngles(motors)
    #initialValues = [motorAngles[0][0], motorAngles[1][0]]
    while not interface.motorAngleReferencesReached(motors):
        time.sleep(0.1)


def goLine(distance):
    angle = distance * AnglePerCentimeter
    interface.increaseMotorAngleReferences(motors, [left_coefficient * angle, angle])
    motorAngles = interface.getMotorAngles(motors)
    #initialValues = [motorAngles[0][0], motorAngles[1][0]]
    while not interface.motorAngleReferencesReached(motors):
        time.sleep(0.1)

#interface.startLogging("./log2_" + str(k_p) + ".txt"

#----------------------------------------Square test--------------------------------------------
'''
goLine(40)
rotate(90/(2*math.pi))
goLine(40)
rotate(90/(2*math.pi))
goLine(40)
rotate(90/(2*math.pi))
goLine(40)
rotate(90/(2*math.pi))
'''
class Dot(object):
    def __init__(self, x,y,theta,weight):
        self.x = x
        self.y = y
        self.theta = theta
        self.w = weight

#----------------------------------------Web page simulation--------------------------------------
def webSimulation():
    NOP = 100 #numbef of particle
    SIGMA_E = 1 # gaussian error in distance angle
    SIGMA_F = 0.01 # gaussian error in straight line moving angle
    SIGMA_G = 0.02 # gaussian error in rotation angle


    line1 = (100, 100, 100, 800) # (x0, y0, x1, y1)
    line2 = (100, 100, 800, 100)  # (x0, y0, x1, y1)


    print "drawLine:" + str(line1)
    print "drawLine:" + str(line2)

    P = [] #particle
    for i in range(NOP):
        P.append(Dot(100,100,0,1.0/NOP))  # just take the same weight

    particles = [(P[l].x,P[l].y,P[l].theta) for l in range(NOP)]
    print "drawParticles:" + str(particles)
    # divide each edge of the square into 4 pieces and run one at a time then sleep for a while
    for i in range(4):
        for j in range(4):
            for k in range(NOP):            
                P[k].x += (D+random.gauss(0, SIGMA_E))*math.cos(P[k].theta)
                P[k].y += (D+random.gauss(0, SIGMA_E))*math.sin(P[k].theta)
                P[k].theta += random.gauss(0,SIGMA_F)
                
        # Create a list of particles to draw. This list should be filled by tuples (x, y, theta).
            particles = [(P[l].x,P[l].y,P[l].theta) for l in range(NOP)]
            # MOVE 10cm
            goLine(10)
            # DRAW 
            print "drawParticles:" + str(particles)
            time.sleep(0.5)
            
        # rotation
        for k in range(NOP):
            P[k].theta += math.pi/2+random.gauss(0,SIGMA_G)
        particles = [(P[l].x,P[l].y,P[l].theta) for l in range(NOP)]
        # ROTATE
        rotate(90/(2*math.pi))
        print "drawParticles:" + str(particles)
        #time.sleep(0.5)
        


# ---------------------------------Waypoint navigation-----------------------------------
def compute_coord(x, y, wx, wy):
    dx = wx - x
    dy = wy - y
    alpha = math.atan2(dy, dx)  #in radius
    dist = math.sqrt(dx*dx + dy*dy)
    return (alpha, dist)

def compute_angle_turn(curr_angle, dest_angle):
    print "cur:"+str(curr_angle/(math.pi)*180)
    print "des:"+str(dest_angle/(math.pi)*180)
    angle_diff = dest_angle - curr_angle
    # tricks to reduce the turing anle
    if angle_diff > math.pi:
        angle_diff = -(math.pi*2 - angle_diff)
    if angle_diff < -math.pi:
        angle_diff = math.pi*2 + angle_diff
    return angle_diff, dest_angle

def get_average_point(P):
    avg_x = 0.0
    avg_y = 0.0
    avg_theta = 0.0
    for i in range(len(P)):
        avg_x += P[i].x*P[i].w
        avg_y += P[i].y*P[i].w
        avg_theta += P[i].theta*P[i].w
    return (avg_x, avg_y, avg_theta)

'''

def update_points(D,angle_diff):
    for k in range(NOP):            
            P[k].x += (D+random.gauss(0, SIGMA_E))*math.cos(P[k].theta)
            P[k].y += (D+random.gauss(0, SIGMA_E))*math.sin(P[k].theta)
            P[k].theta += angle_diff + random.gauss(0,SIGMA_F)
            '''
            

def navigateToWaypoint(start_point):
    origin = start_point
    while 1:
        inputStr = raw_input("input destination:  ")
        if inputStr == "exit":
            print "mission completed"
            return 
        wx,wy = inputStr.split(',')
        wx = float(wx)
        wy = float(wy)
        navigateToWaypointAux(wx, wy, origin)
    
def navigateToWaypointAux(wx, wy, origin):
    curr_x, curr_y, curr_theta = origin.x,origin.y,origin.theta
    (alpha, dist) = compute_coord(curr_x, curr_y, wx, wy)
    angle_diff, dest_angle = compute_angle_turn(curr_theta, alpha)
    rotate(angle_diff)
    goLine(dist)
    origin.x = wx
    origin.y = wy
    origin.theta =  dest_angle 
    print origin.x,origin.y,origin.theta
    return dist,angle_diff
#webSimulation()    
#origin = Dot(0,0,0,1.0)
#navigateToWaypoint(origin)
#interface.stopLogging()
interface.terminate()
    

        
    
    
    