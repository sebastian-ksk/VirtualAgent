class DataProperties:
    def __init__(self):
        self.soilProperties = {
            "Maize": {
                "root_max": [0.23, 0.46, 0.69, 0.92, 2.30],
                "Dz": [0.23, 0.23, 0.23, 0.23, 1.38],
            },
            "Potato": {
                "root_max": [0.15, 0.30, 0.45, 0.61, 1.50],
                "Dz": [0.15, 0.15, 0.15, 0.15, 0.90],
            },
            "Tomato": {
                "root_max": [0.15, 0.30, 0.45, 0.60, 1.00],
                "Dz": [0.15, 0.15, 0.15, 0.14, 0.40],
            },
            "Wheat": {
                "root_max": [0.26, 0.52, 0.78, 1.04, 1.50],
                "Dz": [0.26, 0.26, 0.26, 0.26, 0.46],
            },
            "Barley": {
                "root_max": [0.25, 0.50, 0.75, 1.0, 1.30],
                "Dz": [0.25, 0.25, 0.25, 0.25, 0.30],
            },
            "Quinoa": {
                "root_max": [0.23, 0.46, 0.69, 0.92, 1.00],
                "Dz": [0.23, 0.23, 0.23, 0.23, 0.08],
            },
            "Onion": {
                "root_max": [0.10, 0.20, 0.20, 0.20, 0.20],
                "Dz": [0.10, 0.10, 0.0, 0.00, 0.00],
            },
        }
        # days, crop_cofficient, root_depth
        self.Corn = [25, 37, 40, 30, 0.30, 1.2, 0.5, 0, 0.4572]
        self.Potato = [25, 30, 36, 30, 0.5, 1.15, 0.75, 0, 0.3048]
        self.Tomato = [25, 30, 30, 25, 0.60, 1.15, 0.8, 0.04, 0.3048]
        self.Barley = [40, 60, 60, 40, 0.30, 1.15, 0.25, 0, 0.498]
        self.Wheat = [40, 60, 60, 37, 0.30, 1.15, 0.4, 0, 0.519]
        self.Quinoa = [25, 60, 60, 35, 0.30, 1.2, 0.5, 0, 0.4645]
        self.Onion = [21, 42, 49, 38, 0.40, 0.85, 0.35, 0.04, 0.165]

        self.dicIrrManagement = {
            "IrrMethod": 3,
            "SMT1": 75,
            "SMT2": 75,
            "SMT3": 75,
            "SMT4": 75,
            "AppEff": 90,
            "WetSurf": 100,
        }

        self.Para_Potato = {
            "CropType": "2",
            "CalendarType": "1",
            "SwitchGDD": "0",
            "PlantingDate": "01/03",
            "HarvestDate": "01/08",
            "Emergence": "15",
            "MaxRooting": "50",
            "Senescence": "105",
            "Maturity": "125",
            "HIstart": "46",
            "Flowering": "-999",
            "YldForm": "77",
            "GDDmethod": "3",
            "Tbase": "2",
            "Tupp": "26",
            "PolHeatStress": "0",
            "Tmax_up": "-999",
            "Tmax_lo": "-999",
            "PolColdStress": "0",
            "Tmin_up": "-999",
            "Tmin_lo": "-999",
            "BioTempStress": "0",
            "GDD_up": "7",
            "GDD_lo": "0",
            "fshape_b": "13.8135",
            "PctZmin": "70",
            "Zmin": "0.3",
            "Zmax": "0.6",
            "fshape_r": "1.5",
            "fshape_ex": "-6",
            "SxTopQ": "0.048",
            "SxBotQ": "0.012",
            "a_Tr": "1",
            "SeedSize": "15",
            "PlantPop": "40000",
            "CCmin": "0.05",
            "CCx": "0.92",
            "CDC": "0.01884",
            "CGC": "0.126",
            "Kcb": "1.1",
            "fage": "0.15",
            "WP": "18",
            "WPy": "100",
            "fsink": "0.5",
            "bsted": "0.000138",
            "bface": "0.001165",
            "HI0": "0.85",
            "HIini": "0.01",
            "dHI_pre": "2",
            "a_HI": "0",
            "b_HI": "10",
            "dHI0": "5",
            "Determinant": "0",
            "exc": "0",
            "MaxFlowPct": "33.33",
            "p_up1": "0.2",
            "p_up2": "0.6",
            "p_up3": "0.7",
            "p_up4": "0.8",
            "p_lo1": "0.6",
            "p_lo2": "1",
            "p_lo3": "1",
            "p_lo4": "1",
            "fshape_w1": "3",
            "fshape_w2": "3",
            "fshape_w3": "3",
            "fshape_w4": "0",
            "ETadj": "1",
            "Aer": "5",
            "LagAer": "3",
            "beta": "12",
            "GermThr": "0.2",
            "GermThr": "0.2",
        }
        self.dic_parameters = {
            "CODE": "Tibasosa1",
            "LAT": "5.78291",
            "LON": "-73.1047",
            "AREA": "7841.31",
            "CLAY": "26.72",
            "SILT": "54.61",
            "SAND": "18.19",
            "SP": "58.95",
            "FC1010": "46.373",
            "PWP1010": "26.013",
            "HC": "1.07",
            "DENSITY": "1.14",
            "TYPE SOIL": "SiltLoam",
            "CROP": "Potato.CRO",
            "MODEL": "BETTER",
            "SEEDTIME": "44261",
            "DAYS_CROP": "121",
            "PRESCRIPTION": "0",
            "Ks": "0",
            "DAY_START": "0",
            "WEEK": "0",
            "Kc": "NaN",
            "root depth": "NaN",
            "TAW": "NaN",
            "MAE": "NaN",
            "L1": "0.1",
            "L2": "0.1",
            "FC1020": "45.737",
            "PWP1020": "25.47",
        }

    @property
    def IrrMagnamentProp(self):
        return self.dicIrrManagement

    @property
    def soilProp(self):
        return self.soilProperties

    @property
    def dictPotato(self):
        return self.Para_Potato

    @property
    def initialParameters(self):
        return self.dic_parameters

    # rutas agente real
