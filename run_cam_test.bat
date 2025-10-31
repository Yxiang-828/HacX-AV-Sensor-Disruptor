@echo off
call .\venv\Scripts\activate.bat
pip install opencv-python numpy pyserial
python tests\cam_test\cam_test.py
pause