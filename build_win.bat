del "WingetUI.exe"
cd wingetui
rmdir /Q /S build
rmdir /Q /S dist
python -m PyInstaller "Win.spec"
cd dist
move "WingetUI.exe" ../../
cd ..
rmdir /Q /S build
rmdir /Q /S dist
cd ..
"WingetUI"
pause