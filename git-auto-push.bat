@echo off
echo [GIT AUTO PUSH] Iniciando sincronização...

:: Caminho para Git Bash - ajuste se necessário
set GITBASH="C:\Program Files\Git\bin\bash.exe"

:: Caminho para o script .sh
set SCRIPT_PATH="C:/Users/Cesar/Documents/Projetos/4. Transcrição/git-auto-push.sh"

:: Executa o script via Git Bash
%GITBASH% --login -i %SCRIPT_PATH%

echo [GIT AUTO PUSH] Finalizado.
pause
