import telebot, dotenv, os, time, logging, shutil, datetime

DRIVE_LINK  = "На данный момент ссылки нет..."

dotenv.load_dotenv()
token = os.getenv('TOKEN')

bot = telebot.TeleBot(token)


def upload(path="media/image.png"):
    logging.info(f"Started upload for file at {path}...")

    dest = path.replace("media", "album", 1)

    sl = dest.rfind("/")
    dot = dest.rfind(".")

    dest = dest[:sl + 1] + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S.%f")[:-3] + dest[dot:]

    shutil.copy(path, dest)

    logging.info("Upload successful!")
    return 0


@bot.message_handler(commands=["start", "?"])
def start_message(message: telebot.types.Message):
    bot.reply_to(message, "Присылайте фотографию для добавления в альбом.\n\nКоманды:\n\t/link - получить ссылку на альбом\n\t/stat - узнать количество загруженных фоток")


@bot.message_handler(commands=["link"])
def display_types(message: telebot.types.Message):
    bot.reply_to(message, f"Ссылка на альбом:\n{DRIVE_LINK}")


@bot.message_handler(commands=["stat"])
def get_stats(message: telebot.types.Message):
    count = len(os.listdir('album/'))

    bot.reply_to(message, f"На данный момент загружено {count} фоток.")


@bot.message_handler(content_types=["photo"])
def get_photo(message: telebot.types.Message):
    photo_id = message.photo[-1].file_id

    f_path = bot.get_file(photo_id).file_path
    dl_file = bot.download_file(f_path)

    with open("media/image.png", 'wb') as f:
        f.write(dl_file)

    while upload() != 0:
        logging.warning(f"Retrying photo upload with id {photo_id}...")
        time.sleep(5)

    os.remove("media/image.png")
    bot.reply_to(message, "Фото отправлено!")


@bot.message_handler(content_types=["video"])
def get_video(message: telebot.types.Message):
    video_id = message.video.file_id

    f_path = bot.get_file(video_id).file_path
    dl_file = bot.download_file(f_path)

    if (ind := f_path.rfind("/")) != -1:
        f_path = f_path[ind + 1:]

    f_path = f"media/{f_path}"

    with open(f_path, 'wb') as f:
        f.write(dl_file)

    while upload(path=f_path) != 0:
        logging.warning(f"Retrying vid upload with id {video_id}...")
        time.sleep(5)

    os.remove(f_path)
    bot.reply_to(message, "Видео отправлено!")


@bot.message_handler(content_types=["document"])
def get_doc(message: telebot.types.Message):
    file_id = message.document.file_id

    f_path = bot.get_file(file_id).file_path
    dl_file = bot.download_file(f_path)

    if (ind := f_path.rfind("/")) != -1:
        f_path = f_path[ind + 1:]

    f_path = f"media/{f_path}"

    with open(f_path, 'wb') as f:
        f.write(dl_file)

    while upload(path=f_path) != 0:
        logging.warning(f"Retrying doc upload with id {file_id}...")
        time.sleep(5)

    os.remove(f_path)
    bot.reply_to(message, "Файл отправлен!")


if __name__ == '__main__':
    log_format = "%(asctime)s - %(levelname)s: %(message)s"
    logging.basicConfig(format=log_format, filename='photobot.log', level=logging.INFO)
    logging.info('Started Logger!')
    bot.infinity_polling()
