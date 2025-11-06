@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================
:: ComfyUI EasyToolkit Installation Script
:: ============================================

set "SCRIPT_DIR=%~dp0"
set "REQUIREMENTS=%SCRIPT_DIR%requirements.txt"
set "PYTHON_EMBEDED=..\..\..\python_embeded\python.exe"
set "PYTHON_EMBEDDED=..\..\..\python_embedded\python.exe"
set "INSTALL_SUCCESS=1"

:: Color codes (using ANSI escape sequences)
set "COLOR_RESET=[0m"
set "COLOR_GREEN=[92m"
set "COLOR_YELLOW=[93m"
set "COLOR_RED=[91m"
set "COLOR_BLUE=[94m"

:: ============================================
:: Functions
:: ============================================

:: Print colored message
call :PrintHeader

:: Check if requirements.txt exists
if not exist "%REQUIREMENTS%" (
    call :PrintError "requirements.txt not found at: %REQUIREMENTS%"
    set "INSTALL_SUCCESS=0"
    goto :End
)

call :PrintInfo "Found requirements.txt"
call :PrintInfo "Dependencies to install:"
for /f "usebackq delims=" %%i in ("%REQUIREMENTS%") do (
    echo   - %%i
)
echo.

:: Try to find Python executable
set "PYTHON_EXEC="

:: Check for python_embeded (typo version)
if exist "%PYTHON_EMBEDED%" (
    set "PYTHON_EXEC=%PYTHON_EMBEDED%"
    call :PrintInfo "Found ComfyUI Portable Python: python_embeded"
    goto :PythonFound
)

:: Check for python_embedded (correct spelling)
if exist "%PYTHON_EMBEDDED%" (
    set "PYTHON_EXEC=%PYTHON_EMBEDDED%"
    call :PrintInfo "Found ComfyUI Portable Python: python_embedded"
    goto :PythonFound
)

:: Fall back to system Python
call :PrintWarning "ComfyUI Portable Python not found."
echo.
call :PrintInfo "Do you want to use system Python instead?"
echo.
set /p "USE_SYSTEM_PYTHON=Use system Python? (Y/N): "

if /i "!USE_SYSTEM_PYTHON!"=="Y" (
    call :PrintInfo "Checking system Python..."
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXEC=python"
        call :PrintInfo "Found system Python"
        goto :PythonFound
    ) else (
        call :PrintError "System Python not found!"
        call :PrintError "Please install Python or check your ComfyUI installation."
        set "INSTALL_SUCCESS=0"
        goto :End
    )
) else (
    call :PrintInfo "Installation cancelled by user."
    set "INSTALL_SUCCESS=0"
    goto :End
)

:PythonFound
:: Verify Python version
call :PrintInfo "Verifying Python installation..."
"%PYTHON_EXEC%" --version 2>&1
if !errorlevel! neq 0 (
    call :PrintError "Python executable found but cannot run!"
    set "INSTALL_SUCCESS=0"
    goto :End
)

:: Check pip availability
call :PrintInfo "Checking pip availability..."
"%PYTHON_EXEC%" -m pip --version >nul 2>&1
if !errorlevel! neq 0 (
    call :PrintError "pip is not available!"
    call :PrintError "Please install pip first."
    set "INSTALL_SUCCESS=0"
    goto :End
)

call :PrintSuccess "pip is available"
echo.

:: Install dependencies
call :PrintHeader2 "Installing Dependencies"

set "PIP_INDEX=-i https://pypi.tuna.tsinghua.edu.cn/simple"
set "ERROR_COUNT=0"

for /f "usebackq delims=" %%i in ("%REQUIREMENTS%") do (
    set "PACKAGE=%%i"
    :: Skip empty lines and comments
    if not "!PACKAGE!"=="" (
        echo !PACKAGE! | findstr /r /c:"^#" >nul
        if !errorlevel! neq 0 (
            call :PrintInfo "Installing: !PACKAGE!"
            if "%PYTHON_EXEC%"=="python" (
                pip install "!PACKAGE!" %PIP_INDEX%
            ) else (
                "%PYTHON_EXEC%" -s -m pip install "!PACKAGE!" %PIP_INDEX%
            )
            
            if !errorlevel! neq 0 (
                call :PrintError "Failed to install: !PACKAGE!"
                set /a ERROR_COUNT+=1
            ) else (
                call :PrintSuccess "Successfully installed: !PACKAGE!"
            )
            echo.
        )
    )
)

:: Summary
echo.
call :PrintHeader2 "Installation Summary"

if !ERROR_COUNT! equ 0 (
    call :PrintSuccess "All dependencies installed successfully!"
    call :PrintSuccess "ComfyUI EasyToolkit is ready to use."
    echo.
    call :PrintInfo "Please restart ComfyUI to load the extension."
) else (
    call :PrintWarning "Installation completed with !ERROR_COUNT! error(s)."
    call :PrintWarning "Some packages may not have been installed correctly."
    set "INSTALL_SUCCESS=0"
)

goto :End

:: ============================================
:: Helper Functions
:: ============================================

:PrintHeader
echo ============================================
echo  ComfyUI EasyToolkit - Installation
echo ============================================
echo.
goto :eof

:PrintHeader2
echo --------------------------------------------
echo  %~1
echo --------------------------------------------
goto :eof

:PrintInfo
echo [INFO] %~1
goto :eof

:PrintSuccess
echo [SUCCESS] %~1
goto :eof

:PrintWarning
echo [WARNING] %~1
goto :eof

:PrintError
echo [ERROR] %~1
goto :eof

:End
echo.
echo ============================================
if "!INSTALL_SUCCESS!"=="1" (
    echo Installation completed successfully!
) else (
    echo Installation completed with errors.
    echo Please check the messages above.
)
echo ============================================
echo.
pause
exit /b !INSTALL_SUCCESS!