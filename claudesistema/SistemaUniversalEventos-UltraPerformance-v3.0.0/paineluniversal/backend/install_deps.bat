@echo off
echo Instalando dependencias necessarias...
pip install openai
pip install python-jose[cryptography] 
pip install passlib[bcrypt]
pip install python-multipart
pip install asyncio
echo Instalacao concluida!
pause
