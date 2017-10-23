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
# Como usar
Tendo instaladas todas as dependências, você deve definir o valor da variável my_token como o token recebido no momento da criação do seu bot junto ao BotFather. Feito isso, é só começar a usá-lo via Telegram.

# Hardware
-O projeto foi testado com Raspberrys Pi 2B e 3B
-Sensor PIR compatível com Arduino (OUTPUT 3.3V)
-Webcam padrão USB.
-Caixas de som analógicas

# Arquitetura
O usuário se comunica via telegram, através de moblile ou computador. A raspberry coleta as atualizações dos servidores do telegram. A raspberry lê os dados do sensor de movimento. Envia audio para reprodução nas caixas de som. Envia ordens para a webcam e recebe imagens.
A arquitetura usada no bot pode ser vista no diagrama.
![alt text](https://github.com/kenchen12/TelegramCamBot/blob/kenchen12-patch-1/Diagram.png?raw=true)
# Dependências
    o Programas
      - fswebcam
      - omxplayer
      - scrot
    o Pacotes python
      - Python 3 ou superior
      - RPi.GPIO
      - Python-telegram-bot
      

