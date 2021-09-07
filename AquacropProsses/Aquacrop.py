import os
import pandas as pd
from datetime import datetime, timedelta, date
import subprocess, os
import math
import time
import os.path
from os import path, sep
import asyncio
import csv


class Aquacrop_os:
    def __init__(self, dataProperties, documentWriteReturns, parametersAQ):

        (
            self.crop,
            self.FieldCap_1,
            self.Pwp_1,
            self.FieldCap_2,
            self.Pwp_2,
            self.hidraulicCond,
            self.EndDaysCrop,
            self.seedDate,
            self.saturationPoint,
        ) = (
            parametersAQ["Crop"],
            parametersAQ["FCfirstLayer"],
            parametersAQ["PwpfirstLayer"],
            parametersAQ["FCsecondLayer"],
            parametersAQ["PwpsecondLayer"],
            parametersAQ["hidraulicConduc"],
            parametersAQ["EndDayscrop"],
            parametersAQ["SeedDate"],
            parametersAQ["SaturationPoint"],
        )

        print(f"seed date {self.seedDate}")
        print("Aquacrop OS init")
        self.parametersData = dataProperties
        self.DocumentsWrites = documentWriteReturns
        self.path_py = os.getcwd()
        self.outputDir = "/home/sebastianc/Desktop/VirtualAgent/AquacropProsses/AquacropResults/Lote"  # ruta donde se encuentra el lote
        self.path_AQ_os = (
            "/home/sebastianc/Desktop/VirtualAgent/AquacropProsses/AquaCropOS_v50a"
        )
        self.dir_weather = (
            "/home/sebastianc/Desktop/VirtualAgent/storage/WheatherStationData.csv"
        )
        self.dir_lote = self.outputDir

        """---------------------------Write document FileLocations.txt-------------------------"""
        self.FileLocationDir = f"{self.path_AQ_os}/FileLocations.txt"
        self.paragraphTowrite = self.DocumentsWrites.fileLocationDocument(
            inputPaht="home/sebastianc/Desktop/VirtualAgent/AquacropProsses/AquaCropOS_v50a/Input",
            OutputPaht="home/sebastianc/Desktop/VirtualAgent/AquacropProsses/AquaCropOS_v50a/Output",
        )
        self.FileLocationDoc = open(self.FileLocationDir, "w", errors="ignore")
        self.FileLocationDoc.write(self.paragraphTowrite)
        self.FileLocationDoc.close()
        """-----------------------------------------------------------------------------"""

        self.seedTime = datetime.strptime(self.seedDate, "%Y-%m-%d")
        if path.isfile(f"{self.outputDir}/VWC_pres2.csv"):
            print("dir exist")
        else:
            with open(
                f"{self.outputDir}/VWC_pres2.csv",
                "a",
            ) as dataF:
                writer = csv.writer(dataF, delimiter="\t")
                writer.writerow(
                    [
                        "Date",
                        "Tmax(C)",
                        "Tmin(C)",
                        "ET0",
                        "Rain(mm)",
                        "Irrigation(mm)",
                        "depl",
                        "ks",
                        "ETcadj",
                        "ETc",
                        "eff_rain",
                        "sp_crcoeff",
                        "sp_rootdepth",
                        "d_TAW",
                        "d_MAD",
                        "WC1",
                        "WC2",
                        "Total rain",
                        "Total irrigation",
                        "Yiel(ton/ha)",
                        "WUE (Kg/m3)",
                        "IWUE (Kg/m3)",
                        "Prescription(mm)",
                    ]
                )
                for i in range(self.EndDaysCrop + 1):
                    self.DatesCrop = [str(self.seedTime + timedelta(days=i)).split()[0]]
                    writer.writerow(
                        self.DatesCrop,
                    )

            dataF.close()

        """direcciones de edicion de datos para simulacion"""
        self.clockDirection = f"{self.path_AQ_os}/Input/Clock.txt"

        pass

    def EditClock(self, seedTime, endCropDays):

        self.seedTime = datetime.strptime(seedTime, "%Y-%m-%d")
        self.cropEndDay = self.seedTime + timedelta(days=endCropDays)
        # Escritura de datos de inicio de cultivo y final de cultivo
        self.directoryClock = open(self.clockDirection, "w", errors="ignore")
        # version 5
        self.paragraphTowrite = self.DocumentsWrites.ClokDocument(
            SimulationStart=str(self.seedTime).split()[0],
            SimulationEndTime=str(self.cropEndDay).split()[0],
        )
        self.directoryClock.write(self.paragraphTowrite)
        self.directoryClock.close()

    def EditWeatherInput(self, prescriptionMethod, daysPassed):
        self.TminAverage, self.TmaxAverage, self.ET0Average = 10, 20, 2.5
        # edita
        self.prescHistoryDF = pd.read_csv(
            f"{self.outputDir}/{prescriptionMethod}.csv", sep="\t"
        )
        self.writePrescDF = pd.DataFrame()
        self.writePrescDF = self.writePrescDF.fillna(0.0)

        self.prescHistoryDF["Date"] = pd.to_datetime(self.prescHistoryDF["Date"])

        self.writePrescDF["Day"] = self.prescHistoryDF["Date"].dt.day
        self.writePrescDF["Month"] = self.prescHistoryDF["Date"].dt.month
        self.writePrescDF["Year"] = self.prescHistoryDF["Date"].dt.year
        self.ceros = [0] * (len(self.prescHistoryDF) - daysPassed - 1)
        self.writePrescDF["Tmin(C)"] = (
            list(self.prescHistoryDF["Tmin(C)"][: daysPassed + 1]) + self.ceros
        )

        self.writePrescDF["Tmax(C)"] = (
            list(self.prescHistoryDF["Tmax(C)"][: daysPassed + 1]) + self.ceros
        )
        self.writePrescDF["Prcp(mm)"] = (
            list(self.prescHistoryDF["Rain(mm)"][: daysPassed + 1]) + self.ceros
        )
        self.writePrescDF["Et0(mm)"] = (
            list(self.prescHistoryDF["ET0"][: daysPassed + 1]) + self.ceros
        )
        # remplaza los valuees de cero por valuees promedio
        self.writePrescDF["Tmin(C)"] = self.writePrescDF["Tmin(C)"].replace(
            [0], [self.TminAverage]
        )
        self.writePrescDF["Tmax(C)"] = self.writePrescDF["Tmax(C)"].replace(
            [0], [self.TmaxAverage]
        )
        self.writePrescDF["Et0(mm)"] = self.writePrescDF["Et0(mm)"].replace(
            [0], [self.ET0Average]
        )
        # version 5
        self.writePrescDF.to_csv(
            f"{self.path_AQ_os}/Input/Weather.txt",
            header=False,
            sep="\t",
            float_format="%.2f",
            na_rep="0",
            index=False,
        )
        with open(f"{self.path_AQ_os}/Input/Weather.txt", "r", errors="ignore") as fin:
            data = fin.read().splitlines(True)
        self.weatherWrite = open(
            f"{self.path_AQ_os}/Input/Weather.txt", "w", errors="ignore"
        )
        self.weatherWrite.write(
            "%% ---------- Weather input time-series for AquaCropOS ---------- %%\n"
        )
        self.weatherWrite.write(
            "%% Day Month Year MinTemp MaxTemp Precipitation ReferenceET %%\n"
        )
        for line in data:
            self.weatherWrite.write(line)
        self.weatherWrite.close()

    def EditSoil(self, crop, Sat1010, fc1010, pwp1010, Ksat1010):

        self.root_max = self.parametersData.soilProp[crop]["root_max"]
        self.Dz = self.parametersData.soilProp[crop]["Dz"]
        self.paragraphTowrite = self.DocumentsWrites.SoilDocument(
            zSoil=self.root_max[4]
        )
        self.soilDir = self.path_AQ_os + "/Input/Soil.txt"
        self.soilDocument = open(self.soilDir, "w", errors="ignore")
        self.soilDocument.write(self.paragraphTowrite)
        self.soilDocument.close()
        self.hidrologyDir = self.path_AQ_os + "/Input/SoilHydrology.txt"
        self.hidrologyDoc = open(self.hidrologyDir, "w", errors="ignore")
        self.paragraphTowrite = self.DocumentsWrites.SoilHidrologyDocument(
            properties=(
                f"1\t\t{self.root_max[4]}\t\t{float(Sat1010) / 100}\t\t{float(fc1010) / 100}\t\t{float(pwp1010) / 100}\t\t{float(Ksat1010) * 240}"
            )
        )
        self.hidrologyDoc.write(self.paragraphTowrite)
        self.hidrologyDoc.close()

    def EditCropInput(self, crop, seedTime, endCropDays):
        # SEED_TIME='2015-05-01'
        self.seed_time = datetime.strptime(seedTime, "%Y-%m-%d")
        self.cropEndDate = self.seed_time + timedelta(days=endCropDays - 1)
        self.monthSeedTime = str(self.seed_time).split()[0].split("-")[1]
        self.daySeedTime = str(self.seed_time).split()[0].split("-")[2]
        self.monthEndDate = str(self.cropEndDate).split()[0].split("-")[1]
        self.dayEndDate = str(self.cropEndDate).split()[0].split("-")[2]
        """---------------------------Write document CropMix.txt-------------------------"""
        self.cropMixDir = f"{self.path_AQ_os}/Input/CropMix.txt"
        self.paragraphTowrite = self.DocumentsWrites.CropMixDocument(crop=crop)
        self.cropMixDoc = open(self.cropMixDir, "w", errors="ignore")
        self.cropMixDoc.write(self.paragraphTowrite)
        self.cropMixDoc.close()
        """-----------------------------------------------------------------------------"""
        """---------------------------Write document Crop.txt----------------------------"""
        self.cropDir = f"{self.path_AQ_os}/Input/Crop.txt"
        self.cropDoc = open(self.cropDir, "r", errors="ignore")
        self.readDocument = self.cropDoc.read().splitlines(True)

        for index, line in enumerate(self.readDocument):
            self.keyFind = str(line.split(":")[0]).strip()

            if self.keyFind in self.parametersData.dictPotato:

                if self.keyFind == "PlantingDate":

                    self.readDocument[
                        index
                    ] = f"PlantingDate : {self.daySeedTime}/{self.monthSeedTime}\n"
                elif self.keyFind == "HarvestDate":
                    self.readDocument[
                        index
                    ] = f"HarvestDate : {self.dayEndDate}/{self.monthEndDate}\n"
                else:
                    value = self.parametersData.dictPotato[self.keyFind]
                    self.readDocument[index] = f"{self.keyFind } : {value}  \n"
        self.cropDoc = open(self.cropDir, "w", errors="ignore")
        for line in self.readDocument:
            self.cropDoc.write(line)
        self.cropDoc.close()
        """-----------------------------------------------------------------------------"""
        """---------------------------Write document InitialWaterContent.txt------------"""
        self.waterContentDir = self.path_AQ_os + "/Input/InitialWaterContent.txt"
        self.waterContentDoc = open(self.waterContentDir, "w", errors="ignore")
        self.paragraphTowrite = self.DocumentsWrites.initialWaterContDocument()
        self.waterContentDoc.write(self.paragraphTowrite)
        self.waterContentDoc.close()
        """-----------------------------------------------------------------------------"""

    def Edit_Irr(self, prescriptionMethod, endCropDays):
        """---------------------write document IrrigationManagement----------------------"""
        self.IrrManagementDir = self.path_AQ_os + "/Input/IrrigationManagement.txt"
        self.IrrManagementDoc = open(self.IrrManagementDir, "r", errors="ignore")
        self.readDocument = self.IrrManagementDoc.read().splitlines(True)

        for index, line in enumerate(self.readDocument):
            self.keyFind = str(line.split(":")[0]).strip()
            if self.keyFind in self.parametersData.IrrMagnamentProp:
                self.readDocument[
                    index
                ] = f"{self.keyFind} : {self.parametersData.IrrMagnamentProp[self.keyFind]} \n"

        self.IrrManagementDoc = open(self.IrrManagementDir, "w", errors="ignore")
        for line in self.readDocument:
            self.IrrManagementDoc.write(line)
        self.IrrManagementDoc.close()
        """-----------------------------------------------------------------------------"""
        """---------------------write document IrrigationSchedule----------------------"""
        ##edita el riego
        self.IrrHistoryDF = pd.read_csv(
            f"{self.outputDir}/{prescriptionMethod}.csv", sep="\t"
        )
        self.IrrHisttoWriteDF = pd.DataFrame()
        self.IrrHisttoWriteDF = self.IrrHisttoWriteDF.fillna(0)

        self.IrrHistoryDF["Date"] = pd.to_datetime(self.IrrHistoryDF["Date"])
        self.IrrHisttoWriteDF["Day"] = self.IrrHistoryDF["Date"][:endCropDays].dt.day
        self.IrrHisttoWriteDF["Month"] = self.IrrHistoryDF["Date"][
            :endCropDays
        ].dt.month
        self.IrrHisttoWriteDF["Year"] = self.prescHistoryDF["Date"][
            :endCropDays
        ].dt.year
        self.IrrHisttoWriteDF["Depth"] = self.IrrHistoryDF["Irrigation(mm)"][
            :endCropDays
        ]

        self.IrrScheduleDir = f"{self.path_AQ_os}/Input/IrrigationSchedule.txt"
        # Escribe en el ocumento solo el dataFrame
        self.IrrHisttoWriteDF.to_csv(
            self.IrrScheduleDir,
            header=False,
            sep="\t",
            float_format="%.2f",
            na_rep="0",
            index=False,
        )
        self.IrrScheduleDoc = open(self.IrrScheduleDir, "r", errors="ignore")
        self.readDocument = self.IrrScheduleDoc.read().splitlines(True)
        self.IrrScheduleDoc = open(self.IrrScheduleDir, "w", errors="ignore")
        self.IrrScheduleDoc.write(
            "%% -------- Irrigation schedule time-series for AquaCropOS -------- %%\n"
            + "%% Day Month Year Irrigation(mm) %%\n"
        )
        for line in self.readDocument:
            self.IrrScheduleDoc.write(line)
        self.IrrScheduleDoc.close()
        """-----------------------------------------------------------------------------"""

    async def RunModel(self):
        os.chdir(self.path_AQ_os)

        # self.processAQ = await asyncio.create_subprocess_exec(
        #     "octave",
        #     "AquaCropOS_RUN.m",
        #     stdout=asyncio.subprocess.PIPE,
        #     stderr=asyncio.subprocess.STDOUT,
        # )
        # data = await self.processAQ.stdout.readline()
        # line = data.decode("ascii").rstrip()
        # # Wait for the subprocess exit.
        # await self.processAQ.wait()

        # os.chdir(self.path_py)
        # print(data)
        # print(line)
        # time.sleep(5)

        p = subprocess.run(
            ["octave", "AquaCropOS_RUN.m"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        os.chdir(self.path_py)
        print(p)
        time.sleep(5)

        self.CropGrowth = pd.read_csv(
            self.path_AQ_os + "/Output/Sample_CropGrowth.txt", sep="\t"
        )
        self.FinalOutput = pd.read_csv(
            self.path_AQ_os + "/Output/Sample_FinalOutput.txt", sep="\t"
        )
        self.WaterContents = CropGrowth = pd.read_csv(
            self.path_AQ_os + "/Output/Sample_WaterContents.txt", sep="\t"
        )
        self.WaterFluxes = CropGrowth = pd.read_csv(
            self.path_AQ_os + "/Output/Sample_WaterFluxes.txt", sep="\t"
        )

        return self.WaterFluxes, self.CropGrowth, self.FinalOutput, self.WaterContents

    def main(self):

        self.today = datetime.strptime(str(datetime.now()).split()[0], "%Y-%m-%d")
        self.seedTime = datetime.strptime(self.seedDate, "%Y-%m-%d")
        self.dayscrop = abs(self.today - self.seedTime).days
        print(f"days {self.dayscrop}")
        print("edit clock ...")
        self.EditClock(self.seedDate, self.EndDaysCrop)
        print("edit wheater ...")
        self.EditWeatherInput("VWC_pres2", self.dayscrop)
        self.EditSoil(
            self.crop,
            self.saturationPoint,
            self.FieldCap_1,
            self.Pwp_1,
            self.hidraulicCond,
        )
        print("edit Crop")
        self.EditCropInput(self.crop, self.seedDate, self.EndDaysCrop)
        print("edit Irrig")
        self.Edit_Irr("VWC_pres2", self.EndDaysCrop)

        print("init aquacrop")
        (
            self.WaterFluxes,
            self.CropGrowth,
            self.FinalOutput,
            self.WaterContents,
        ) = asyncio.run(self.RunModel())
        self.FinalYield = float(self.FinalOutput.at[0, "Yield"])

        print("end aquacrop")
        return self.FinalYield
