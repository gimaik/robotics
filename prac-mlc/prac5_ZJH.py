import time
import sys
import random
import math
import brickpi
import time

interface=brickpi.Interface()
interface.initialize()

class Map:
    def __init__(self):
        self.walls = [];
        self.loc = [];

    def add_wall(self,wall):
        self.walls.append(wall);

    def add_loc(self,loc):
        self.loc.append(loc);

    def clear(self):
        self.walls = [];

        
        
motors = [0, 1]

k_p = 480.0
k_i = 400.0
k_d = 5.0

LENGTH = 15.0   #15 FOR 40CM
ANGLE = 20.5 #FOR 360
AnglePerCentimeter = LENGTH / 40.0
AnglePerRadius = ANGLE / (2*math.pi) 
left_coefficient1 = 1.02
left_coefficient2 = 1.02
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
    interface.increaseMotorAngleReferences(motors, [left_coefficient2 * angle, -angle])
    motorAngles = interface.getMotorAngles(motors)
    #initialValues = [motorAngles[0][0], motorAngles[1][0]]
    while not interface.motorAngleReferencesReached(motors):
        time.sleep(0.1)


def goLine(distance):
    angle = distance * AnglePerCentimeter
    interface.increaseMotorAngleReferences(motors, [left_coefficient1 * angle, angle])
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
    #print "cur:"+str(curr_angle/(math.pi)*180)
    #print "des:"+str(dest_angle/(math.pi)*180)
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
    #print alpha,dist
    angle_diff, dest_angle = compute_angle_turn(curr_theta, alpha)
    
    origin.x = wx
    origin.y = wy
    origin.theta =  dest_angle 
    #print origin.x,origin.y,origin.theta
    return dist,angle_diff
    

port2 = 2

interface.sensorEnable(port2, brickpi.SensorType.SENSOR_ULTRASONIC);
                       
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

mymap.add_loc((84,30));        
mymap.add_loc((180,30));        
mymap.add_loc((180,54));        
mymap.add_loc((138,54));        
mymap.add_loc((138,80));  
mymap.add_loc((138,120));  
mymap.add_loc((138,168));        
mymap.add_loc((114,168));        
mymap.add_loc((114,84));        
mymap.add_loc((84,84));        
mymap.add_loc((84,30));        


          
            
def calculate_likelihood(x, y, theta, z):
    m = -1
    for i in range(8):
        Ax = mymap.walls[i][0]
        Ay = mymap.walls[i][1]
        Bx = mymap.walls[i][2]
        By = mymap.walls[i][3]
        d = ((By-Ay)*(Ax-x)-(Bx-Ax)*(Ay-y))/((By-Ay)*math.cos(theta)-(Bx-Ax)*math.sin(theta)+0.00000000001)
        if d>0:
            x_inwall = x+d*math.cos(theta)
            y_inwall = y+d*math.sin(theta)
            if (x_inwall-Ax)*(x_inwall-Bx)+(y_inwall-Ay)*(y_inwall-By)<=0 and (m<0 or d<m):
                m = d
    sigma_s = 0.5 # standard deviation for sensor in cm    
    return math.exp(-(z-m)**2/(2*sigma_s**2))





NOP = 100 #numbef of particle
SIGMA_E = 1 # gaussian error in distance angle
SIGMA_F = 0.005 # gaussian error in straight line moving angle
SIGMA_G = 0.01 # gaussian error in rotation angle




P = [] #particle
for i in range(NOP):
    P.append(Dot(mymap.loc[0][0],mymap.loc[0][1],0,1.0/NOP))  # just take the same weight

    
    
    # divide each edge of the square into 4 pieces and run one at a time then sleep for a while
particles = [(P[l].x,P[l].y,P[l].theta) for l in range(NOP)]
print "drawParticles:" + str(particles)

i = 1

while i<11:
    curr = get_average_point(P)
    curr_1 = []
    curr_1.append(Dot(curr[0],curr[1],curr[2],1))   
    
    (D,angle_diff) = navigateToWaypointAux(mymap.loc[i][0], mymap.loc[i][1], curr_1[0])
    print "Move distance and angle",D,angle_diff*180/math.pi
    rotate(angle_diff)
    goLine(D)
    
    for j in range(NOP):
        P[j].theta += angle_diff+random.gauss(0,SIGMA_G)
        P[j].x += (D+random.gauss(0, SIGMA_E))*math.cos(P[j].theta)
        P[j].y += (D+random.gauss(0, SIGMA_E))*math.sin(P[j].theta)
        P[j].theta += random.gauss(0,SIGMA_F)
    
    
    particles = [(P[l].x,P[l].y,P[l].theta) for l in range(NOP)]
    print "drawParticles:" + str(particles)
        
    curr = get_average_point(P)
    print "new loc",curr[0],curr[1],curr[2]
    
    z = 0
    z_n = 0
    usReading = []
    for j in range(30):   
        sonar = interface.getSensorValue(port2)
        
        usReading.append(sonar[0])
        time.sleep(0.01)
    for j  in range(30):
        if usReading[j]<255:
            z_n += 1
            z += usReading[j]
    
    if z_n==0:
        z = 255
    else:
        z = float(z)/z_n
        
    z =z + 5
    
    print z
    if z<255:
        for j in range(NOP):
            P[j].w = calculate_likelihood(P[j].x, P[j].y, P[j].theta, z)
            
    
        w_sum = 0.00001
        for j in range(NOP):
            w_sum += P[j].w
        
        
        for j in range(NOP):
            P[j].w = P[j].w/w_sum
                   
                
    curr = get_average_point(P)
    print "new loc",curr[0],curr[1],curr[2]*angle_diff*180/math.pi
    
    var = [0,0,0]
    for j in range(NOP):
        var[0] += P[j].w*(curr[0]-P[j].x)**2
        var[1] += P[j].w*(curr[1]-P[j].y)**2
        var[2] += P[j].w*(curr[2]-P[j].theta)**2
    
    for j in range(NOP):
        P[j].x = random.gauss(curr[0], var[0])
        P[j].y = random.gauss(curr[1], var[1])
        P[j].theta = random.gauss(curr[2], var[2])
        P[j].w = 1.0/NOP
       
    '''
    index1 = 0 index2 = 0
    P_new = []
    w1 =0 w2 =0
    while index2<NOP:
        if w2<w1:
            P_new.append((Dot(P[index1].x,Dot(P[index1].y,Dot(P[index1].theta,1.0/NOP))
            w2 = w2+1.0/NOP
            index2 = index2+1
        else:
            index1 = index1 +1
            w1 = w1+P[index1].w            
    
    
    
    P = P_new    
    '''
    
    curr = get_average_point(P)
    #print "new loc2",curr[0],curr[1],curr[2]*angle_diff*180/math.pi
    particles = [(P[l].x,P[l].y,P[l].theta) for l in range(NOP)]
    print "drawParticles:" + str(particles)
    
    if curr[0]-mymap.loc[i][0]<2 and curr[1]-mymap.loc[i][1]<2:
        i =i+1
    
        # Create a list of particles to draw. This list should be filled by tuples (x, y, theta).




interface.terminate()




  
    

