@echo off
REM Script de demarrage du serveur Django avec GDAL/GEOS configure

REM Configuration QGIS/GDAL (mettre en PREMIER dans le PATH pour eviter conflits)
SET OSGEO4W_ROOT=C:\Program Files\QGIS 3.40.7
SET PATH=%OSGEO4W_ROOT%\bin;%PATH%

REM Variables d'environnement critiques pour PROJ/GDAL
SET PROJ_LIB=%OSGEO4W_ROOT%\share\proj
SET GDAL_DATA=%OSGEO4W_ROOT%\share\gdal
SET GDAL_DRIVER_PATH=%OSGEO4W_ROOT%\bin\gdalplugins

REM IMPORTANT: Desactiver la base PROJ de PostgreSQL
SET PROJ_NETWORK=OFF

REM Activer le virtualenv et demarrer le serveur
call venv\Scripts\activate.bat

REM Utiliser explicitement le Python du venv pour eviter les conflits
venv\Scripts\python.exe manage.py runserver

pause
