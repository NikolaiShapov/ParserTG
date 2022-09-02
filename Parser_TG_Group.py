#from telethon import TelegramClient
from telethon.sync import TelegramClient  #pip install telethon
from telethon import functions, types
import datetime
import configparser

DMY = datetime.datetime.now().strftime('%d%m%y') # = '180122' дата в таком формате (и есть пароль!)

# Use your own values here
#api_id = 
#api_hash = ' '

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

client = TelegramClient('some_name', api_id, api_hash)
client.start()

#записываем зерультаты в файл
def writ_ruselt(text,dmy,Telegram_title,Telegram_username,item_new,subscribers,date):
    with open('sid'+dmy+'_00.txt' , 'a',encoding='utf-8') as f:
        f.write('==/СМИ\n')
        f.write('01/107.0.1001\n') #НЕ МЕНЯТЬ У ВСЕХ СТАТЕЙ ТАКОЙ КОД
        f.write('02/' + date.strftime('%Y-%m-%d')+'\n') # ДАТА формата 2022-01-18
        f.write('03/107.29\n')# НЕ МЕНЯТЬ У ВСЕХ СТАТЕЙ ТАКОЙ КОД        
        f.write('07/' + Telegram_title + ' ' + date.strftime('%Y.%m.%d %H:%m') + '\n')# НАЗВАНИЕ КАНАЛА ГГГГ.ММ.ДД ЧЧ:ММ
        f.write('08/\n') #ОСТАВИТЬ ПУСТЫМ
        f.write('06/' + text + ' (Подписчиков - ' + subscribers + ')' + ' ('+ 'https://t.me/' + Telegram_username + ').\n\n') #В конце каждой статьи добавляется ссылка на канал с указанием количества подписчиков в таком формате: (Подписчиков - ) ().
        f.write('START ' + 'https://t.me/' + Telegram_username + '/' + str(item_new) + ' FINISH' +'\n\n')
        

def writ_comment_ruselt(dmy,date,sender,text):    
    with open('sid'+dmy+'_00.txt' , 'a',encoding='utf-8') as f:
        try:
            f.write(date.strftime('%Y.%m.%d %H:%m') + ' ' + sender + ':' + text + '\n')
        except:
            f.write(date.strftime('%Y.%m.%d %H:%m') + ' ' + '!!!Erro_Name_User!!!' + ':' + text + '\n')
            print('!!!Erro_Name_User!!!')

#теск редактируем
def Text_redit(text):  
    if text == '':
        return ('NO TEXT NEWS') # в новости может не быть текста а только картинка или видео или ...
    text = text.replace('\xa0',' ')
    text = text.replace('\xad','')
    text = text.replace('\n\n ','\n')
    text = text.replace('\n \n','\n')
    text = text.replace('\n\n','\n')
    #text.rstrip()
    #text = '.\n'.join(text.split('\n'))
    return (text.rstrip())    

async def main():
    async with client_to_manage as client:
        full_info = await client(GetFullChannelRequest(channel="moscowproc"))
        print(f"count: {full_info.full_chat.participants_count}")
        
async def handler():
    news_count = 0
    with open('point.txt') as f: # open file read        
        for line in f:
            news_count_group = 0
            Erro_post = 0
            channel = await client.get_entity(line) # пользователь передаст ссылку на интересующий источник
            #print(channel.stringify())
            Telegram_title = channel.title # Оф. название канала
            Telegram_username = channel.username # Название канала в ссылке на канал
            async for message in client.iter_messages(channel,limit=5000): # получаем limit сообщений
            #print (message.date.replace(tzinfo=None) + datetime.timedelta(hours=3), day)
            #print (type(message.date), type(day))
            # message.legacy == True это условие нужно что бы "удаленные" сообщения не поподали в выборку
                if message.date.replace(tzinfo=None) + datetime.timedelta(hours=3) < day:
                    print('Новости закончились в ', line.replace('\n',''), ', переходим к следующей группе')
                    break
                if message.text != "" and message.date.replace(tzinfo=None) + datetime.timedelta(hours=3) >= day: #and message.legacy == True, replace(tzinfo=None)- убираем временую зону для сравнения и +3 часа что бы привести к МКС
                    #print(message.stringify())
                    #print(channel.username, message.id, message.text[0:20])                      
                    #print(message.id, message.date, message.text, message.stringify())
                    if flag_comments == '1': DMY = str(message.date.month) + '.' + str(message.date.year)
                    try:
                        text = Text_redit(message.text) #тест поста, сразу убираем лишние пробелы и др. "водные" знаки
                        date = message.date + datetime.timedelta(hours=3) # +3 часа = Московскому времени
                        item_new = message.id #номер(id) поста
        ##                    members = client.get_participants(channel.username)
        ##                    print(members)
                        full_info = await client(functions.channels.GetFullChannelRequest(channel=channel))
                        #print(f"count: {full_info.full_chat.participants_count}")
                        #print(full_info.stringify())
                        subscribers = str(full_info.full_chat.participants_count) # количество подписчиков канала
                        writ_ruselt(text,DMY,Telegram_title,Telegram_username,item_new,subscribers,date)

                        if flag_comments == '1':
                            with open('sid'+DMY+'_00.txt' , 'a',encoding='utf-8') as f: f.write('КОММЕНТАРИИ:\n')
                            # Парсим все коментарии к посту:
                            async for comment in client.iter_messages(channel.username, reply_to=message.id, reverse=True): # Проходим по всем коментариям
                                if isinstance(comment.sender, types.User):    #если это пользователь то:
                                    writ_comment_ruselt(DMY,comment.date, comment.sender.first_name, comment.text) # Записываем в файл
                                else:     #Иначе это не пользователь то:
                                    #print(Telegram_title)
                                    try: title = comment.sender.title # Бывает нет ни comment.sender.first_name и comment.sender.title, скорее все это сам владелец канала и по этому присваевам Telegram_title
                                    except: title = Telegram_title
                                    writ_comment_ruselt(DMY,comment.date, title, comment.text) # Записываем в файл

                            with open('sid'+DMY+'_00.txt' , 'a',encoding='utf-8') as f: f.write('\n') #Enter после комментариев
                    except:
                        Erro_post =+1
                        print(Erro_post,'Erro Parser Post -', item_new)

                    news_count_group += 1 #Счетчик Новостей в каждой группе отдельно
                    news_count += 1 #Счетчик Новостей Общий
                    print("=",news_count,'|',news_count_group, "Новостей из ", line.replace('\n',''))
      
print('''Сбор сообщений в Telegram
Группы записываюся в формате https://t.me/НазваниеГруппы
Все группы храняться в текстовом файле point.txt
Для работы скрипта неоходимы api_id и api_hash,
Заходим на сайт телеграма: https://my.telegram.org
Вводим телефон и ждем код подтверждения на родном клиенте телеграма.
Он довольно длинный (12 символов) и неудобный для ввода.
Заходим в пункт "API". Ищем "Telegram API" и заходим в "Creating an application"
(https://my.telegram.org/apps).
Заполняем поля App title и Short name (Произвольно!), нажимаем «Create application»
и забираем две переменные: api_id и api_hash.
Избегая проблем с безопасностью, сохраняем учетные данные в отдельном файле config.ini
''')
print('\n\n')
flag_comments = str(input('Нужны коментарии(1-да;*-нет,По умолчанию "Нет")'))
if flag_comments != '1':
    flag_comments = '0' # если пользователь ввел не один то коменты не нужны = 0
    print('Коментарии НЕ нужны.')
else: print('Коментарии нужны.')

flag_mounth = str(input('Нужны разбить по месяцам (1-да;*-нет,По умолчанию "Нет")'))
if flag_mounth != '1':
    flag_mounth = '0' # если пользователь ввел не один то коменты не нужны = 0
    print('Коментарии НЕ нужны.')
else: print('Коментарии нужны.')
day = datetime.datetime.strptime(input
                                 ("Дата в формате '30/06/22 16:30' с которой нужно собрать сообщения: "),
                                 "%d/%m/%y %H:%M")
start_time = datetime.datetime.now() # time start program
client.loop.run_until_complete(handler())
finish_time = datetime.datetime.now() # time finish program
print("Time the program was running:",finish_time - start_time)
input('Input Enter...')
#client.run_until_disconnected() #Чтобы клиент не заканчивал работу

