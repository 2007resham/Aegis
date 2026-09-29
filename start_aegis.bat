@echo off
cd /d "C:\project\_Cypher\Cypher\Aegis_main"
echo Starting at %date% %time% > startup_log.txt
call venv\Scripts\activate.bat >> startup_log.txt 2>&1
python -u main.py >> startup_log.txt 2>&1
echo Exited at %date% %time% >> startup_log.txt
pause