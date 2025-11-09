import sqlite3

#создать базу данных\проверить существование

conn = sqlite3.connect("database.db")
curs = conn.cursor()

def init_db():
    global conn
    global curs

    curs.execute('''
    CREATE TABLE IF NOT EXISTS banned(
    id INTEGER
    )
    ''')

    curs.execute('''CREATE TABLE IF NOT EXISTS Users(
    id INTEGER,
    name TEXT,
    msg INTEGER,
    mutes INTEGER,
    lookfor BOOLEAN
    )''')
    curs.execute('''CREATE TABLE IF NOT EXISTS Admins(
    id INTEGER,
    currMode INTEGER
    )''')
    curs.execute('''CREATE TABLE IF NOT EXISTS Chats(
    id INTEGER,
    rules TEXT,
    count BOOLEAN
    )''')
    curs.execute('''CREATE TABLE IF NOT EXISTS Lists(
    name TEXT,
    users TEXT
    )''')#Для созывов

    #curs.execute('''ALTER TABLE Chats ADD COLUMN greet TEXT''')
    #debug()
    conn.commit()

#Админы



def get_admins():
    curs.execute('SELECT id FROM Admins')
    return curs.fetchall()

#Пользователи

#Проверить пользователя, если нет - добавить
def check_user(id,name=0,lookfor = False):
    curs.execute('SELECT * FROM Users WHERE id = ?', (id,))
    if(len(curs.fetchall())<=0):
        curs.execute('INSERT INTO Users (id,name,msg,mutes,lookfor) VALUES (?,?,0,0,?)',(id,name,lookfor))
        conn.commit()
        return False
    return True



#Добавить сообщение в счетчик
def lookfor(id):
    check_user(id)
    curs.execute('UPDATE Users SET lookfor=true WHERE id=?', (id,))
    conn.commit()

def not_lookfor(id):
    check_user(id)
    curs.execute('UPDATE Users SET lookfor=false     WHERE id=?', (id,))
    conn.commit()

def add_message(id):
    check_user(id)
    curs.execute('UPDATE Users SET msg = msg+1 WHERE id=? and lookfor=true',(id,))
    conn.commit()

def clear_messages():
    curs.execute('UPDATE Users SET msg = 0')
    conn.commit()

#Добавить новый список
def new_list(name,list):
    curs.execute("INSERT INTO Lists(name, users) VALUES (?,?)",(name,str(list)))
    conn.commit()

def new_admin(id):
    curs.execute("INSERT INTO Admins(id, currMode) VALUES (?,0)",(id,))
    conn.commit()

def remove_admin(id):
    curs.execute("DELETE FROM Admins WHERE id = ?",(id,))
    conn.commit()

def remove_chat(id):
    curs.execute("DELETE FROM Chats WHERE id = ?",(id,))
    conn.commit()

def remove_list(name):
    curs.execute("DELETE FROM Lists WHERE name = ?",(name,))
    conn.commit()

def remove_user(id):
    curs.execute("DELETE FROM Users WHERE id = ?", (id,))

def is_chat_exists(id):
    curs.execute('SELECT * FROM Chats WHERE id = ?', (id,))
    if (len(curs.fetchall()) <= 0):
        return False
    return True


def check_chat(id):
    curs.execute('SELECT * FROM Chats WHERE id = ?', (id,))
    if (len(curs.fetchall()) <= 0):
        curs.execute("INSERT INTO Chats(id, rules,greet,count) VALUES (?,'','',false)",(id,))
        conn.commit()
        return False
    return True

def is_count(id):
    curs.execute('SELECT count FROM Chats WHERE id = ?', (id,))
    return curs.fetchall()[0][0]

def toggle_count(id):
    curs.execute('UPDATE Chats SET count = ? WHERE id = ?', (not is_count(id),id))
    conn.commit()
    return True

def set_message(id,message):
    curs.execute('UPDATE Chats SET rules = ? WHERE id = ?', (message, id))
    conn.commit()

def set_greet(id,message):
    curs.execute('UPDATE Chats SET greet = ? WHERE id = ?', (message, id))
    conn.commit()

def get_greet(id):
    curs.execute('SELECT greet FROM Chats WHERE id==?', (id,))
    return curs.fetchall()

def debug():
    #curs.execute('''ALTER TABLE Chats ADD COLUMN greet TEXT''')
    curs.execute("UPDATE Chats SET greet = \"\" WHERE id!=0")
    conn.commit()

def get_chats():
    curs.execute('SELECT * FROM Chats')
    return curs.fetchall()

def get_users(msgs=9999999999):
    curs.execute('SELECT id,name,msg FROM Users WHERE msg<?',(msgs,))
    return curs.fetchall()

def get_users_lookfor(msgs=9999999999):
    curs.execute('SELECT id,name,msg FROM Users WHERE msg<? and lookfor=true',(msgs,))
    return curs.fetchall()

def get_lists():
    curs.execute('SELECT * FROM Lists')
    return curs.fetchall()


def set_adm_state(id,mode):
    curs.execute('UPDATE Admins SET currMode = ? WHERE id=?', (mode,id))
    conn.commit()

def get_adm_state(id):
    curs.execute('SELECT currMode FROM Admins WHERE id=?',(id,))
    return curs.fetchall()[0][0]

def get_list(name):
    curs.execute('SELECT users FROM Lists WHERE name=?', (name,))
    return curs.fetchall()[0][0].split()

def get_banned():
    curs.execute('SELECT id FROM banned')
    ar = curs.fetchall()
    arret = []
    for a in ar:
        arret.append(a[0])
    return arret

def ban(id):
        curs.execute("INSERT INTO banned(id) VALUES (?)", (id,))
        conn.commit()

def get_all_ids():
    curs.execute('SELECT id FROM Users WHERE id > 0')
    return curs.fetchall()

def get_all_chat_ids():
    curs.execute('SELECT id FROM Chats')
    return curs.fetchall()

def get_count_chat_ids():
    curs.execute('SELECT id FROM Chats WHERE count = true')
    return curs.fetchall()

def unban(id):
    curs.execute("DELETE FROM banned WHERE id = ?",(id,))
    conn.commit()
