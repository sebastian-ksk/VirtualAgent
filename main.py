# created by: sebastian castellanos
from data.ApiServiceEstacionMet import ApiServiceEstacionMet
from data.FireBase import FIREBASE_CLASS
from model.ModelVarMeTereologica import meteorologicalData as DatMet
from model.ModelCultivo import Crop
from model.ModelSensores import Sensors
from model.ModelirrigProperties import irrigation_properties
from model.ModelPrescriptionResult import PrescriptionResults
from services.mqttComunication import MqttComunication
from services.PrescriptionMethods import prescriptionMethods
from AquacropProsses.DataProperties import DataProperties
from AquacropProsses.DocumentWriteRetuns import DocumentWriteRetuns
from AquacropProsses.Aquacrop import Aquacrop_os
from model.AquacropParameters import ParametersAquacrop
from util.DocumentsCreate import DocumentsCreate

"""
librerias externas al sistema 
"""
import signal
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date, time, timedelta  # para fechas y hora
import time as timedelay  # para cronometrar tiempo
from threading import Thread

import sys, os

print(sys.path)
import requests
import json
import urllib
import json
import pandas as pd


class Main:
    def __init__(self):
        super(Main, self).__init__()
        """inicializacion de datos"""
        print("init data")
        self.nameUser = "sebastiancastell371"
        self.groundDivision = "Tibasosa"  # esatacion de Bombeo
        self.agent = 1

        self.pahtHistoricalData = f"/home/sebastianc/Desktop/VirtualAgent/storage/{self.groundDivision}{self.agent}_HistorycalData.csv"
        self.dirDataWheaterStation = f"/home/sebastianc/Desktop/VirtualAgent/storage/{self.groundDivision}{self.agent}_WheatherStation.csv"

        # self.agent = int(input("ingrese el numero del agente : "))
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
        self.count = 10
        # modelo defaul del cultivo
        self.cropModel = Crop(
            "Maize", 20, 80, "Moisture_Sensor", 11, date(2020, 1, 1), "00:00", "00:00"
        )
        # modelo propiedades de riego
        self.IrrigProperties = irrigation_properties()

        # Modelo de sensores
        self.sensors = Sensors(self.cropModel.typeCrop, "0x000000000")
        self.sensors.allSensors = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        print("-- firebase -- ")
        # conexion a firebase y actualizacion de datos
        self.FirebaseName = f"sebastiancastell371.{self.groundDivision}_{self.agent}"
        self.FB = FIREBASE_CLASS(
            self.FirebaseName,
            self.cropModel,
            self.IrrigProperties,
        )

        DocumentsCreate(
            HistoryDocument=self.pahtHistoricalData,
            MeteDataDocument=self.dirDataWheaterStation,
            seedDate=str(self.cropModel.seedTime),
            endDaysCrop=121,
        )  # creacion de documentos

        # estacion meteorlogica
        """consulta a estacion metereologica a las 00:00 todos los dias """
        self.apiServiceMet = ApiServiceEstacionMet(DatMet, self.dirDataWheaterStation)
        self.schedSimSensors = BackgroundScheduler()
        self.schedSimSensors.configure(timezone="utc")
        self.schedSimSensors.add_job(
            self.simulationMoistureSensors,
            "cron",
            day_of_week="1-6",
            hour="*",
            minute="1,15,30,45",
        )
        self.schedSimSensors.start()
        self.schedRebootAgent = BackgroundScheduler()
        self.schedRebootAgent.add_job(self.RebootAgent, "cron", hour=23, minute=55)
        self.schedRebootAgent.start()
        print("Aquacrop Init...")
        self.parametersAQ = ParametersAquacrop(
            crop=self.cropModel.typeCrop,
            fc1=self.cropModel.FieldCap,
            pwp1=self.cropModel.pointWp,
            fc2=self.cropModel.FieldCap - 1.7,
            pwp2=self.cropModel.pointWp - 0.5,
            saturationPoint=self.cropModel.FieldCap + 10,
            layer1=0.1,
            layer2=0.1,
            hidraulic_conduc=1.07,
            seedDate=str(self.cropModel.seedTime),
            daysCrop=121,
        )

        self.AquaCrop_os = Aquacrop_os(
            DataProperties(),
            DocumentWriteRetuns(),
            self.parametersAQ.parameters,
            self.pahtHistoricalData,
            self.dirDataWheaterStation,
        )

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
        )
        self.presc_Meth = prescriptionMethods(
            self.cropModel,
            self.sensors,
            self.prescriptionResult,
            self.apiServiceMet,
            self.pahtHistoricalData,
            self.dirDataWheaterStation,
        )  # inicializacion de metodos de prescripcion
        self.presc_Meth.Moisture_Sensor_Presc()
        """========Inicializacion de Protocolos de comunicacion ====="""
        self.Mqtt = MqttComunication(self.agent, self.groundDivision, self.AquaCrop_os)
        timedelay.sleep(5)

    def AgentPrescription(self):
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
                    try:
                        self.FB.ResultIrrDoc_ref.update(
                            {
                                "irrigationApplied": float(self.IrrigAplied),
                                "IrrigationTime": self.TimePrescription * 60,
                                "IrrigationState": "OFF",
                                "LastIrrigationDate": str(self.today),
                            }
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
                                "NetPrescription": round(self.ActualPrescription, 2),
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
                                "prescriptionDone": "true",
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

                            if self.horNouwStr == self.cropModel.firstIrrigationtime:
                                self.cropModel.firstIrrigationtime = (
                                    "--:--"  # para evitar bucle infinito
                                )
                                print("first irrigation")
                            else:
                                self.cropModel.secondIrrigationtime = (
                                    "--:--"  # para evitar bucle infinito
                                )
                                print("second irrigation")

                            self.SendPrescription = self.TotalPrescription / 2
                            self.TimePrescription = self.calculationIrrigationTime(
                                self.IrrigProperties._drippers,
                                self.IrrigProperties._area,
                                self.IrrigProperties._efficiency,
                                self.IrrigProperties._nominalDischarge,
                                self.SendPrescription,
                            )
                            if self.TimePrescription > 0:
                                self.FlagOrderIrrigSend = True
                                self.HourSendIrrigOrder = datetime.now()
                                try:
                                    self.FB.ResultIrrDoc_ref.update(
                                        {"IrrigationState": "ON"}
                                    )
                                except:
                                    print("Error upload IrrigationState Send Order")

                            else:
                                try:
                                    self.FB.ResultIrrDoc_ref.update(
                                        {
                                            "irrigationApplied": 0,
                                            "IrrigationTime": 0,
                                            "IrrigationState": "OFF",
                                            "LastIrrigationDate": str(self.today),
                                        }
                                    )
                                except:
                                    print("Error upload IrrigationState Send Order")

                            self.IrrigAplied = self.IrrigAplied + self.SendPrescription
                            print(f"riego aplicado: {self.IrrigAplied}")
                            if self.IrrigAplied >= self.TotalPrescription:
                                self.FlagTotalPrescApplied = True
                                self.FlagPrescriptionDone = False
                                self.FlagirrigationAuthor = False
                                self.IrrigAplied = 0

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
        self.dailysimulation()
        self.FlagPrescriptionDone == True
        self.FlagTotalPrescApplied = True
        self.Mqtt.FlagIrrigation = False
        self.Mqtt.FlagNewIrrigation = False
        self.count = 10
        print("Agent ReStart...")

    def dailysimulation(self):

        self.meteoData = self.apiServiceMet.checkStation()
        self.prescHistoryDF = pd.read_csv(f"{self.pahtHistoricalData}", sep="\t")
        self.HistDF = self.prescHistoryDF.set_index(self.prescHistoryDF["Date"])
        self.prescData = self.prescriptionResult.allDataPrescription
        self.depletion, self.Kc, self.Ks = (
            round(self.prescData[4], 2),
            round(self.prescData[5], 2),
            round(self.prescData[9], 2),
        )
        self.ETcadj, self.ETc, self.root_depth = (
            round(self.prescData[10], 2),
            round(self.prescData[12], 2),
            round(self.prescData[6] * 1000, 2),
        )
        self.effRain, self.dTaw, self.mad = (
            round(self.prescData[11], 2),
            round(self.prescData[7], 2),
            round(self.prescData[8] * 1000, 2),
        )
        self.presc, self.VWC1, self.VWC2 = (
            round(self.sensors.allSensors[3], 3),
            round(self.sensors.allSensors[4], 3),
            round(self.prescData[3], 3),
        )
        self.todayr = str(
            datetime.strptime(str(datetime.now()).split()[0], "%Y-%m-%d")
        ).split()[0]
        self.yesterdayr = str(
            datetime.strptime(
                str(datetime.now() - timedelta(days=1)).split()[0], "%Y-%m-%d"
            )
        ).split()[0]

        if str(self.cropModel.seedTime).strip() == str(self.todayr).strip():
            self.totalRain, self.totalIrr = self.meteoData.RainD, self.IrrigAplied
        else:
            self.totalRain = (
                float(self.HistDF.at[self.yesterdayr, "Total rain"])
                + self.meteoData.RainD
            )
            self.totalIrr = (
                float(self.HistDF.at[self.yesterdayr, "Total irrigation"])
                + self.IrrigAplied
            )
        print(f"Hoy es {self.todayr}")
        self.HistDF.at[self.todayr, "Tmin(C)"] = self.meteoData.TeMin
        self.HistDF.at[self.todayr, "Tmax(C)"] = self.meteoData.TeMax
        self.HistDF.at[self.todayr, "ET0"] = self.meteoData.EToD
        self.HistDF.at[self.todayr, "Rain(mm)"] = self.meteoData.RainD
        self.HistDF.at[self.todayr, "Irrigation(mm)"] = self.IrrigAplied
        self.HistDF.at[self.todayr, "depl"] = self.depletion
        self.HistDF.at[self.todayr, "ks"] = self.Ks
        self.HistDF.at[self.todayr, "sp_crcoeff"] = self.Kc
        self.HistDF.at[self.todayr, "ETcadj"] = self.ETcadj
        self.HistDF.at[self.todayr, "ETc"] = self.ETc
        self.HistDF.at[self.todayr, "eff_rain"] = self.effRain
        self.HistDF.at[self.todayr, "sp_rootdepth"] = self.root_depth
        self.HistDF.at[self.todayr, "d_TAW"] = self.dTaw
        self.HistDF.at[self.todayr, "d_MAD"] = self.mad
        self.HistDF.at[self.todayr, "WC1"] = self.VWC1
        self.HistDF.at[self.todayr, "WC2"] = self.VWC2
        self.HistDF.at[self.todayr, "Total rain"] = self.totalRain
        self.HistDF.at[self.todayr, "Total irrigation"] = self.totalIrr
        self.HistDF.at[self.todayr, "Prescription(mm)"] = self.presc

        self.HistDF.to_csv(
            f"{self.pahtHistoricalData}",
            index=False,
            sep="\t",
            float_format="%.2f",
        )
        self.finalYield = self.AquaCrop_os.main()
        if self.totalIrr != 0:
            self.wue = (self.finalYield / self.totalIrr) * 1000
            self.Iwue = (self.finalYield / (self.totalIrr + self.totalRain)) * 1000
        else:
            self.wue, self.Iwue = 0, 0

        self.HistDF.at[self.todayr, "Yiel(ton/ha)"] = self.finalYield
        self.HistDF.at[self.todayr, "WUE (Kg/m3)"] = self.wue
        self.HistDF.at[self.todayr, "IWUE (Kg/m3)"] = self.Iwue

        self.HistDF.to_csv(
            f"{self.pahtHistoricalData}",
            index=False,
            sep="\t",
            float_format="%.2f",
        )

    def simulationMoistureSensors(self):

        self.todaym = str(
            datetime.strptime(str(datetime.now()).split()[0], "%Y-%m-%d")
        ).split()[0]
        self.dataMeteH = pd.read_csv(
            f"{self.dirDataWheaterStation}",
            sep="\t",
        )
        self.Metdf = self.dataMeteH.set_index(self.dataMeteH["Date"])

        self.ETot_1, self.Raint_1 = (
            float(self.Metdf.at[f"{self.todaym}", "ET0"]),
            float(self.Metdf.at[f"{self.todaym}", "Rain(mm)"]),
        )
        print(f"et = {self.ETot_1}")
        self.meteoData = self.apiServiceMet.checkStation()
        self.Etot, self.Raint = self.meteoData.EToD, self.meteoData.RainD
        self.difRain, self.difEto = (
            (self.Raint - self.Raint_1),
            (self.Etot - self.ETot_1),
        )

        print(f"dif Rain {self.difRain}")
        print(f"dif Rain {self.difEto}")

        self.prescHistoryDF = pd.read_csv(
            self.pahtHistoricalData,
            sep="\t",
        )
        self.dataCropdf = self.prescHistoryDF.set_index(self.prescHistoryDF["Date"])
        self.Kc = float(self.dataCropdf.at[f"{self.todaym}", "sp_crcoeff"])

        self.vwc_1 = round(
            (
                self.sensors.allSensors[0] * (150 / 100)
                + self.difRain
                + self.IrrigAplied
                - self.difEto * float(self.Kc)
            )
            * (100 / 150),
            2,
        )
        print(f"vwc ={self.vwc_1}")
        if self.vwc_1 > 60:
            self.vwc_1 = 60
        elif self.vwc_1 < 0:
            self.vwc_1 = 0.0

        self.vwc_2 = round(self.vwc_1 * (250 / 150), 2)
        self.sensors.allSensors[0] = self.vwc_1
        self.sensors.allSensors[1] = self.vwc_2
        self.sensors.allSensors[4] = self.meteoData.Temp
        self.sensors.allSensors[5] = self.meteoData.Hum
        self.firebaseSensors()

    def firebaseSensors(self):
        self.today = date(datetime.now().year, datetime.now().month, datetime.now().day)
        print(str(self.today))
        self.hourUp = ""
        self.minUp = ""
        self.countUp = ""
        if datetime.now().hour < 10:
            self.hourUp = f"0{datetime.now().hour}"
        else:
            self.hourUp = f"{datetime.now().hour}"
        if datetime.now().minute < 10:
            self.minUp = f"0{datetime.now().minute}"
        else:
            self.minUp = f"{datetime.now().minute}"

        if self.count < 10:
            self.countUp = f"0{self.count}"
        else:
            self.countUp = f"{self.count}"

        self.FB.SensorsDoc_ref.update(
            {
                ""
                + f"{str(self.today)}.{self.countUp}": {
                    "Hour": f"{self.hourUp}:{self.minUp}",
                    "VWC1": self.sensors.allSensors[0],
                    "VWC2": self.sensors.allSensors[1],
                    "VWC3": self.sensors.allSensors[2],
                    "VWC4": self.sensors.allSensors[3],
                    "temperature": self.sensors.allSensors[4],
                    "RH": self.sensors.allSensors[5],
                    "soilTemperature": self.sensors.allSensors[6],
                    "CanopyTemperature": self.sensors.allSensors[7],
                    "CanopyTemperatureAmb": self.sensors.allSensors[8],
                },
            }
        )
        self.count += 1


if __name__ == "__main__":
    MainSystem = Main()
    # MainSystem.RebootAgent()
    # MainSystem.simulationMoistureSensors()
    # MainSystem.AquaCrop_os.main()

    timedelay.sleep(5)
    subproces_PrincF = Thread(target=MainSystem.AgentPrescription())
    subproces_PrincF.daemon = True
    subproces_PrincF.start()
