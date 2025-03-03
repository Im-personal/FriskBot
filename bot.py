import asyncio

import db
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Initialize bot and dispatcher
bot = Bot(token="7670339176:AAG3IfW1RWCkd4SoMA8PgubEOClsL2nU5vg")
dp = Dispatcher()

adm_list = []

db.init_db()

M_NONE = 0
M_ADMIN = 1
M_REMOVE_ADMIN = 6
M_CHATS = 2
M_CHATS_SER = 3
M_CHATS_SER_MSG = 4
M_MESSAGES = 5
M_LIST_NAME = 7
M_LIST_USERS = 8


def load_data():
    global adm_list
    adm_list=[]
    for n in db.get_admins():
        adm_list.append(n[0])


@dp.message(Command("start"))
async def start(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            await bot.send_message(message.from_user.id, "Привет! Пиши /help для всех команд.")
        else:
            await bot.send_message(message.from_user.id, "Привет! Напиши сюда и сообщение будет переслано админам. (Если адресат скрыт - админы не смогут ответить)")

@dp.message(Command("help"))
async def start(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            await bot.send_message(message.from_user.id, '''/help - список команд
/id - Узнать ID пользователя

/lists - Просмотреть созданные списки
/newlist - Создать новый список

/call <Название списка> - Созвать пользователей из списка (Если оставить пустым - созыв всего чата)

/addadmin - Добавить новых админов
/removeadmin - Удалить админов

/setupchats - Настройка чатов

/users <Количество> - Отобразить пользователей, написавших менее <Количество> сообщений в чате со включенным подсчетом
''')

@dp.message(Command("id"))
async def start(message: types.Message):
    if message.from_user.id in adm_list:
            await bot.send_message(message.chat.id, f"ID пользователя: {message.reply_to_message.from_user.id}")

@dp.message(Command("addadmin"))
async def start(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            await bot.send_message(message.from_user.id, '''
            Отправь ID или перешли сообщение того, кого хочешь добавить - они моментально станут админами.
            Когда хватит - пиши /cancel
            ''')
            db.set_adm_state(message.from_user.id,M_ADMIN)

@dp.message(Command("state"))
async def state(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            await bot.send_message(message.from_user.id, f"{db.get_adm_state(message.from_user.id)}")


@dp.message(Command("removeadmin"))
async def remove_admin(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            await bot.send_message(message.from_user.id, '''
            Отправь ID или перешли сообщение того, с кого хочешь снять власть - они моментально будут удалены.
            Когда хватит - пиши /cancel
            ''')
            db.set_adm_state(message.from_user.id,M_REMOVE_ADMIN)

@dp.message(Command("cancel"))
async def remove_admin(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            await bot.send_message(message.from_user.id, '''
            Выход из режимов!
            ''')
            db.set_adm_state(message.from_user.id,M_NONE)

@dp.message(Command("setupchats"))
async def setup_chats(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            db.set_adm_state(message.from_user.id, M_CHATS)
            await bot.send_message(message.from_user.id,f"Настройка чатов! Вот чаты, которые помнит бот:")

            for d in db.get_chats():
                chat_d = await bot.get_chat(d[0])
                await bot.send_message(message.from_user.id, f"{chat_d.title}\nID: {chat_d.id}\n\nПодсчет сообщений {'выключен' if d[2]==0 else 'включён'}\n\nСообщение под посты: \n{'[Не задано]' if len(d[1])<1 else d[1]}")

            await bot.send_message(message.from_user.id,f"Для включения подсчета сообщений в чате напишите /count <id>\n\nДля создания сообщения, что будет писаться под каждым постом напишите /message <id>\n\nУбрать чат из списка (бот выйдет из чата) /remove <id>")

@dp.message(Command("count"))
async def count(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            id = int(message.text.replace('/count ', ''))
            if id > 0:
                id *= -1
            if db.is_chat_exists(id):
                db.toggle_count(id)
                chat_d = await bot.get_chat(id)
                await bot.send_message(message.from_user.id,
                                       f"Теперь в чате {chat_d.title} {'подсчитываются сообщения' if db.is_count(id) else 'сообщения не подсчитываются'}")
            else:
                    await bot.send_message(message.from_user.id,"Нет такого чата..")

@dp.message(Command("newlist"))
async def new_list(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            db.set_adm_state(message.from_user.id,M_LIST_NAME)
            await bot.send_message(message.from_user.id, "Введите название нового списка\n\nДля отмены /cancel")

@dp.message(Command("message"))
async def message(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            global chat_to_work
            id = int(message.text.replace('/message ', ''))
            if id > 0:
                id *= -1

            chat_to_work = id

            db.set_adm_state(message.from_user.id, M_CHATS_SER_MSG)
            await bot.send_message(message.from_user.id, "Введите сообщение, которое будет писаться под постами канала. \nЧтобы удалить предыдущее сообщение - напишите \"None\" \n\nДля отмены напишите /cancel.")

chat_to_work = 0

@dp.message(Command("remove"))
async def remove(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            try:
                id = int(message.text.replace('/remove ',''))
                if id > 0:
                    id*=-1

                await bot.leave_chat(id)
                db.remove_chat(id)

                await bot.send_message(message.from_user.id,"Чат удален!")
            except Exception as e:
                name = message.text.replace('/remove ','')
                db.remove_list(name)
                await bot.send_message(message.from_user.id,"Список удален!")

@dp.message(Command("call"))
async def lists(msg: types.Message):
    if msg.chat.type != "private":
        if msg.from_user.id in adm_list:
            name = msg.text.replace('/call ','')
            if(len(name)>0):
                list = db.get_list(name)
                await bot.send_message(msg.chat.id, f"Призыв списка {name}!")
                s = ""
                count = 0
                for l in list:
                    s+=f"[прив](tg://user?id={l})\n"
                    count+=1
                    if(count==4):
                        await bot.send_message(msg.chat.id, s, parse_mode="MarkdownV2")
                        await asyncio.sleep(1)
                        s = ""
                        count = 0
            else:
                await bot.send_message(msg.chat.id, f"Призыв чата! (в разработке........)")

@dp.message(Command("clear"))
async def clear(msg: types.Message):
    if msg.chat.type == "private":
        if msg.from_user.id in adm_list:
            db.clear_messages()
            await bot.send_message(msg.chat.id, "Данные обнулены!")

@dp.message(Command("users"))
async def lists(msg: types.Message):
    if msg.chat.type == "private":
        if msg.from_user.id in adm_list:
            count = 9999999 if msg.text=='/users' else int(msg.text.replace('/users ',''))
            us = db.get_users_lookfor(count)
            res = f"Пользователи, написавшие меньше {count} сообщений:\n"
            for u in us:
                res+=f"[{protect(u[1])}](tg://user?id={u[0]}) \\- {u[2]}\n"
            res += protect("\n/clear - для очистки количества сообщений")
            await bot.send_message(msg.chat.id, res, parse_mode="MarkdownV2")

def protect(text):
    return text.replace("_", "\\_").replace("!", "\\!").replace(".", "\\.").replace("{", "\\{").replace("}", "\\}").replace("|", "\\|").replace("=", "\\=").replace("-", "\\-").replace("+", "\\+").replace("#", "\\#").replace(">", "\\>").replace("`", "\\`").replace("~", "\\~").replace("(", "\\(").replace(")", "\\)").replace("[", "\\[").replace("]", "\\]").replace("*", "\\*")



@dp.message(Command("lists"))
async def lists(msg: types.Message):
    if msg.chat.type == "private":
        if msg.from_user.id in adm_list:
            lists = db.get_lists()
            res = "Существующие списки:\n"
            for l in lists:
                res+=f"{l[0]} - {len(l[1].split())} участников\n"

            if(len(lists)==0):
                res+="[Списков еще нет - /newlist для создания нового списка]\n"

            res+="\n/remove <название> - чтобы удалить список"
            await bot.send_message(msg.from_user.id, res)
@dp.message(Command("done"))
async def done(msg: types.Message):
    if msg.chat.type == "private":
        if msg.from_user.id in adm_list:
            u_id = msg.from_user.id
            mode = db.get_adm_state(u_id)
            if mode==M_LIST_USERS:
                db.set_adm_state(u_id,M_NONE)
                if len(list_users)>0:
                    res = ""
                    for c in list_users:
                        res+=f"{c} "
                    db.new_list(list_name,res)
                    await bot.send_message(u_id, f"Список {list_name} создан!")
                else:
                    await bot.send_message(u_id, f"Список не создан, слишком мало участников!")

@dp.message(Command("debug"))
async def debug(message: types.Message):
    db.debug()


@dp.message()
async def any(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id in adm_list:
            if(message.reply_to_message):
                if message.reply_to_message.forward_from:
                    await message.forward(message.reply_to_message.forward_from.id)
                    await bot.send_message(message.from_user.id, "Сообщение отправлено!")
                    return

            await process_action(message)

        else:
            for admin in adm_list:
                await message.forward(admin)
            await bot.send_message(message.from_user.id, "Сообщение отправлено!")
    else:
        ch_id = message.chat.id
        if not db.check_chat(ch_id):
            for admin in adm_list:
                await bot.send_message(admin, f"Добавлен новый чат - {(await bot.get_chat(ch_id)).title}")

        u_id = message.from_user.id

        if not db.check_user(u_id,message.from_user.first_name,db.is_count(message.chat.id)):
            for admin in adm_list:
                await bot.send_message(admin, f"В базу данных добавлен новый пользователь - {message.from_user.first_name}")
        if db.is_count(message.chat.id):
            db.lookfor(u_id)
            db.add_message(u_id)


list_name = ""
list_users = []

async def  process_action(msg:types.Message):
    u_id = msg.from_user.id
    mode = db.get_adm_state(u_id)
    global list_users
    if mode == M_ADMIN:
        try:
            if msg.forward_from:
                if msg.forward_from.id not in adm_list:
                    db.new_admin(msg.forward_from.id)
                    await bot.send_message(msg.from_user.id,"Новый админ добавлен!")
                    adm_list.append(msg.forward_from.id)
                    return
            else:#if await bot.get_chat(int(msg.text)):
                if int(msg.text) not in adm_list:
                    db.new_admin(int(msg.text))
                    await bot.send_message(msg.from_user.id,"Новый админ добавлен!")
                    adm_list.append(int(msg.text))
                    return
        except Exception as e:
            pass
        await bot.send_message(msg.from_user.id,"Не получилось чего-то")
    elif mode == M_REMOVE_ADMIN:
        try:
            if msg.forward_from:
                if msg.forward_from.id in adm_list and u_id !=msg.forward_from.id:
                    db.remove_admin(msg.forward_from.id)
                    await bot.send_message(msg.from_user.id,"Админ исключен.")
                    adm_list.remove(msg.forward_from.id)
                    return
            else:#if await bot.get_chat(int(msg.text)):
                if int(msg.text) in adm_list and u_id!=int(msg.text):
                    db.remove_admin(int(msg.text))
                    await bot.send_message(msg.from_user.id,"Админ исключен.")
                    adm_list.remove(int(msg.text))
                    return
        except Exception as e:
            pass
        await bot.send_message(msg.from_user.id,"Не получилось чего-то")
    elif mode == M_CHATS_SER_MSG:
        text = msg.text
        if text == "None":
            db.set_message(chat_to_work,'')
        else:
            db.set_message(chat_to_work, text)
        a = await bot.get_chat(chat_to_work)
        await bot.send_message(u_id,f"В чате {a.title} обновлен текст под пост.")
    elif mode == M_LIST_NAME:
        global list_name
        list_name = msg.text
        list_users = []
        await bot.send_message(u_id, f"Отправьте ID (отдельными сообщениями) или перешлите сообщения тех, кто будет в списке {list_name}.\n\n/cancel - для отмены\n/done - по готовности")
        db.set_adm_state(u_id,M_LIST_USERS)
    elif mode == M_LIST_USERS:
        try:
            if msg.forward_from:
                print(f"{msg.forward_from.id} not in {list_users} -> {msg.forward_from.id not in list_users}")
                if msg.forward_from.id not in list_users:
                    list_users.append(msg.forward_from.id)
                    await bot.send_message(msg.from_user.id,f"Пользователей в списке {list_name}: {len(list_users)}")
                    return
            else:#if await bot.get_chat(int(msg.text)):
                print(f"{int(msg.text)} not in {list_users} -> {int(msg.text) not in list_users}")
                if int(msg.text) not in list_users:
                    list_users.append(int(msg.text))
                    await bot.send_message(msg.from_user.id, f"Пользователей в списке {list_name}: {len(list_users)}")
                    return
        except Exception as e:
            print(e)
        await bot.send_message(msg.from_user.id,"Не получилось чего-то")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("BOT STARTED")
    load_data()
    asyncio.run(main())