#!/usr/bin/env python 

# Some suitable functions and data structures for drawing a map and particles

import time
import random
import math
from version3 import *

SIGMA_E = 1 # gaussian error in distance angle
SIGMA_F = 0.01 # gaussian error in straight line moving angle
SIGMA_G = 0.02 # gaussian error in rotation angle
class Dot(object):
    def __init__(self, x,y,theta,weight):
        self.x = x
        self.y = y
        self.theta = theta
        self.weight = weight


# A Canvas class for drawing a map and particles:
#     - it takes care of a proper scaling and coordinate transformation between
#      the map frame of reference (in cm) and the display (in pixels)
class Canvas:
    def __init__(self,map_size=210):
        self.map_size    = map_size;    # in cm;
        self.canvas_size = 768;         # in pixels;
        self.margin      = 0.05*map_size;
        self.scale       = self.canvas_size/(map_size+2*self.margin);
        
    # line is a tuple that contains the x,y for the start point and end point
    def drawLine(self,line):
        x1 = self.__screenX(line[0]);
        y1 = self.__screenY(line[1]);
        x2 = self.__screenX(line[2]);
        y2 = self.__screenY(line[3]);
        print "drawLine:" + str((x1,y1,x2,y2))

    # data is the cloud of particles
    def drawParticles(self,data):
        display = [(self.__screenX(d.x),self.__screenY(d.y))  for d in data];
        print "drawParticles:" + str(display);
    
    # given the x,y display it on the screen
    def __screenX(self,x):
        return (x + self.margin)*self.scale

    def __screenY(self,y):
        return (self.map_size + self.margin - y)*self.scale

# Simple Particles set
class Particles:
    def __init__(self,x,y,theta):
        self.n = 50;     # how many particles we use
        self.data = [];  # initialize all particles to the same origin
        for i in range(self.n):
            self.data.append(Dot(x,y,theta,1.0/self.n))

    # spread out after going straight
    def updateStraight(self,dist):
        for i in range(self.n):
            self.data[i].x += (dist+random.gauss(0, SIGMA_E))*math.cos(self.data[i].theta)
            self.data[i].y += (dist+random.gauss(0, SIGMA_E))*math.sin(self.data[i].theta)
            self.data[i].theta += random.gauss(0,SIGMA_F)
            
    # spread out after rotation
    def updateRotate(self,rotAngle):
        for i in range(self.n):
            self.data[i].theta += rotAngle + random.gauss(0,SIGMA_G)
            
    def evenWeight(self,dot):
        return Dot(dot.x,dot.y,dot.theta,1.0/self.n)
    
    # from differently-weighted particles to evenly-weighted particles
    def resampleParticles(self):
        sum = 0.0
        cumProb = [] # cumulative probability distribution
        newData = self.data
        for i in range(self.n):
            sum += self.data[i].weight
            cumProb.append(sum)
               
        for i in range(self.n):
            u = random.random() 
            pos = -1
            for j in range(self.n):
                if u < cumProb[j]:
                    pos = j
                    break
            if (pos == -1):
                pos = self.n - 1
            newData.append(self.evenWeight(self.data[pos]))
        self.data = newData
        return True
                
    def updateWeights(self,sonarDist):
        # update weights of each particles(unnormalized)
        for i in range(self.n):
            self.data[i].weight = self.data[i].weight*calculate_likelihood(self.data[i].x,self.data[i].y,self.data[i].theta,sonarDist)

    def normalizeWeights(self):
        sum = 0.0
        for i in range(self.n):
            sum += self.data[i].weight
        for i in range(self.n):
            self.data[i].weight = self.data[i].weight/sum

    def calculateMean(self):
        # given the current particles distribution to calculate the mean
        #mean = Dot(84.0, 30.0, 0.0, 1/self.n)
        mean = Dot(0.0, 0.0, 0.0, 1/self.n)
        for i in range(self.n):
            mean.x += self.data[i].x*self.data[i].weight
            mean.y += self.data[i].y*self.data[i].weight
            mean.theta += self.data[i].theta*self.data[i].weight
        return mean

    def draw(self):
        canvas.drawParticles(self.data);


# A Map class containing walls
class Map:
    def __init__(self):
        self.walls = [];

    def add_wall(self,wall):
        self.walls.append(wall);

    def clear(self):
        self.walls = [];

    
    def draw(self):
        for wall in self.walls:
            canvas.drawLine(wall);
            

#---------------------------------------------------main----------------------------------



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

        
#-----------------------------------MonteCarlo Localization----------------------------------
def readFromSonar():
    read_times = 20
    result_list = []
    for i in range(read_times):
        result_list.append(interface.getSensorValue(port2)[0])
        #print result_list
        time.sleep(0.1)
    #print sum(result_list)/read_times 
    return (sum(result_list)/read_times + 1)


def calculate_likelihood(x,y,theta,z):
    m = 9999 # predicted distance to the wall
    for wall_index in range(numOfWall):
        #print wall_index
        Ax = mymap.walls[wall_index][0]
        Ay = mymap.walls[wall_index][1]
        Bx = mymap.walls[wall_index][2]
        By = mymap.walls[wall_index][3]
        
        # the measured dictance of current position to the line of the 'wall'
        dist = ((By-Ay)*(Ax-x)-(Bx-Ax)*(Ay-y)) / ((By-Ay)*math.cos(theta)-(Bx-Ax)*math.sin(theta)+0.00000000001)
        #print 'dist',dist
        
        if dist >= 0:
            # the exact place to hit the wall
            x_hypo = x + dist * math.cos(theta)
            y_hypo = y + dist * math.sin(theta)
            if (x_hypo-Ax)*(x_hypo-Bx) + (y_hypo-Ay)*(y_hypo-By) <= 0 and dist<m:  # hit point between endpoints of walls is real, and only keep the shortest distance
                #print 'we find the right dist!',dist
                m = dist
                #print m
        
        #print 'chosen:',m
    return math.exp(-((z-m))**2/(2*sigma**2)) + K #unnormalised, robust likelihood
        
#read the sonar output and use bayes theorem to update the weight of each particles
'''
def updateWeight(particles,sonarDist):
    sumWeights =0
    for i in range(particles.n):
        particles.data[i].weight = particles.data[i].weight*calculate_likelihood(particles.data[i].x,particles.data[i].y,particles.data[i].theta,sonarDist)
        sumWeights += particles.data[i].weight
    # normalization
    for j in range(particles.n):
        particles.data[j].weight = particles.data[j].weight / sumWeights
    return particles
    '''

# givne all weighted particles to calculate the next mean
'''
def updateMean(particles):
    sum_x = 0
    sum_y = 0
    sum_theta = 0
    for i in range(particles.n):
        sum_x += particles.data[i].weight*particles.data[i].x
        sum_y += particles.data[i].weight*particles.data[i].y
        sum_theta += particles.data[i].weight*particles.data[i].theta
    
    print('before meanupdate: ', particles.data[0].x,particles.data[0].y, particles.data[0].theta)
    
    for i in range(particles.n):
        particles.data[i].x = sum_x/particles.n
        particles.data[i].y = sum_y/particles.n
        particles.data[i].theta = sum_theta/particles.n
        
    print('after meanupdate: ',particles.data[0].x,particles.data[0].y, particles.data[0].theta)
    '''


        

# ---------------------------------Waypoint navigation-----------------------------------
def compute_coord(x, y, wx, wy):
    dx = wx - x
    dy = wy - y
    alpha = math.atan2(dy, dx)  #in radius
    dist = math.sqrt(dx*dx + dy*dy)
    return (alpha, dist)

def compute_angle_turn(curr_angle, dest_angle):
    #print "cur:"+str(curr_angle/(math.pi)*180)
    #print "des:"+str(dest_angle/(math.pi)*180)
    angle_diff = dest_angle - curr_angle
    # tricks to reduce the turing anle
    if angle_diff > math.pi:
        angle_diff = -(math.pi*2 - angle_diff)
    if angle_diff < -math.pi:
        angle_diff = math.pi*2 + angle_diff
    print 'need to rotate: ',angle_diff
    return angle_diff, dest_angle

'''
def get_average_point(P):
    avg_x = 0.0
    avg_y = 0.0
    avg_theta = 0.0
    for i in range(len(P)):
        avg_x += P[i].x*P[i].w
        avg_y += P[i].y*P[i].w
        avg_theta += P[i].theta*P[i].w
    return (avg_x, avg_y, avg_theta)


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
        '''
    
def navigateToWaypointAux(wx, wy, origin):
    curr_x, curr_y, curr_theta = origin.x,origin.y,origin.theta
    (alpha, dist) = compute_coord(curr_x, curr_y, wx, wy)
    angle_diff, dest_angle = compute_angle_turn(curr_theta, alpha)
    print('angle_diff:', angle_diff, 'dest_angle:', dest_angle)
    
    rotate(-angle_diff) #remember the minus
    goLine(dist)
    '''
    origin.x = wx
    origin.y = wy
    origin.theta =  dest_angle 
    '''
    #print origin.x,origin.y,origin.theta
    return dist,angle_diff,dest_angle

#-------------------------------------------Main test-----------------------------------------------
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
left_coefficient = 0.9995
D = 150

#-------------Robot Initialization-------------
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

#Sonar sensor
port2 = 2
interface.sensorEnable(port2, brickpi.SensorType.SENSOR_ULTRASONIC);

canvas = Canvas();    # global canvas we are going to draw on
mymap = Map();
# Definitions of walls
# a: O to A
# b: A to B
# c: C to D
# d: D to E
# e: E to F
# f: F to G
# g: G to H
# h: H to O
mymap.add_wall((0,0,0,168));        # a
mymap.add_wall((0,168,84,168));     # b
mymap.add_wall((84,126,84,210));    # c
mymap.add_wall((84,210,168,210));   # d
mymap.add_wall((168,210,168,84));   # e
mymap.add_wall((168,84,210,84));    # f
mymap.add_wall((210,84,210,0));     # g
mymap.add_wall((210,0,0,0));        # h
mymap.draw();


K = 0.001 # rubust likelihood constant
sigma = 3
numOfWall = 8
wayPoint = [(84,30),(180,30), (180,54), (138,54),(138,168), (114,168), (114, 84), (84,84), (84,30)]

particles = Particles(wayPoint[0][0], wayPoint[0][1], 0) # initialized to [84.0, 30.0, 0.0]

tol  = 2.0 # tolerance of deviation
for Wx,Wy in wayPoint:
    diff = math.sqrt((Wx - particles.calculateMean().x)**2 + (Wy- particles.calculateMean().y)**2)
    print 'diff to'+str(Wx)+','+str(Wy),diff


    while diff > tol:
    #for k in range(0,50):
        origin = particles.calculateMean()
        print "origin",origin.x,origin.y,origin.theta
        distToGo,angleToGo,dest_angle = navigateToWaypointAux(Wx,Wy,origin)
        print('disttogo:', distToGo, 'angleToGo:' , angleToGo)
        particles.updateRotate(angleToGo)
        particles.updateStraight(distToGo)
        sonarDist = readFromSonar()
        
        '''
        for i in range(particles.n):
            updateWeight(particles,sonarDist)
            updateMean(particles)
            '''

        if sonarDist :
            particles.updateWeights(sonarDist)
            particles.normalizeWeights()
            print 'before resampling: ', particles.calculateMean().x,particles.calculateMean().y       
            particles.resampleParticles()
            print 'after resampling: ',particles.calculateMean().x,particles.calculateMean().y

        
        diff = math.sqrt((Wx - particles.calculateMean().x)**2 + (Wy - particles.calculateMean().y)**2)
        print 'diff: ',diff
        
        
    

    
    
    
    
    
    
    
    
    
    
    
    
    