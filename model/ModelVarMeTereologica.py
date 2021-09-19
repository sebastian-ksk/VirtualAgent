# modelo de la api que se consume para optener variables meteorologicas
from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast


@dataclass
class meteorologicalData:
    # did: str
    date: str
    hour: str
    EToD: float
    RainD: float
    TeMax: float
    TeMin: float
    Temp: float
    Hum: float

    @staticmethod
    def from_dict(obj: Any) -> "meteorologicalData":
        date = str(obj["observation_time"]).split(",")[0].split("on")[1]
        hour = str(obj["observation_time_rfc822"]).split(" ")[4]
        observation_davis = obj["davis_current_observation"]
        EToD = round(float(observation_davis["et_day"]) * 25.4, 2)
        RainD = round(float(observation_davis["rain_day_in"]) * 25.4, 2)
        TeMax = round((float(observation_davis["temp_day_high_f"]) - 32) * (5 / 9), 2)
        TeMin = round((float(observation_davis["temp_day_low_f"]) - 32) * (5 / 9), 2)
        Temp = round((float(observation_davis["temp_in_f"]) - 32) * (5 / 9), 2)
        Hum = round(float(observation_davis["relative_humidity_in"]), 2)
        return meteorologicalData(date, hour, EToD, RainD, TeMax, TeMin, Temp, Hum)
