@echo off
chcp 65001 >nul
setlocal DisableDelayedExpansion
title Aplicar traducao KH3
echo.
echo === Traducao Kingdom Hearts III ===
echo.

set "ALVO=%~1"
if defined ALVO goto temalvo

echo Arraste a pasta do jogo em cima deste arquivo.
echo Ou cole o caminho dela abaixo.
set /p "ALVO=Pasta app0: "
if defined ALVO goto temalvo

echo Nenhuma pasta informada.
goto fim

:temalvo
echo Alvo: "%ALVO%"
echo.
set "KH3_FROM_BAT=1"
set "PYTHONUNBUFFERED=1"
set "PYTHONIOENCODING=utf-8"
echo Atualizando. A barra anda ate terminar. Nao feche esta janela.

where python >nul 2>&1
if errorlevel 1 goto trypy
python "%~dp0aplicar_traducao.py" "%ALVO%"
goto depois

:trypy
where py >nul 2>&1
if errorlevel 1 goto nopy
py -3 "%~dp0aplicar_traducao.py" "%ALVO%"
goto depois

:nopy
echo Python 3 nao encontrado.
echo Instale o Python no PC (python.org) e marque "Add python.exe to PATH".
goto fim

:depois
if errorlevel 1 goto falhou
echo.
echo Pronto.
goto fim

:falhou
echo.
echo Falhou. Confira o Python e a pasta do jogo.

:fim
echo.
pause
endlocal
