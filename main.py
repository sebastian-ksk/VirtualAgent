# created by: sebastian castellanos
from data.ApiServiceEstacionMet import ApiServiceEstacionMet
from data.FireBase import FIREBASE_CLASS
from model.ModelVarMeTereologica import meteorologicalData as DatMet
from model.ModelCultivo import Crop
from model.ModelSensores import Sensors
from model.ModelirrigProperties import irrigation_properties

from model.ModelPrescriptionResult import PrescriptionResults
from services.mqttComunication import MqttComunication
from services.xbeeCommunication import XbeeCommunication
from services.PrescriptionMethods import prescriptionMethods

# from AquaCrop_OsPy.AquaCrop_OsPy.AquaCrop_OS_v5  import AquaCrop_os

"""
librerias externas al sistema 
"""
import signal
from apscheduler.schedulers.background import (
    BackgroundScheduler,
)  # para programar tareas
from datetime import datetime, date, time, timedelta  # para fechas y hora
import time as timedelay  # para cronometrar tiempo
from threading import Thread

import sys, os

print(sys.path)
import requests
import json
import urllib
import json


class Main:
    def __init__(self):
        super(Main, self).__init__()
        """inicializacion de datos"""
        print("init data")

        self.groundDivision = "Tibasosa"

        self.agent = int(input("ingrese el numero del agente : "))
        self.FlagPrescriptionDone = False
        self.FlagOrderIrrigSend = False
        self.FlagirrigationAuthor = False
        self.TimePrescription = 0
        self.TotalPrescription = 0
        self.HourSendIrrigOrder = datetime.now()
        self.IrrigAplied = 0
        self.TotalPrescription = 0
        self.FlagTotalPrescApplied = False
        self.SendPrescription = 0

        self.fileRealIrrigAplication = (
            "/home/pi/Desktop/RealAgent/src/storage/RealIrrigationApplication.txt"
        )

        # estacion meteorlogica
        """consulta a estacion metereologica a las 00:00 todos los dias """
        self.apiServiceMet = ApiServiceEstacionMet(DatMet)
        self.schedWeatherSatation = BackgroundScheduler()
        self.schedWeatherSatation.add_job(
            self.apiServiceMet.checkStation, "cron", hour=23, minute=58
        )
        self.schedWeatherSatation.start()

        self.schedRebootAgent = BackgroundScheduler()
        self.schedRebootAgent.add_job(self.RebootAgent, "cron", hour=23, minute=50)
        self.schedRebootAgent.start()

        self.schedWeatherStation_2 = BackgroundScheduler()
        self.schedWeatherStation_2.add_job(self.Station_2, "cron", hour=23, minute=33)
        self.schedWeatherStation_2.start()

        """        
         self.schedPres_Aqucarop = BackgroundScheduler()
        self.schedPres_Aqucarop.add_job(self.Pres_Aquacrop, 'cron', hour = 0,  minute =1)
        self.schedPres_Aqucarop.start() 
        """

        self.schedWeatherStation_0m = BackgroundScheduler()
        self.schedWeatherStation_0m.add_job(self.Station_15m, "cron", minute=0)
        self.schedWeatherStation_0m.start()

        self.schedWeatherStation_15m = BackgroundScheduler()
        self.schedWeatherStation_15m.add_job(self.Station_15m, "cron", minute=15)
        self.schedWeatherStation_15m.start()

        self.schedWeatherStation_30m = BackgroundScheduler()
        self.schedWeatherStation_30m.add_job(self.Station_15m, "cron", minute=30)
        self.schedWeatherStation_30m.start()

        self.schedWeatherStation_45m = BackgroundScheduler()
        self.schedWeatherStation_45m.add_job(self.Station_15m, "cron", minute=45)
        self.schedWeatherStation_45m.start()

        self.Path_Data = "/home/pi/Desktop/RealAgent/src/storage"
        print("Aquacrop Init...")
        self.AquaCrop_os = AquaCrop_os()
        # modelo defaul del cultivo
        self.cropModel = Crop(
            "Maize", 20, 80, "Moisture_Sensor", 11, date(2020, 1, 1), "00:00", "00:00"
        )
        # modelo propiedades de riego
        self.IrrigProperties = irrigation_properties()

        print("-- firebase -- ")
        # conexion a firebase y actualizacion de datos
        self.FB = FIREBASE_CLASS(
            f"{self.groundDivision}_{self.agent}",
            self.cropModel,
            self.IrrigProperties,
        )
        # Modelo de sensores
        self.sensors = Sensors(self.cropModel.typeCrop, "0x000000000")
        print(f"niveles de sensores: { self.sensors._SensorsLevels}")
        # Modelo Resultados de prescripciones
        self.prescriptionResult = PrescriptionResults(
            "--",
            str(datetime.now()).split()[0],
            str(datetime.now()).split()[1],
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )  # resultados de prescripcion
        # modelo de metodos de prescripciones
        self.presc_Meth = prescriptionMethods(
            self.cropModel, self.sensors, self.prescriptionResult, self.apiServiceMet
        )  # inicializacion de metodos de prescripcion
        self.presc_Meth.Moisture_Sensor_Presc()
        """========Inicializacion de Protocolos de comunicacion ====="""
        self.Mqtt = MqttComunication(self.agent, self.groundDivision, self.AquaCrop_os)
        timedelay.sleep(5)

        print("---------XbeeCommunication --------------------")
        self.xbeeComm = XbeeCommunication(
            "/dev/ttyUSB0",
            9600,
            self.sensors,
            self.FB,
            self.agent,
            self.TimePrescription,
            self.IrrigAplied,
        )
        self.subproces_XbeeCallBack = Thread(target=self.xbeeComm.runCallback)
        self.subproces_XbeeCallBack.daemon = True
        self.subproces_XbeeCallBack.start()

        # print(sensor.allSensors)

    def realAgentPrescription(self):
        print("init program")
        self.todayMemory = date(2021, 3, 6)
        # self.todayMemory = date(datetime.now().year,datetime.now().month,datetime.now().day)

        while True:
            if self.FlagOrderIrrigSend == True:
                self.CurrentTime = datetime.now()
                self.duration_in_s = (
                    self.CurrentTime - self.HourSendIrrigOrder
                ).total_seconds()
                if self.duration_in_s >= self.TimePrescription:
                    self.xbeeComm.sendIrrigationOrder("SSTOPP;1;", self.agent)
                    self.xbeeComm.save_data_Xbee(
                        f"{self.Path_Data}/RegisterIrrigation.txt",
                        self.SendPrescription,
                    )
                    try:
                        self.FB.ResultIrrDoc_ref.update(
                            {"irrigationApplied": float(self.IrrigAplied)}
                        )
                    except:
                        print("error update data irrigationApplied")
                        print("Unexpected error:", sys.exc_info()[0])
                    self.FlagOrderIrrigSend = False
            else:
                pass

            self.today = date(
                datetime.now().year, datetime.now().month, datetime.now().day
            )
            if self.today != self.todayMemory:
                self.cropModel.dayscrop = abs(self.today - self.cropModel.seedTime).days
                self.contWeeks = int(self.cropModel.dayscrop / 7) + 1
                self.FB.CropDoc_ref.update({"DaysCrop": int(self.cropModel.dayscrop)})
                self.todayMemory = self.today
            else:
                pass

            self.horNouwStr = f"{datetime.now().hour}:{datetime.now().minute}"
            if self.horNouwStr == self.cropModel.presctime:
                if self.FlagPrescriptionDone == False:
                    self.ActualPrescription = self.getPrescriptionData(
                        self.cropModel.prescMode
                    )
                    try:
                        self.FB.ResultIrrDoc_ref.update(
                            {
                                "NetPrescription": self.ActualPrescription,
                                "LastPrescriptionDate": str(self.today),
                            }
                        )
                    except:
                        pass
                    print(f"Prescription= {self.ActualPrescription}")
                    self.FlagPrescriptionDone = True

            elif self.Mqtt.FlagPetition == True:
                if self.FlagPrescriptionDone == False:
                    self.ActualPrescription = self.getPrescriptionData(
                        self.cropModel.prescMode
                    )
                    print(f"Prescription= {self.ActualPrescription}")
                    try:
                        self.FB.ResultIrrDoc_ref.update(
                            {
                                "NetPrescription": self.ActualPrescription,
                                "LastPrescriptionDate": str(self.today),
                            }
                        )
                    except:
                        pass
                    self.FlagPrescriptionDone = True
                self.Report_Agent = self.AgentReport()
                self.Mqtt.client.publish(
                    f"Ag/{self.groundDivision}/Bloque_1/{self.agent}",
                    f"{self.Report_Agent}",
                    qos=2,
                )
                self.Mqtt.FlagPetition = False

            if self.FlagPrescriptionDone == True:

                if self.FlagirrigationAuthor == False:

                    if self.cropModel.negotiation == True:
                        if self.Mqtt.FlagIrrigation == True:
                            self.TotalPrescription = self.ActualPrescription
                            print(f"nuevo riego a aplicar {self.TotalPrescription }")
                            self.Mqtt.FlagIrrigation = False
                            self.FlagirrigationAuthor = True
                        elif self.Mqtt.FlagNewIrrigation == True:
                            self.TotalPrescription = self.Mqtt.NewPrescription  # mm
                            print(f"nuevo riego a aplicar {self.TotalPrescription }")
                            self.Mqtt.FlagNewIrrigation = False
                            self.FlagirrigationAuthor = True
                    else:
                        print("no negotiation ")
                        self.TotalPrescription = self.ActualPrescription
                        self.FlagirrigationAuthor = True

                else:
                    self.horNouwStr = f"{datetime.now().hour}:{datetime.now().minute}"
                    if (
                        self.horNouwStr == self.cropModel.firstIrrigationtime
                        or self.horNouwStr == self.cropModel.secondIrrigationtime
                    ):
                        if self.FlagTotalPrescApplied == False:
                            self.cropModel.firstIrrigationtime = (
                                "--:--"  # para evitar bucle infinito
                            )
                            self.cropModel.secondIrrigationtime = (
                                "--:--"  # para evitar bucle infinito
                            )
                            self.SendPrescription = self.TotalPrescription / 2
                            self.TimePrescription = self.calculationIrrigationTime(
                                self.IrrigProperties._drippers,
                                self.IrrigProperties._area,
                                self.IrrigProperties._efficiency,
                                self.IrrigProperties._nominalDischarge,
                                self.SendPrescription,
                            )
                            if self.TimePrescription > 0:
                                self.xbeeComm.sendIrrigationOrder(
                                    f"SITASK;1;{self.TimePrescription};", self.agent
                                )
                                self.FlagOrderIrrigSend = True
                                self.HourSendIrrigOrder = datetime.now()
                            else:
                                self.xbeeComm.save_data_Xbee(
                                    f"{self.Path_Data}/RegisterIrrigation.txt",
                                    self.SendPrescription,
                                )

                            self.IrrigAplied = self.IrrigAplied + self.SendPrescription

                            print(f"riego aplicado: {self.IrrigAplied}")
                            if self.IrrigAplied >= self.TotalPrescription:
                                self.FlagTotalPrescApplied = True
                                self.FlagPrescriptionDone = False
                                self.FlagirrigationAuthor = False
                                self.IrrigAplied = 0
                            try:
                                self.FB.ResultIrrDoc_ref.update(
                                    {"IrrigationState": "SENDORDER"}
                                )
                            except:
                                print("Error upload IrrigationState Send Order")

    def AgentReport(self):
        self.prescData = self.prescriptionResult.allDataPrescription
        LOTE, CROP_DEFAULT, STAR_DATE = (
            self.groundDivision,
            self.cropModel.typeCrop,
            self.cropModel.seedTime,
        )
        presc, Kc, Ks = (
            round(self.prescData[3], 3),
            round(self.prescData[5], 3),
            round(self.prescData[9], 3),
        )
        CONT_DAYS, CONT_WEEK, root_depth = (
            self.cropModel.dayscrop,
            self.contWeeks,
            round(self.prescData[7] * 1000, 3),
        )
        Taw, Mae, PRESC_MODE_send = (
            round(self.prescData[8], 3),
            round(self.prescData[9], 3),
            self.prescData[0].split("-")[0],
        )
        VWC, deple = round(self.sensors.allSensors[3], 3), round(self.prescData[4], 3)
        Report_Agent = f"{LOTE}{self.agent};{CROP_DEFAULT}.CRO;{str(STAR_DATE)};{presc};{Kc};{Ks};{CONT_DAYS};{CONT_WEEK};{root_depth};{Taw};{Mae};{PRESC_MODE_send};{VWC};{deple};1;{datetime.now()}"
        print(Report_Agent)
        return Report_Agent

    def getPrescriptionData(self, prescriptionMode):
        if prescriptionMode == "Moisture_Sensors":
            self.prescription = self.presc_Meth.Moisture_Sensor_Presc()
        elif prescriptionMode == "Weather_Station":
            self.prescription = self.presc_Meth.Weather_Station_presc(
                self.cropModel.dayscrop
            )
        elif prescriptionMode == "Better":
            print("Better Prescription wait ...")
            self.prescription = self.AquaCrop_os.Pres_Aquacrop()
            self.prescriptionResult.allDataPrescription = self.AquaCrop_os.return_data()

        else:
            self.prescription = 1
        return self.prescription

    def calculationIrrigationTime(
        self, drippers, area, efficiency, nominalDischarge, prescription
    ):
        self.timeMinutes = (
            (prescription * area) / (efficiency * drippers * nominalDischarge)
        ) * 60
        self.timeSeconds = self.timeMinutes * 60
        print(f"Timeirrig: {self.timeSeconds} s, {self.timeMinutes} minutes")
        return int(self.timeSeconds)

    def RebootAgent(self):
        if self.xbeeComm.numberCompletedOrders > 0:
            self.realIrrigAplication = (
                self.TotalPrescription / 2
            ) * self.xbeeComm.numberCompletedOrders
            if self.xbeeComm.numberReceivedOrders > self.xbeeComm.numberCompletedOrders:
                print("probable desperdicio de agua")
        else:
            self.realIrrigAplication = 0

        self.SaveFile = open(self.fileRealIrrigAplication, "a", errors="ignore")
        print(f"deficit {self.prescriptionResult.allDataPrescription[4]}")
        self.SaveFile.write(
            f"{str(datetime.now()).split()[0]},{str(datetime.now()).split()[1]},{self.TotalPrescription},{self.realIrrigAplication},{self.prescriptionResult.allDataPrescription[4]}\n"
        )
        self.SaveFile.close()
        self.FlagPrescriptionDone == True
        self.FlagTotalPrescApplied = True
        self.Mqtt.FlagIrrigation = False
        self.Mqtt.FlagNewIrrigation = False
        print("Agent ReStart...")

    def Station_2(self):
        os.system(
            "python3 /home/pi/Desktop/RealAgent/src/AquaCrop_OsPy/AquaCrop_OsPy/Station_2.py"
        )
        return

    def Station_15m(self):
        print("station_15m")
        os.system(
            "python3 /home/pi/Desktop/RealAgent/src/AquaCrop_OsPy/AquaCrop_OsPy/Station_15m.py"
        )
        os.system(
            "python3 /home/pi/Desktop/RealAgent/src/AquaCrop_OsPy/AquaCrop_OsPy/calculate_vwc.py"
        )
        return


if __name__ == "__main__":
    MainSystem = Main()
    timedelay.sleep(5)
    subproces_PrincF = Thread(target=MainSystem.realAgentPrescription())
    subproces_PrincF.daemon = True
    subproces_PrincF.start()
