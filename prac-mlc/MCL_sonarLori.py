import brickpi
import time
import math

interface=brickpi.Interface()
interface.initialize()

SONAR_THRESHOLD = 10

#port0 = 0 # port which ultrasoic sensor is plugged in to
#port1 = 1
port2 = 2

#interface.sensorEnable(port, brickpi.SensorType.SENSOR_ULTRASONIC);
#interface.sensorEnable(port, brickpi.SensorType.SENSOR_TOUCH);
#interface.sensorEnable(port0, brickpi.SensorType.SENSOR_TOUCH);
#interface.sensorEnable(port1, brickpi.SensorType.SENSOR_TOUCH);
interface.sensorEnable(port2, brickpi.SensorType.SENSOR_ULTRASONIC);

def getSensorValue():
    sonarValues = []
    
    for i in range(20):
        usReading2 = interface.getSensorValue(port2)
        sonarValues.append(usReading2[0])   
        time.sleep(0.05)    
        sonarValues.sort() 
        median = sonarValues[10]

        #newSonarValues = []
        #for val in sonarValues:
        #   if abs(val - median) < SONAR_THRESHOLD:
        #      newSonarValues.append(val)
                
        return median
    


interface.terminate()