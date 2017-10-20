#pinagem do pir = vcc|signal|gnd com os pinos proximos ao observador
from telegram.ext import Updater, CommandHandler, RegexHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from subprocess import call
from telegram import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
import _thread
import logging
import re
import time
import RPi.GPIO as GPIO

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='example.log',level=logging.INFO)

logger = logging.getLogger(__name__)
my_token = None
users = set()

#o pino 12, no modo board, da raspberry deve ser conectado ao pino de saída de sinal do pir. Outro pino pode ser escolhido, sempre levando em conta as limitações de hardware
pir_pin = 12


pir_active = False 
bot_instance = None
WHICH, PIR, SOUND, NOTIFICATIONS = range(4)
audio_name = None

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

#Informa as funções do bot
def start(bot, update):
	keyboard = [[KeyboardButton("Enviar foto")],[KeyboardButton("Screenshot")],[KeyboardButton("Configurar")]]
	reply_markup1 = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
	update.message.reply_text("Bem Vindo ao CamBot. Se uma câmera estiver disponível, você será capaz de solicitar que uma foto seja capturada e enviada para você. Se um sensor de movimento estiver disponível, você poderá solicitar que uma foto seja enviada sempre que algo se mover. Além disso, você pode enviar uma mensagem de áudio para que ela seja reproduzida imediatamente ou configurar para que a mensagem de voz seja reproduzida sempre que algo se mover. Também é possível solicitar uma screenshot do hardware que está hospedando este bot.", reply_markup=reply_markup1)
	logger.info('User "%s" started using this bot' % (update.effective_user.username))

#função executada quando uma mensagem de voz é recebida
#faz o download do arquivo de voz no formato oga, reproduz usando o omxplayer e registra o ocorrido
def audio_message(bot, update):
	voice = bot.get_file(update.message.voice.file_id)
	name = 'audio '+time.strftime("%c", time.localtime())+'.oga'
	voice.download(custom_path=name)
	call(["omxplayer", "-o", "alsa", name])
	logger.info('User "%s" sent a the audio "%s" for runonce' % (update.effective_user.username, name))

#função executada durante a "conversa gerenciada" configurar
#faz o download do áudio recebido, define audio_name (variável que define o áudio reproduzido em caso de movimento), envia ao usuário confirmação e regristra o ocorrido
def define_sound(bot, update):
	voice = bot.get_file(update.message.voice.file_id)
	audio_name = 'audio '+time.strftime("%c", time.localtime())+'.oga'
	voice.download(custom_path=audio_name)
	update.message.reply_text("O audio enviado será reproduzido quando houver movimentação.")
	logger.info('User "%s" sent a the audio "%s" for run on movement' % (update.effective_user.username, audio_name))
	return ConversationHandler.END;
	
#salva uma captura de tela e envia para quem a solicitou e registra o ocorrido
def send_screenshot(bot, update):
	name = 'screen '+time.strftime("%c", time.localtime())+'.png'
	print(name)
	print(call(["scrot", name]))
	print(bot_instance.send_photo(chat_id=update.message.chat_id, photo=open(name, 'rb')))
	logger.info('User "%s" requested a screenshot' % (update.effective_user.username))
	
#salva uma captura da webcam, caso tenha sido solicitada por um usuário, envia-a ao usuário que a solicitou. Caso contrário, foi chamada devido a detecção de algum movimento; Então, envia a captura a todos os usuários inscritos
def send_webcam(bot = None, update = None): 
	name = time.strftime("%c", time.localtime())+'.jpg'
	print("send_cam")
	call(["fswebcam", "-r", "640x480", name])
	if update != None:
		print(bot_instance.send_photo(chat_id=update.message.chat_id, photo=open(name, 'rb')))
		logger.info('Picture sent to "%s" due to request' % (update.effective_user.username))
		
	elif len(users) != 0:
		if audio_name != None:
			call(["omxplayer", "-o", "alsa", audio_name])
		for user in users:
			try:
				print(bot_instance.send_photo(chat_id=user, photo=open(name, 'rb')))
				logger.info('Picture sent to "%s" due to movement detected' % (user))
			except:
				print('unexpected error:', sys.exc_info()[0])
				raise
#envia as opções de configuração
def setup(bot, update):
	print("setup")
	keyboard = [[InlineKeyboardButton("Configurar Notificações", callback_data='1')],[InlineKeyboardButton("Configurar PIR", callback_data='2')],[InlineKeyboardButton("Configurar Som", callback_data='3')], [InlineKeyboardButton("Cancelar", callback_data= "cancelar")]]
	reply_markup1 = InlineKeyboardMarkup(keyboard)
	update.message.reply_text("Escolha o que deseja configurar", reply_markup=reply_markup1)
	return WHICH;

#envia as opções de configuração de som
def setup_sound(bot, update):
	keyboard = [[InlineKeyboardButton("Desativar", callback_data='desativar')],[InlineKeyboardButton("Cancelar", callback_data='cancelar')]]
	reply_markup1 = InlineKeyboardMarkup(keyboard)
	bot.edit_message_text(text="Envie uma mensagem de áudio para que ela seja reproduzida sempre que algo se mover ou use a opção de desativar esta funcionalidade.", chat_id=update.effective_user.id, message_id= update.effective_message.message_id)
	bot.edit_message_reply_markup(message_id = update.effective_message.message_id, chat_id=update.effective_user.id, reply_markup=reply_markup1)
	return SOUND;

#define o áudio que deve ser reproduzido em caso de movimento para None e registra
def deactivate_sound(bot, update):
	audio_name = None
	bot.edit_message_text(text="A reprodução automática de audio foi desativada.", chat_id=update.effective_user.id, message_id= update.effective_message.message_id)
	logger.info('Audio reproduction disabled by user "%s"' % (update.effective_user.username))
	return ConversationHandler.END;
	
#oferece as opções de configuração do sensor de movimento	
def setup_pir(bot, update):
	keyboard = [[InlineKeyboardButton("Ativar Pir", callback_data='ativado')],[InlineKeyboardButton("Desativar Pir", callback_data='desativado')], [InlineKeyboardButton("Cancelar", callback_data = "cancelar")]]
	reply_markup1 = InlineKeyboardMarkup(keyboard)
	text1 = "Atualmente o sensor de movimento está "
	if pir_active == True:
		text1 += "ativado"
	else:
		text1 += "desativado"
#só pode editar mensagens enviadas pelo bot!
	bot.edit_message_text(text=text1, chat_id=update.effective_user.id, message_id= update.effective_message.message_id)
	bot.edit_message_reply_markup(message_id = update.effective_message.message_id, chat_id=update.effective_user.id, reply_markup=reply_markup1)
	return PIR;

#altera o estado da detecção de movimento
def switch_pir(bot, update):
	if update.callback_query.data == 'ativado':
		pir_active = True
		GPIO.add_event_detect(pir_pin, GPIO.RISING, callback=send_webcam, bouncetime=3000)
		logger.info('Pir enabled by user "%s"' % (update.effective_user.username))
	if update.callback_query.data == 'desativado':
		pir_active = False
		GPIO.remove_event_detect(pir_pin)
		logger.info('Pir disabled by user "%s"' % (update.effective_user.username))
	bot.edit_message_text(text="O sensor foi " + update.callback_query.data, chat_id=update.effective_user.id, message_id= update.effective_message.message_id)
	return ConversationHandler.END;
		
		
#cancela a configuração: remove os teclados e mensagens e teclados de configuração; Sai da conversa gerenciada sobre configuração
def cancel(bot, update):
	bot.edit_message_text(text="Ok", chat_id=update.effective_user.id, message_id= update.effective_message.message_id)
	return ConversationHandler.END;
	print("Cancel")

#oferece opções sobre notificações
def setup_notifications(bot, update):
	keyboard = [[InlineKeyboardButton("Ativar notificações", callback_data='ativadas')], [InlineKeyboardButton("Desativar notificações", callback_data='desativadas')],[InlineKeyboardButton("Cancelar", callback_data='cancelar')]]
	reply_markup1 = InlineKeyboardMarkup(keyboard)
	if update.effective_user.id in users:
		text = "Suas notificações estão ativas"
	else:
		text = "Suas notificações estão inativas"
	bot.edit_message_text(text=text, chat_id=update.effective_user.id, message_id= update.effective_message.message_id)
	bot.edit_message_reply_markup(message_id = update.effective_message.message_id, chat_id=update.effective_user.id, reply_markup=reply_markup1)
	return NOTIFICATIONS;

#define o estado da configuração de notificação
def switch_notifications(bot, update):
	if update.callback_query.data == 'ativadas':
		if update.effective_user.id not in users:
			users.add(update.effective_user.id)
			logger.info('User "%s" subscribed to receive notifications' % (update.effective_user.username))
	if update.callback_query.data == 'desativadas':
		if update.effective_user.id in users:
			users.remove(update.effective_user.id)
			logger.info('User "%s" unsubscribed to receive notifications' % (update.effective_user.username))
		
	text = "Suas notificações estão "
	bot.edit_message_text(text="As notificações estão " + update.callback_query.data, chat_id=update.effective_user.id, message_id= update.effective_message.message_id)
	return ConversationHandler.END;
	
	
def main():
	if my_token == None:
		print ("O Token NÃO FOI DEFINIDO, defina-o usando a variável my_id.")
		exit();
#configuração dos pinos de GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pir_pin, GPIO.IN)

	#O Token dado pelo BotFather na criação do seu bot
	updater = Updater(my_token)
#definição da variável global bot_instance, referência para o seu bot
	global bot_instance
	bot_instance = updater.bot

#Cria uma "conversa gerenciada", que é iniciada pelo recebimento do texto Configurar
	conv_handler = ConversationHandler(entry_points = [RegexHandler("^Configurar$", setup)],
 		states={
			WHICH: [CallbackQueryHandler(setup_notifications, pattern = "^1$"), CallbackQueryHandler(setup_pir, pattern = "^2$"), CallbackQueryHandler(setup_sound, pattern = "^3$")], 
			PIR: [CallbackQueryHandler(switch_pir)],
			SOUND: [MessageHandler(Filters.voice, define_sound), CallbackQueryHandler(deactivate_sound, pattern = "^desativar$")],
			NOTIFICATIONS: [CallbackQueryHandler(switch_notifications)]
		}, 
		fallbacks = [CallbackQueryHandler(cancel, pattern = "^cancelar$")],
	)
#dispatcher é responsável por "despachar" as atualizações que chegam
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(conv_handler);
	dp.add_handler(RegexHandler("^Enviar foto$", send_webcam))
	dp.add_handler(RegexHandler("^Screenshot", send_screenshot))
	dp.add_handler(MessageHandler(Filters.voice, audio_message))
	dp.add_error_handler(error)

	updater.start_polling()

	updater.idle()


	

if __name__ == '__main__':
    main()
