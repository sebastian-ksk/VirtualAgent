"""=====================================================================================================================
 En este scrpit se plante  la consulta de los dastos metereologicos del servidor a traves del metodo get de protocolo http. 
 Esta consulta se realiza a la base de datos de waterlink.
 NOTA:
 >> Es necesario contener un token privado que se obtiene del servidsor privado.
 ========================================================================================================================
"""
import sys
import requests
import json
import urllib
import sys
from datetime import datetime, timedelta
from datetime import date
import pandas as pd
import csv

from requests.models import Response


class ApiServiceEstacionMet:
    def __init__(self, modelWeather, directoryWheaterData):
        self.url = "https://api.weatherlink.com/v1/NoaaExt.json?user=001D0A0117A4&pass=multiagent&apiToken=6BA678C3A1844C6B9B9767F9543331A1"
        self.modelWeather = modelWeather
        self.directory = directoryWheaterData

    def request_station(self):
        try:
            self.payload = {}
            self.headers = {}
            self.response = requests.request(
                "GET", self.url, headers=self.headers, data=self.payload
            )
            return self.response.json()

        except:
            print("ERROR EN ADQUISICION DE DATOS")

    def checkStation(self):
        self.response = self.request_station()
        self.infoStation = self.modelWeather.from_dict(self.response)
        self.DataWheaterStationDF = pd.DataFrame()
        self.date = str(datetime.now()).split()[0]
        self.newLineData = [
            self.date,
            self.infoStation.TeMax,
            self.infoStation.TeMin,
            self.infoStation.EToD,
            self.infoStation.RainD,
        ]
        with open(self.directory, "a") as dataF:
            writer = csv.writer(dataF, delimiter="\t")
            writer.writerow(
                self.newLineData,
            )
        dataF.close()
        return self.infoStation
