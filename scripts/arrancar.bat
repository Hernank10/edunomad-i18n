@echo off
title Servidor - eduNomad (Puerto 8011)
color 0A

REM Redirigir TEMP al USB
set TMP=E:\tmp_pip
set TEMP=E:\tmp_pip
if not exist E:\tmp_pip mkdir E:\tmp_pip

REM Ir a la carpeta del proyecto
cd /d "E:\02_proyectos\eduNomad\_original"

REM Anadir la carpeta al sys.path (para PythonPortable)
set PYTHONPATH=E:\02_proyectos\eduNomad\_original

echo.
echo =======================================================
echo  Iniciando eduNomad
echo  URL: http://127.0.0.1:8011/
echo  Python: E:\PythonPortable\python.exe
echo =======================================================
echo.

REM Aplicar migraciones (por si acaso)
echo [1/2] Aplicando migraciones...
"E:\PythonPortable\python.exe" manage.py migrate --noinput
echo.

REM Abrir navegador y arrancar
echo [2/2] Arrancando servidor...
start "" http://127.0.0.1:8011/
"E:\PythonPortable\python.exe" manage.py runserver 127.0.0.1:8011

echo.
echo [!] El servidor se ha detenido.
pause
