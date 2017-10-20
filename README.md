[![Python-Versions](https://img.shields.io/badge/python-3.4%2C%203.5-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
# TelegramCamBot
Uma aplicação desenvolvida em Python envolvendo Raspberry Pi, automação e Telegram Bots. 

# Funcionalidades:
    o Captura de fotos
        -Sob demanda, através do Telegram
        -Automaticamente, caso movimento seja detectado por um sensor PIR
    o Reprodução de áudio
        -Sob demanda
        -Quando movimento é detectado
        
# Dependências
    o Programas
      - fswebcam
      - omxplayer
      - scrot
    o Pacotes python
      - Python 3 ou superior
      - RPi.GPIO
      - Python-telegram-bot
      
# Como usar
Tendo instaladas todas as dependências, você deve definir o valor da variável my_token como o token recebido no momento da criação do seu bot junto ao BotFather. Feito isso, é só começar a usá-lo via Telegram.

