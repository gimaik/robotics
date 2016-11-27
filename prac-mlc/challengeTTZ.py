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
        self.n = 100;     # how many particles we use
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
        newData = [] 
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
    interface.increaseMotorAngleReferences(motors[:2], [-left_coefficient * angle, angle])
    motorAngles = interface.getMotorAngles(motors[:2])
    #initialValues = [motorAngles[0][0], motorAngles[1][0]]
    while not interface.motorAngleReferencesReached(motors[:2]):
        time.sleep(0.1)
        
def rotateMotor(rotation):
    angle = rotation * AnglePerRadius2
    interface.increaseMotorAngleReferences(motors, [0,0,angle])
    motorAngles = interface.getMotorAngles(motors)
    #initialValues = [motorAngles[0][0], motorAngles[1][0]]
    while not interface.motorAngleReferencesReached(motors):
        time.sleep(0.2)
        


def goLine(distance):
    angle = distance * AnglePerCentimeter
    interface.increaseMotorAngleReferences(motors[:2], [left_coefficient * angle, angle])
    motorAngles = interface.getMotorAngles(motors[:2])
    #initialValues = [motorAngles[0][0], motorAngles[1][0]]
    while not interface.motorAngleReferencesReached(motors[:2]):
        time.sleep(0.1)





        
#-----------------------------------MonteCarlo Localization----------------------------------
def readFromSonar():
    read_times = 20  #20
    result_list = []
    for i in range(read_times):
        result_list.append(interface.getSensorValue(port2)[0])
        #print result_list
        time.sleep(0.01)
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
motors = [0, 1, 2]

k_p = 480.0
k_i = 400.0
k_d = 5.0

LENGTH = 15.0   #15 FOR 40CM
ANGLE = 20.5 #FOR 360
AnglePerCentimeter = LENGTH / 40.0
AnglePerRadius = ANGLE / (2*math.pi) 
AnglePerRadius2 = 14*ANGLE / (15*math.pi*6) # for sonar sensor
left_coefficient = 0.9995
D = 150

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


#-------------Robot Initialization-------------
interface.motorEnable(motors[0])
interface.motorEnable(motors[1])
interface.motorEnable(motors[2])

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

#sonar sensor motor
motorParams2 = interface.MotorAngleControllerParameters()
motorParams2.maxRotationAcceleration = 2.0
motorParams2.maxRotationSpeed = 5
motorParams2.feedForwardGain = 255/20.0
motorParams2.minPWM = 18.0
motorParams2.pidParameters.minOutput = -255
motorParams2.pidParameters.maxOutput = 255
motorParams2.pidParameters.k_p = k_p
motorParams2.pidParameters.k_i = k_i
motorParams2.pidParameters.K_d = k_d

interface.setMotorAngleControllerParameters(motors[0],motorParams0)
interface.setMotorAngleControllerParameters(motors[1],motorParams1)
interface.setMotorAngleControllerParameters(motors[2],motorParams2)

#Sonar sensor
port2 = 2
interface.sensorEnable(port2, brickpi.SensorType.SENSOR_ULTRASONIC);


#---------------------------------------------------------Monte Carlo Test------------------------------------------------------------
'''

K = 0.001 # rubust likelihood constant
sigma = 3
numOfWall = 8
wayPoint = [(84,30),(120,30),(150,30),(180,30), (180,54), (138,54),(138,90),(138,130),(138,168), (114,168), (114,120),(114, 84), (84,84), (84,30)]
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
        particles.draw()
        particles.updateStraight(distToGo)
        particles.draw()
        sonarDist = readFromSonar()
        

        if sonarDist :
            particles.updateWeights(sonarDist)
            particles.normalizeWeights()
            
            print 'before resampling: ', particles.calculateMean().x,particles.calculateMean().y       
            particles.resampleParticles()
            print 'after resampling: ',particles.calculateMean().x,particles.calculateMean().y
            particles.draw()

        
        diff = math.sqrt((Wx - particles.calculateMean().x)**2 + (Wy - particles.calculateMean().y)**2)
        print 'diff: ',diff
'''
            

#----------------------------------------Place Recognition-----------------------------------



# Location signature class: stores a signature characterizing one location
class LocationSignature:
    def __init__(self, no_bins = 30): #set an interval of 6 degree
        self.sig = [0] * no_bins #initializes to all zeros
        
    def print_signature(self):
        for i in range(len(self.sig)):
            print self.sig[i]

# --------------------- File management class ---------------
class SignatureContainer():
    def __init__(self, size = 5):
        self.size      = size; # max number of signatures that can be stored
        self.filenames = [];
        
        # Fills the filenames variable with names like loc_%%.dat 
        # where %% are 2 digits (00, 01, 02...) indicating the location number. 
        for i in range(self.size):
            self.filenames.append('loc_{0:02d}.dat'.format(i))

    # Get the index of a filename for the new signature. If all filenames are 
    # used, it returns -1;
    def get_free_index(self):
        n = 0
        while n < self.size:
            if (os.path.isfile(self.filenames[n]) == False):
                break
            n += 1
            
        if (n >= self.size):
            return -1;
        else:    
            return n;
 
    # Delete all loc_%%.dat files
    def delete_loc_files(self):
        print "STATUS:  All signature files removed."
        for n in range(self.size):
            if os.path.isfile(self.filenames[n]):
                os.remove(self.filenames[n])
            
    # Writes the signature to the file identified by index (e.g, if index is 1
    # it will be file loc_01.dat). If file already exists, it will be replaced.
    def save(self, signature, index):
        filename = self.filenames[index]
        if os.path.isfile(filename):
            os.remove(filename)
            
        f = open(filename, 'w')

        for i in range(len(signature.sig)):
            s = str(signature.sig[i]) + "\n"
            f.write(s)
        f.close();

    # Read signature file identified by index. If the file doesn't exist
    # it returns an empty signature.
    def read(self, index):
        ls = LocationSignature()
        filename = self.filenames[index]
        if os.path.isfile(filename):
            f = open(filename, 'r')
            for i in range(len(ls.sig)):
                s = f.readline()
                if (s != ''):
                    ls.sig[i] = int(s)
            f.close();
        else:
            print "WARNING: Signature does not exist."
        
        return ls
        
# FILL IN: spin robot or sonar to capture a signature and store it in ls
def characterize_location(ls):
    for i in range(len(ls.sig)):
        sig_i = readFromSonar()
        rotateMotor(2*math.pi/len(ls.sig))
        time.sleep(0.1)
        ls.sig[i] = sig_i
    #ls.print_signature()
    rotateMotor(-2*math.pi)
    return ls

# FILL IN: compare two signatures
def compare_signatures(ls1, ls2):
    dist = 0
    #print "TODO:    You should implement the function that compares two signatures."
    ls_diff = [0]*(256/5+1)
    # transform into the frequency histogram
    for sig in ls1.sig:
        ls_diff[sig/5] += 1
    for sig in ls2.sig:
        ls_diff[sig/5] -= 1
    # calculate the signatures difference
    ls_diff = [x*x for x in ls_diff]
    dist = sum(ls_diff)
    return dist

# This function characterizes the current location, and stores the obtained 
# signature into the next available file.
def learn_location():
    ls = LocationSignature()
    characterize_location(ls)
    idx = signatures.get_free_index();
    if (idx == -1): # run out of signature files
        print "\nWARNING:"
        print "No signature file is available. NOTHING NEW will be learned and stored."
        print "Please remove some loc_%%.dat files.\n"
        return
    
    signatures.save(ls,idx)
    print "STATUS:  Location " + str(idx) + " learned and saved."

# This function tries to recognize the current location.
# 1.   Characterize current location
# 2.   For every learned locations
# 2.1. Read signature of learned location from file
# 2.2. Compare signature to signature coming from actual characterization
# 3.   Retain the learned location whose minimum distance with
#      actual characterization is the smallest.
# 4.   Display the index of the recognized location on the screen
def recognize_location():
    ls_obs = LocationSignature();
    characterize_location(ls_obs);

    # FILL IN: COMPARE ls_read with ls_obs and find the best match
    for idx in range(signatures.size):
        print "STATUS:  Comparing signature " + str(idx) + " with the observed signature."
        ls_read = signatures.read(idx);
        dist    = compare_signatures(ls_obs, ls_read)

# Prior to starting learning the locations, it should delete files from previous
# learning either manually or by calling signatures.delete_loc_files(). 
# Then, either learn a location, until all the locations are learned, or try to
# recognize one of them, if locations have already been learned.

            
            
#---------------------------------------------------------Place Recognition------------------------------------------------------------
#numOfWall = 8
#wayPoint = [(84,30), (150,30), (180,30), (180,54), (138,54), (138,100), (138,168), (114,168), (114, 84), (84,84), (84,30)]



'''
#---------------draw on web interface----------------
origin = Dot(84,30,0.0,0.0)
ls = LocationSignature()
dist = characterize_location(ls)

i = 0
for m in dist.sig:
    theta = i*2*math.pi/len(dist.sig)
    hitpoint_x = origin.x + m*math.cos(theta)
    hitpoint_y = origin.y + m*math.sin(theta)
    line = (origin.x,origin.y,hitpoint_x,hitpoint_y)
    print line
    i += 1
    canvas.drawLine(line)
'''


#--------------place to place recognition--------------
'''
ls1 = characterize_location(LocationSignature())
rotateMotor(math.pi/4)
#oLine(10)
ls2 = characterize_location(LocationSignature())
print compare_signatures(ls1, ls2)
'''

#-------------- train flow for 5 different places and save signature for new place recognition------------
# FILL IN
origin = Dot(84,30,0,0)    #84,30,0,0
(dist,angle_diff,dest_angle) = navigateToWaypointAux(84,20,origin) #84,20
rotate(angle_diff)
origin.theta += angle_diff
print(origin)

rotate(-0.05)
dis = readFromSonar()
interface.terminate()        
    

    
    
    
    
    
    
    
    
    
    
    
    
    