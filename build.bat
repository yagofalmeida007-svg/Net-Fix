@echo off
setlocal
cd /d "%~dp0"
REM Gera dist\NetFix.exe (rode no Windows, na pasta do projeto)

REM 1. Procura o Python (prefere o launcher "py")
set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY goto sempython

%PY% --version >nul 2>nul
if errorlevel 1 goto sempython

REM 2. Garante que o pip existe
%PY% -m pip --version >nul 2>nul
if errorlevel 1 (
  echo pip nao encontrado. Tentando instalar automaticamente...
  %PY% -m ensurepip --upgrade
  %PY% -m pip --version >nul 2>nul
  if errorlevel 1 goto sempip
)

REM 3. Instala as dependencias
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto erro

REM 4. Gera o executavel
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name NetFix ^
  --uac-admin ^
  --noupx ^
  --icon assets\icons\app.ico ^
  --add-data "assets;assets" ^
  --collect-all customtkinter ^
  main.py
if errorlevel 1 goto erro

echo.
echo Pronto: dist\NetFix.exe
pause
exit /b 0

:sempython
echo.
echo Python nao encontrado.
echo Instale em https://www.python.org/downloads/ e marque a opcao
echo "Add python.exe to PATH" na primeira tela do instalador.
pause
exit /b 1

:sempip
echo.
echo Nao consegui instalar o pip automaticamente.
echo Rode o instalador do Python novamente, escolha "Modify" e
echo marque a opcao "pip".
pause
exit /b 1

:erro
echo.
echo Algo deu errado. Veja as mensagens acima.
pause
exit /b 1
