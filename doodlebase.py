#!/usr/bin/python3
import MySQLdb as mysql #keine Lust auf komplizierte Groß/Kleinschreibung
import random, string

host   = 'localhost'
user   = 'ralf'
passwd = 'icqv'
db     = 'sch_ralf'

def createDoodle(mname, owner):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    
    #Testet auf Schonvorhandensein
    while(True):
        id=newId()
        cur.execute(f"select mid from meeting where mid='{id}';")
        if len(cur.fetchall()) == 0:
            break

    #Fügt meeting hinzu
    sql=f"insert into meeting(mid, mname, owner) values('{id}', '{mname}', '{owner}');"
    cur.execute(sql)
    con.commit()
    con.close()
    return id

def deleteMeeting(mid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"delete from meeting where mid='{mid}';"
    cur.execute(sql)
    con.commit()
    con.close()

def addTime(mid, startzeit, endzeit):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"insert into zeitraum(mid, start, ende) values('{mid}', '{startzeit}', '{endzeit}');"
    cur.execute(sql)
    con.commit()
    con.close()

def addUser(uname, mid, usersecret):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    secret = usersecret
    sql = "insert into user(uname, mid, secret) values('{}', '{}', '{}');".format(uname, mid, secret)
    cur.execute(sql)
    con.commit()
    con.close()
    return secret

def getMeeting(mid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = "select * from meeting where mid='{}';".format(mid)
    cur.execute(sql)
    con.close()
    return cur.fetchone()

def meetingExists(mid):
    return bool(getMeeting(mid))

def getZeiträumeVonMeeting(mid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = "select * from zeitraum where mid='{}';".format(mid)
    cur.execute(sql)
    con.close()
    return cur.fetchall()

def getUsersOfZeitraum(zid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"select uname from teilnahme where zid={zid};"
    cur.execute(sql)
    con.close()
    return cur.fetchall()

def getSecret(mid, uname):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"select secret from user where mid='{mid}' and uname='{uname}';"
    cur.execute(sql)
    con.close()
    return cur.fetchone()[0]

def getUser(mid, uname):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"select * from user where mid='{mid}' and uname='{uname}';"
    cur.execute(sql)
    con.close()
    return cur.fetchall()

def getUserAmount(zid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = "select count(uname) from teilnahme where zid={};".format(zid)
    cur.execute(sql)
    con.close()
    return cur.fetchone()[0]

def deleteZeitraum(zid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"delete from teilnahme where zid={zid};"
    cur.execute(sql)
    sql = f"delete from zeitraum where zid={zid};"
    cur.execute(sql)
    con.commit()
    con.close()
    
def getZeiträumeVonMeeting(mid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = "select * from zeitraum where mid='{}';".format(mid)
    cur.execute(sql)
    con.close()
    return cur.fetchall()

def userExists(mid, uname):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"select COUNT(1) from user where mid='{mid}' and uname='{uname}';"
    cur.execute(sql)
    con.close()
    return cur.fetchall()[0][0] == 1

def isOwner(uname, mid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = "select owner from meeting where mid='{}';".format(mid)
    cur.execute(sql)
    con.close()
    return cur.fetchall()[0][0] == uname

def agreeToZeitraum(uname, mid, zids):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    zeiträume = getZeiträumeOfUser(uname, mid)
    for i in zeiträume:
        sql = f"delete from teilnahme where zid={i[0]}"
        cur.execute(sql)
    for i in zids:
        sql = f"insert into teilnahme values('{uname}',{i});"
        cur.execute(sql)
    con.commit()
    con.close()
    
def getZeiträumeOfUser(uname, mid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"""
        select 
        z.zid 
        from 
        ((teilnahme t 
        join zeitraum z on z.zid=t.zid) 
        join user u on u.uname=t.uname) 
        where 
        u.uname='{uname}'
        and
        u.mid='{mid}';
    """
    cur.execute(sql)
    con.close()
    return cur.fetchall()

def getTitle(mid):
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    sql = f"select mname from meeting where mid='{mid}';"
    cur.execute(sql)
    con.close()
    return cur.fetchone()[0]
    
def newId():
    id = ''.join(random.choice(string.ascii_letters) for _ in range(6))
    return id.lower()
    
if __name__ == '__main__':
    print(getMeeting("hihi"))