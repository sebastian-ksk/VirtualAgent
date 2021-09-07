from datetime import datetime, date, time, timedelta


class PrescriptionResults:
    def __init__(
        self,
        PrescriptionMethod,
        date,
        hour,
        irr_pres_net,
        deficit,
        Kc,
        sp_rootdepth,
        dTaw,
        mad,
        Ks,
        ETcadj,
        eff_rain,
        ETc,
    ):
        self._PrescriptionMethod = PrescriptionMethod
        self._date = date
        self._hour = hour
        self._irr_pres_net = irr_pres_net
        self._deficit = deficit
        self._Kc = Kc
        self._sp_rootdepth = sp_rootdepth
        self._dTaw = dTaw
        self._mad = mad
        self._Ks = Ks
        self._ETcadj = ETcadj
        self._eff_rain = eff_rain
        self._ETc = ETc
        self.__allDataPrescription = [
            self._PrescriptionMethod,  # 0
            self._date,  # 1
            self._hour,  # 2
            self._irr_pres_net,  # 3
            self._deficit,  # 4
            self._Kc,  # 5
            self._sp_rootdepth,  # 6
            self._dTaw,  # 7
            self._mad,  # 8
            self._Ks,  # 9
            self._ETcadj,  # 10
            self._eff_rain,  # 11
            self._ETc,  # 12
        ]

    @property
    def allDataPrescription(self):
        return self.__allDataPrescription

    @allDataPrescription.setter
    def allDataPrescription(self, alldataPrescription):
        self.__allDataPrescription = alldataPrescription
