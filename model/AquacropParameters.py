class ParametersAquacrop:
    __parametersAQ = {}

    def __init__(
        self,
        crop,
        fc1,
        pwp1,
        fc2,
        pwp2,
        layer1,
        layer2,
        hidraulic_conduc,
        daysCrop,
        seedDate,
        saturationPoint,
    ):
        self.__parametersAQ = {
            "Crop": crop,
            "FCfirstLayer": fc1,
            "FCsecondLayer": fc2,
            "PwpfirstLayer": pwp1,
            "PwpsecondLayer": pwp2,
            "FirstLayer": layer1,
            "SecondLayer": layer2,
            "hidraulicConduc": hidraulic_conduc,
            "EndDayscrop": daysCrop,
            "SeedDate": seedDate,
            "SaturationPoint": saturationPoint,
        }

    @property
    def parameters(self):
        return self.__parametersAQ