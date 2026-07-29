@echo off
REM SPDT-001 Batch DevEco Studio Sync v2 ? ?? .idea ???? Sync
set "DEVENV=D:\9_infra\DevEco\6.1\bin\devecostudio.bat"
set "ROOT=D:\92_products\SPDT-001_Harmony\apps"

echo ========================================
echo  SPDT-001 Batch Sync v2 (fresh .idea)
echo  %date% %time%
echo ========================================
echo.
echo This version DELETES .idea folders first
echo to force DevEco to treat each project as
echo a fresh open (triggering signing auto-inject).
echo.
pause

echo [1/17] craftsman-api-tester
rmdir /s /q "%ROOT%\craftsman-api-tester\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\craftsman-api-tester"
pause

echo [2/17] craftsman-code-editor
rmdir /s /q "%ROOT%\craftsman-code-editor\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\craftsman-code-editor"
pause

echo [3/17] craftsman-ohpm
rmdir /s /q "%ROOT%\craftsman-ohpm\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\craftsman-ohpm"
pause

echo [4/17] craftsman-scanner
rmdir /s /q "%ROOT%\craftsman-scanner\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\craftsman-scanner"
pause

echo [5/17] craftsman-utils
rmdir /s /q "%ROOT%\craftsman-utils\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\craftsman-utils"
pause

echo [6/17] craftsman-utils-v2
rmdir /s /q "%ROOT%\craftsman-utils-v2\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\craftsman-utils-v2"
pause

echo [7/17] harmonycoder
rmdir /s /q "%ROOT%\harmonycoder\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\harmonycoder"
pause

echo [8/17] harmonycoder-snippets
rmdir /s /q "%ROOT%\harmonycoder-snippets\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\harmonycoder-snippets"
pause

echo [9/17] rhythm-habit
rmdir /s /q "%ROOT%\rhythm-habit\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\rhythm-habit"
pause

echo [10/17] rhythm-habit-game
rmdir /s /q "%ROOT%\rhythm-habit-game\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\rhythm-habit-game"
pause

echo [11/17] rhythm-meditation
rmdir /s /q "%ROOT%\rhythm-meditation\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\rhythm-meditation"
pause

echo [12/17] rhythm-nutrition
rmdir /s /q "%ROOT%\rhythm-nutrition\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\rhythm-nutrition"
pause

echo [13/17] rhythm-pomodoro
rmdir /s /q "%ROOT%\rhythm-pomodoro\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\rhythm-pomodoro"
pause

echo [14/17] thinkkit-flashcard
rmdir /s /q "%ROOT%\thinkkit-flashcard\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\thinkkit-flashcard"
pause

echo [15/17] thinkkit-flashcard2
rmdir /s /q "%ROOT%\thinkkit-flashcard2\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\thinkkit-flashcard2"
pause

echo [16/17] thinkkit-rss
rmdir /s /q "%ROOT%\thinkkit-rss\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\thinkkit-rss"
pause

echo [17/17] thinkkit-zknote
rmdir /s /q "%ROOT%\thinkkit-zknote\.idea" 2>nul
start "" "%DEVENV%" "%ROOT%\thinkkit-zknote"
pause

echo.
echo ========================================
echo  ALL DONE
echo  Verify: python apps\build-all.py --report-only
echo ========================================
pause