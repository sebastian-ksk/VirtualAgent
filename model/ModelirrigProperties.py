class irrigation_properties:
    def __init__(self):
        self._drippers = 28 
        self._area = 19.5      #m^2
        self._efficiency = 0.9  
        self._nominalDischarge = 0.76 #[L/h]
        self.__AllProperties = [self._drippers,self._area,self._efficiency,self._nominalDischarge]

    @property
    def allDataIrrigProperties(self):
        return self.__AllProperties

    @allDataIrrigProperties.setter
    def allDataIrrigProperties(self,alldataProp):
        self.__AllProperties= alldataProp

