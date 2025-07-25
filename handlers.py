from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
import database


def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    if database.add_user(user):
        update.message.reply_text("Welcome! You have been added to the database.")
    else:
        update.message.reply_text("You are already registered in the database.")

def handle_audio(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Please select a playlist to add this audio.",
        reply_markup=ReplyKeyboardMarkup(
            [['Workout Playlist', 'Chill Playlist'],
             ['Study Playlist', 'Party Playlist'],
             ['Favorites']],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    # Store the audio file ID in context for later use
    context.user_data['audio_file_id'] = update.message.audio.file_id
    

def add_audio_to_playlist(update: Update, context: CallbackContext):
    user = update.message.from_user
    audio_file_id = context.user_data.get('audio_file_id')
    playlist_name = update.message.text

    if playlist_name not in ['Workout Playlist', 'Chill Playlist', 'Study Playlist', 'Party Playlist', 'Favorites']:
        update.message.reply_text("Invalid playlist name. Please select a valid playlist.")
        return

    if audio_file_id and database.add_audio_to_playlist(user, playlist_name, audio_file_id):
        update.message.reply_text(f"Audio added to {playlist_name} successfully!")
    else:
        update.message.reply_text("Failed to add audio to the playlist. Please try again.")
    
    # Clear the stored audio file ID
    context.user_data['audio_file_id'] = None
    update.message.reply_text("You can send another audio file to add to a playlist.")


def list_playlists(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_data = database.get_users(user)

    if not user_data:
        update.message.reply_text("You are not registered. Please use /start to register.")
        return

    playlists = user_data.get('playlist', [])
    if not playlists:
        update.message.reply_text("You have no playlists.")
        return
    
    # send the list of playlists as inline buttons
    keyboard = [[InlineKeyboardButton(playlist['name'], callback_data=playlist['name'])] for playlist in playlists]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Your playlists:", reply_markup=reply_markup)


def send_songs(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    user = query.from_user
    playlist_name = query.data
    
    user_data = database.get_users(user)
    if not user_data:
        query.edit_message_text("You are not registered. Please use /start to register.")
        return
    
    for playlist in user_data.get('playlist', []):
        if playlist['name'] == playlist_name:
            songs = playlist['songs']
            if not songs:
                query.edit_message_text(f"No songs found in {playlist_name}.")
                return
            
            for song in songs:
                query.message.reply_audio(audio=song['file_id'], caption=f"Song in {playlist_name}")
            return
