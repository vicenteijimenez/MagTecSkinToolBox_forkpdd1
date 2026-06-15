#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun   9 10:02:37 2026

@author: stefan
"""

import gmsh
import Config
import Generation

# 1. Inicializar la configuración del modelo
MiConfig = Config.Config()
MiConfig.init_model_parameters()

# 2. Inicializar la API de Gmsh antes de llamar a cualquier función geométrica
gmsh.initialize()
gmsh.model.add("SensorFinger_Visualization")

# 3. Llamar a la función que genera la geometría del dedo
# Nota: Usamos Generation.createFinger o Generation.Finger. 
# Si quieres configurar mallas, se suele usar Generation.Finger.
FingerDimTag = Generation.createFinger(
    Length=MiConfig.Length, 
    Height=MiConfig.Height, 
    OuterRadius=MiConfig.OuterRadius, 
    TeethRadius=MiConfig.TeethRadius, 
    PlateauHeight=MiConfig.PlateauHeight, 
    JointHeight=MiConfig.JointHeight, 
    Thickness=MiConfig.Thickness, 
    JointSlopeAngle=MiConfig.JointSlopeAngle, 
    FixationWidth=MiConfig.FixationWidth, 
    BellowHeight=MiConfig.BellowHeight, 
    NBellows=MiConfig.NBellows, 
    WallThickness=MiConfig.WallThickness, 
    CenterThickness=MiConfig.CenterThickness, 
    CavityCorkThickness=MiConfig.CavityCorkThickness, 
    lc=MiConfig.lc_finger
)

# 4. Sincronizar el kernel de OpenCASCADE (OCC) con el modelo de Gmsh
gmsh.model.occ.synchronize()

# 5. Lanzar la interfaz gráfica interactiva (GUI) para visualizar el diseño
print("Abriendo la ventana de Gmsh... Cierra la ventana gráfica para terminar el script.")
gmsh.fltk.run()

# 6. Limpiar la memoria y cerrar la API de Gmsh de forma segura al salir de la GUI
gmsh.finalize()