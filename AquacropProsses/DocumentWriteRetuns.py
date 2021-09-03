class DocumentWriteRetuns:
    def __init__(self):
        pass

    def fileLocationDocument(self, inputPaht, OutputPaht):
        self.writeDocument = (
            "%% Enter Location of Input files %%\n"
            + f"{inputPaht}\n"
            + "%% Enter Location of Output files %%\n"
            + f"{OutputPaht}"
        )
        return self.writeDocument

    def ClokDocument(self, SimulationStart, SimulationEndTime):
        self.writeDocument = (
            "%% ---------- Clock parameter inputs for AquaCropOS ---------- %%\n"
            + "%% Simulation start time (yyyy-mm-dd) %%\n"
            + f"SimulationStartTime : { SimulationStart}\n"
            + "%% Simulation end time (yyyy-mm-dd) %%\n"
            + f"SimulationEndTime :   {SimulationEndTime}\n"
            + "%% Simulate off-season (N or Y) %%\n"
            + "OffSeason : N        \n"
        )
        return self.writeDocument

    def SoilDocument(self, zSoil):
        self.writeDocument = (
            "%% ---------- Soil parameter inputs for AquaCropOS ---------- %%\n"
            + "%% Soil profile filename %%\n"
            + "SoilProfile.txt\n"
            + "%% Soil textural properties filename %%\n"
            + "N/A\n"
            + "%% Soil hydraulic properties filename %%\n"
            + "SoilHydrology.txt\n"
            + "%% Calculate soil hydraulic properties (0: No, 1: Yes) %%\n"
            + "CalcSHP : 0\n"
            + "%% Total thickness of soil profile (m) %%\n"
            + f"zSoil :  {zSoil} \n"
            + "%% Total number of compartments %%\n"
            + "nComp : 12\n"
            + "%% Total number of layers %%\n"
            + "nLayer : 1\n"
            + "%% Thickness of soil surface skin evaporation layer (m) %%\n"
            + "EvapZsurf : 0.04\n"
            + "%% Minimum thickness of full soil surface evaporation layer (m) %%\n"
            + "EvapZmin : 0.15\n"
            + "%% Maximum thickness of full soil surface evaporation layer (m) %%\n"
            + "EvapZmax : 0.30\n"
            + "%% Maximum soil evaporation coefficient %%\n"
            + "Kex : 1.1\n"
            + "%% Shape factor describing reduction in soil evaporation %%\n"
            + "fevap : 4\n"
            + "%% Proportional value of Wrel at which soil evaporation layer expands %%\n"
            + "fWrelExp : 0.4\n"
            + "%% Maximum coefficient for soil evaporation reduction due to sheltering effect of withered canopy %%\n"
            + "fwcc : 50\n"
            + "%% Adjust default value for readily evaporable water (0: No, 1: Yes) %%\n"
            + "AdjREW : 0\n"
            + "%% Readily evaporable water (mm) (only used if adjusting) %%\n"
            + "REW : 9\n"
            + "%% Adjust curve number for antecedent moisture content (0:No, 1:Yes) %%\n"
            + "AdjCN : 1\n"
            + "%% Curve number %%\n"
            + "CN : 72\n"
            + "%% Thickness of soil surface (m) used to calculate water content to adjust curve number %%\n"
            + "zCN : 0.3\n"
            + "%% Thickness of soil surface (m) used to calculate water content for germination %%\n"
            + "zGerm : 0.3\n"
            + "%% Depth of restrictive soil layer (set to negative value if not present) %%\n"
            + "zRes : -999\n"
            + "%% Capillary rise shape factor %%\n"
            + "fshape_cr : 16\n"
        )
        return self.writeDocument

    def SoilHidrologyDocument(self, properties):
        self.writeDocument = (
            "%% ------------- Soil hydraulic properties for AquaCropOS -------------- %%\n"
            + "%%Layer    Thickness(m)    thS(m3/m3)    thFC(m3/m3)    thWP(m3/m3)    Ksat(mm/day)    %%\n"
            + f"{properties} \n"
        )
        return self.writeDocument

    def CropMixDocument(self, crop):
        self.writeDocument = (
            "%% ---------- Crop mix options for AquaCropOS ---------- %%\n"
            + "%% Number of crop options %%\n"
            + "1\n"
            + "%% Specified planting calendar %%\n"
            + "N\n"
            + "%% Crop rotation filename %%\n"
            + "CropRotation.txt\n"
            + "%% Information about each crop type %%\n"
            + "%% CropType, CropFilename, IrrigationFilename %%\n"
            + f"{crop}, Crop.txt, IrrigationManagement.txt\n"
        )
        return self.writeDocument

    def initialWaterContDocument(self):
        self.writeDocument = (
            "%% ---------- Initial soil water content for AquaCropOS ---------- %%\n"
            + "%% Type of value (Prop (i.e. WP/FC/SAT), Num (i.e. XXX m3/m3), Pct (i.e. % TAW)) %%\n"
            + "Prop\n"
            + "%% Method (Depth: Inteprolate depth points; Layer: Constant value for each soil layer) %%\n"
            + "Layer\n"
            + "%% Number of input points (NOTE: Must be at least one point per soil layer) %%\n"
            + "1\n"
            + "%% Input data points (Depth/Layer   Value) %%\n"
            + "1 FC\n"
        )
        return self.writeDocument