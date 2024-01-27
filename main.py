import logging
import os
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from gtts import gTTS
from langdetect import detect
from keep_alive import keep_alive
keep_alive()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the function to handle incoming messages
def handle_messages(update, context):
    message_text = update.message.text
    chat_id = update.message.chat_id

    # Extract language code from the message
    if message_text.lower() == 'english':
        language_code = 'en'
    elif message_text.lower() == 'bangla':
        language_code = 'bn'
    elif message_text.lower() == 'others':
        # Prompt the user to select from individual language buttons
        buttons = [
            [InlineKeyboardButton("Hindi", callback_data='hi')],
            [InlineKeyboardButton("Spanish", callback_data='es')],
            [InlineKeyboardButton("French", callback_data='fr')],
            [InlineKeyboardButton("German", callback_data='de')],
            [InlineKeyboardButton("Italian", callback_data='it')],
            [InlineKeyboardButton("Chinese", callback_data='zh')],
            [InlineKeyboardButton("Japanese", callback_data='ja')],
            [InlineKeyboardButton("Russian", callback_data='ru')],
            [InlineKeyboardButton("Arabic", callback_data='ar')],
            [InlineKeyboardButton("Tamil", callback_data='ta')],
            [InlineKeyboardButton("Telugu", callback_data='te')],
            # Add more languages as needed
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id, 'Please select a language:', reply_markup=reply_markup)
        return
    else:
        # Use language detection for other cases
        try:
            language_code = detect(message_text)
        except:
            # Default to English if detection fails
            language_code = 'en'

    # Prompt the user to enter a message in the detected language
    context.bot.send_message(chat_id, f"Please enter your message in {language_code}.")

    # Store the detected language in user_data for future messages
    context.user_data['language'] = language_code

# Define the function to handle text messages after language selection
def handle_text(update, context):
    text = update.message.text
    chat_id = update.message.chat_id

    # Retrieve the selected language from user_data
    language_code = context.user_data.get('language', 'en')

    # Convert text to speech using gTTS with the detected language
    tts = gTTS(text=text, lang=language_code)

    # Save the audio to a temporary file with a title based on the text
    audio_file_path = f"/tmp/audio_{chat_id}_{text[:15].replace(' ', '_')}.mp3"
    tts.save(audio_file_path)

    # Send the generated audio file as a document with the title as the filename
    context.bot.send_document(chat_id, document=open(audio_file_path, 'rb'), filename=f'{text[:15]}.mp3', caption=text)

    # Clean up the temporary file
    os.remove(audio_file_path)

# Define the /start command handler to initiate language selection
def start(update, context):
    buttons = [
        [KeyboardButton('English')],
        [KeyboardButton('Bangla')],
        [KeyboardButton('Others')]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    update.message.reply_text('Please select your preferred language:', reply_markup=reply_markup)

# Define the function to handle the "Others" button and dynamically generate language options
def others(update, context):
    buttons = [
        [InlineKeyboardButton("Hindi", callback_data='hi')],
        [InlineKeyboardButton("Spanish", callback_data='es')],
        [InlineKeyboardButton("French", callback_data='fr')],
        [InlineKeyboardButton("German", callback_data='de')],
        [InlineKeyboardButton("Italian", callback_data='it')],
        [InlineKeyboardButton("Chinese", callback_data='zh')],
        [InlineKeyboardButton("Japanese", callback_data='ja')],
        [InlineKeyboardButton("Russian", callback_data='ru')],
        [InlineKeyboardButton("Arabic", callback_data='ar')],
        [InlineKeyboardButton("Tamil", callback_data='ta')],
        [InlineKeyboardButton("Telugu", callback_data='te')],
        # Add more languages as needed
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Please select a language:', reply_markup=reply_markup)

# Define the callback function to handle language selection from "Others" button
def language_selection_callback(update, context):
    query = update.callback_query
    language_code = query.data
    context.user_data['language'] = language_code

    # Notify the user about the selected language
    query.edit_message_text(f"Selected language: {language_code}")

# Set up the updater with your bot token
updater = Updater(token='6688250412:AAHSdLb_UKf4TGdp0275AG4OLVEZ6i_OQyQ', use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Register the message handler to handle language selection
dispatcher.add_handler(MessageHandler(Filters.text & (Filters.regex('^(English|Bangla|Others)$')), handle_messages))

# Register the message handler to handle text messages after language selection
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

# Register the /start command handler
dispatcher.add_handler(CommandHandler("start", start))

# Register the handler for the "Others" button
dispatcher.add_handler(CommandHandler("others", others))

# Register the callback handler for language selection
dispatcher.add_handler(CallbackQueryHandler(language_selection_callback))

# Start the Bot
updater.start_polling()

# Run the bot until you send a signal to stop it
updater.idle()
