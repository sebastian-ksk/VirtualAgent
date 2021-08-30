import requests
import json
import urllib
import sys
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice,XBee64BitAddress,OperatingMode,RemoteATCommandPacket
from datetime import datetime, date, time, timedelta #para fechas y hora

# "/dev/ttyUSB0"

class XbeeCommunication():
    Path_Data=""
    
    def __init__(self, UsbDirection, baudRate,sensors, firebase,numberAgent,timeIrrig,PrescIrrig):
        self.FireBase = firebase
        self.ContsensorReport = 0 
        self.numberAgent = numberAgent
        self.timeIrrig = timeIrrig
        self.PrescIrrig = PrescIrrig
        self.FlagReceivedOrder = [False,False]
        self.numberReceivedOrders = 0
        self.FlagCompletedOrder = [False,False] 
        self.numberCompletedOrders = 0
        self.XbeesValvesSystem={'Agent_1': '0013A20041573102', 
        'Agent_2': '0013A20040D8D9C4',
        'Agent_3': '0013A20040DB569B',
        'Agent_4': '0013A20040E8816B'}
        print('xbee  ')
        self.sensors = sensors
        self.Path_Data = '/home/pi/Desktop/RealAgent/src/storage'
        self.device=XBeeDevice(UsbDirection,baudRate)
        self.device.open()
        print('xbee init ')

    def runCallback(self):
        try: 
            self.device.add_data_received_callback(self.data_receive_callback)
            print("Waiting for data...\n")
            input()
        finally:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
            if self.device is not None and self.device.is_open():
                self.device.close()  

    def data_receive_callback(self, xbee_message):
        self.message=str(xbee_message.data.decode()).split(':')
        print(str(datetime.now()).split()[1])
        self.today = date(datetime.now().year,datetime.now().month,datetime.now().day)
        if self.message[0] == 'IRRIG':
            print(str(xbee_message.data.decode()))
            if self.message[1].split(";")[0]=="COMPLETE":
                print('End Irrigation')
                self.save_data_Xbee(f"{self.Path_Data}/Irrigation_finished.txt",self.message[1].split('\x00')[0])             
                self.numberCompletedOrders += 1
                try:
                    self.FireBase.ResultIrrDoc_ref.update({
                        u'IrrigationState':'OFF',
                        u'LastIrrigationDate' : str(self.today),
                    })
                except:
                    print('error update data IrrigationState:OFF')
                          
            else:
                print('Irrigation Start')
                self.save_data_Xbee(f"{self.Path_Data}/Irrigation_started.txt",self.message[1])
                self.numberReceivedOrders += 1    
                try:
                    self.FireBase.ResultIrrDoc_ref.update({
                        u'IrrigationState':'ON'
                    })
                except:
                    print('error update data IrrigationState:ON')
                      
      
      
        elif self.message[0]=="SENSORS":
            print('sensores:')
            self.messageSens = self.message[1].split('\x00')[0].split('End')[0].split(',')
            self.save_data_Xbee(f"{self.Path_Data}/Sensor_data.txt",self.message[1].split('\x00')[0].split('End')[0])
            self.sensors.allSensors = [float(x) for x in self.messageSens[1:len(self.messageSens)-1] ]
            
            for x in range(0,4):
                self.sensors.allSensors[x] = round(self.calc_volumetricWaterContent(self.sensors.allSensors[x],4.75),2)
            
            if self.sensors.allSensors[4] >= 125:
                self.sensors.allSensors[4] = self.sensors.allSensors [8] 
            
            #
            
            self.file_HiD= open('/home/pi/Desktop/RealAgent/src/AquaCrop_OsPy/AquaCrop_OsPy/SensorsData/CalSensorData1.txt', 'r',errors='ignore')
            self.data = self.file_HiD.read().splitlines()
            self.file_HiD.close
            self.DataSensSimulate = self.data[-1].split('\t')
            self.vwcSimulate1 =  self.DataSensSimulate[3]
            self.file_HiD= open('/home/pi/Desktop/RealAgent/src/AquaCrop_OsPy/AquaCrop_OsPy/SensorsData/CalSensorData2.txt', 'r',errors='ignore')
            self.data = self.file_HiD.read().splitlines()
            self.file_HiD.close
            self.DataSensSimulate = self.data[-1].split('\t')
            self.vwcSimulate2 =  self.DataSensSimulate[10]    
            self.sensors.allSensors[0] = self.vwcSimulate1
            self.sensors.allSensors[1] = self.vwcSimulate2

            print(f'All Sensors : {self.sensors.allSensors}')
            self.sumSensors = 0
            for x in range(4,9):
                self.sumSensors = self.sumSensors + self.sensors.allSensors[x]

            if self.sumSensors > 0:
                now = datetime.now() 
                dateHour = str(now.strftime("%Y-%m-%d %H:%M:%S")) 
                self.Allsensors = self.sensors.allSensors
                data={"user":"Angel",
                "Treatment": self.numberAgent,
                "Longitude":float(5.5),
                "Latitude":float(-78.4),
                "SM_1":self.Allsensors[0],"SM_2":float(self.Allsensors[1]),"SM_3":float(self.Allsensors[2]),
                "Env_Temp":float(self.Allsensors[4]),"RH":float(self.Allsensors[5]),"CO2":float(self.Allsensors[6]),
                "Canopy_Temp":float(self.Allsensors[7]),"CS_Temp":float(self.Allsensors[8]),"Irrig_Pres_Rate":float(self.PrescIrrig),
                "Irrig_Pres_Time":float(self.timeIrrig),"Date_Time":dateHour}
                requests.post(url="http://104.248.53.140:8080/sPostV3.php",json=data)  

                if self.ContsensorReport == 12:
                    self.ContsensorReport=0   
                    try:
                        self.FireBase.SensorsDoc_ref.update({
                                u''+f'{str(self.today)}-{datetime.now().hour}:{datetime.now().minute}':{
                                    u'VWC1' :self.sensors.allSensors[0],
                                    u'VWC2' :self.sensors.allSensors[1],
                                    u'VWC3' :self.sensors.allSensors[2],
                                    u'VWC4' :self.sensors.allSensors[3],
                                    u'temperature' :self.sensors.allSensors[4],
                                    u'RH' : self.sensors.allSensors[5],
                                    u'soilTemperature':self.sensors.allSensors[6],
                                    u'CanopyTemperature':self.sensors.allSensors[7],
                                    u'CanopyTemperatureAmb':self.sensors.allSensors[8],
                                }    
                            })
                        print('Sensors Update to Firebase')    

                    except:
                        print("error update data sensors ")
                    
                else:
                    self.ContsensorReport+=1    


    def calc_volumetricWaterContent(self,adcValue,voltageReference):
           #........... Vegetronix Datasheet ...............
        self._sensorVoltage = (adcValue*voltageReference)/1024
        if self._sensorVoltage<=1.1:
            moistureValue = 10*self._sensorVoltage-1
            if moistureValue<=0.0:
                moistureValue=0.0
        elif self._sensorVoltage>1.1 and self._sensorVoltage<=1.3:
            moistureValue = 25*self._sensorVoltage-17.5
        elif self._sensorVoltage>1.3 and self._sensorVoltage<=1.82:
            moistureValue = 48.08*self._sensorVoltage-47.5
        elif self._sensorVoltage>1.82 and self._sensorVoltage<=2.2:
            moistureValue = 26.32*self._sensorVoltage-7.89
        elif self._sensorVoltage>2.2 and self._sensorVoltage<=3.0:
            #Original
            moistureValue = 62.5*self._sensorVoltage-87.5
        else:
            moistureValue = 100
        return moistureValue
        #  timeacq=time.asctime()
        #  hour=str(time.strftime("%H:%M:%S")) 
        #  day=str(time.strftime("%Y-%m-%d"))
        #  dy=str(day)+" "+str(hour)
        #  data={"user":"Angel","Treatment":3,"Longitude":float(5.5),"Latitude":float(-78.4),"SM_1":float(self.Allsensors [2]),"SM_2":float(self.Allsensors [3]),"SM_3":float(self.Allsensors [4]),"Env_Temp":float(self.Allsensors [5]),"RH":float(self.Allsensors [6]),"CO2":float(self.Allsensors [7]),"Canopy_Temp":float(self.Allsensors [8]),"CS_Temp":float(self.Allsensors [9]),"Irrig_Pres_Rate":0.0,"Irrig_Pres_Time":0.0,"Date_Time":str(dy)}
        #  requests.post(url="http://104.248.53.140:8080/sPostV3.php",json=data)  
#............. Felipe and Sebastian Equation
    #    if self._sensorVoltage<=1.34:
    #       moistureValue = 10.052*self._sensorVoltage-6.5
    #       if moistureValue<=0.0:
    #          moistureValue=0.0
    #    elif self._sensorVoltage>1.34 and self._sensorVoltage<=1.41:
    #       moistureValue = 91.8864*self._sensorVoltage-118.4967
    #    elif self._sensorVoltage>1.41 and self._sensorVoltage<=1.6036:
    #       moistureValue = 14.4655*self._sensorVoltage-10.6601
    #    elif self._sensorVoltage>1.6036 and self._sensorVoltage<=1.7735:
    #       moistureValue = 18.8*self._sensorVoltage-15.5687
    #    elif self._sensorVoltage>1.7735 and self._sensorVoltage<=2.0923:
    #       moistureValue = 41.1692*self._sensorVoltage-55.879
    #    elif self._sensorVoltage>2.0923 and self._sensorVoltage<=2.3201:
    #       moistureValue = 6.5147*self._sensorVoltage+16.3505
    #    elif self._sensorVoltage>2.3201 and self._sensorVoltage<=3.2:
    #       moistureValue = 4.5065*self._sensorVoltage+20.6494
    #    else:
    #       moistureValue = 43.0
    #    return moistureValue 
        

    def save_data_Xbee(self,directory,message):
        
        self.dir_file = directory
        self.SaveFile = open(self.dir_file, 'a',errors='ignore')
        self.SaveFile.write(f'{str(datetime.now()).split()[0]},{str(datetime.now()).split()[1]},{message}\n')
        self.SaveFile.close()

    def sendIrrigationOrder(self,message,Agent):
        try:
            print(self.XbeesValvesSystem[f'Agent_{Agent}'])
            self.remote_device=RemoteXBeeDevice(self.device,XBee64BitAddress.from_hex_string(self.XbeesValvesSystem[f'Agent_{Agent}']))     
            self.device.send_data(self.remote_device,message)   
            print('send xbee order .') 
            return True
        except:
            return False