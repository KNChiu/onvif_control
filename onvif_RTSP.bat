ECHO ON
call C:\ProgramData\Miniconda3\Scripts\activate.bat
call activate onvif
cd "C:\Users\user\Desktop\ONVIF\onvif_control"
C:\Users\user\.conda\envs\onvif\python.exe rtsp_imshow.py
pause
ECHO finish