#!/usr/bin/python3
from flask import Flask, request, render_template, send_from_directory, abort, redirect
import os, requests, random, database, calendar, datetime
import doodlebase
import hashlib
from MySQLdb import IntegrityError

salt = "BäselmaiselIsFunny"

#Config
file = "config.conf"
options = dict()
with open(file) as f:
    content = f.read().splitlines()
    for opt in content:
        opt = opt.split(" ")
        options[opt[0]] = opt[1]

app = Flask(__name__)
app.config.update(
        TEMPLATES_AUTO_RELOAD = True
)

@app.route('/')
def main():
    return "Flask von Ralf"

# Die standard Doodleseite
@app.route('/doodle')
def entry():
    return render_template('doodle/main.html') 

@app.route('/doodle', methods=["POST",])
def join():
    postargs = request.form
    return redirect(f"/doodle/{postargs['link']}")

@app.route('/doodle/create', methods=["GET",])
@app.route('/doodle/create/<int:code>', methods=["GET",])
def createmeetingGet(code=None):
    return render_template('doodle/createdoodle.html', code=code)

@app.route('/doodle/create', methods=["POST",])
@app.route('/doodle/create/<int:code>', methods=["POST",])
def createmeetingPost(code=None):
    postargs = request.form
    if postargs['title'] and postargs['uname'] and postargs['secret']:
        mid  = doodlebase.createDoodle(postargs['title'], postargs['uname'])
        secret = createHash(postargs['secret'])
        doodlebase.addUser(postargs['uname'], mid, secret)
        return redirect(f"/doodle/{mid}/{postargs['uname']}/{secret}")
    return redirect("/doodle/create/4321")

@app.route('/doodle/<mid>', methods=["GET",])
@app.route('/doodle/<mid>/<int:code>', methods=["GET",])
def createuserGet(mid, code=None):
    if not doodlebase.meetingExists(mid):
        return f"meeting {mid} doesn't exist."
    return render_template('doodle/cuname.html', code=code, mid=mid)

@app.route('/doodle/<mid>', methods=["POST",])
@app.route('/doodle/<mid>/<int:code>', methods=["POST",])
def createuserPost(mid, code=None):
    postargs = request.form
    if not postargs['secret'] or not postargs['uname']: 
        return redirect(f"/doodle/{mid}/4321")
    uname  = postargs['uname']
    secret = createHash(postargs['secret'])
    if doodlebase.userExists(mid, uname):
        return redirect(f"/doodle/participate/{mid}/{uname}/{secret}")
    else:
        doodlebase.addUser(uname, mid, secret)
        return redirect(f"/doodle/participate/{mid}/{uname}/{secret}")

    
@app.route('/doodle/participate/<mid>/<uname>/<secret>', methods=['GET',])
@app.route('/doodle/participate/<mid>/<uname>/<secret>/<success>', methods=['GET',])
@app.route('/doodle/participate/<mid>/<uname>/<secret>/<int:navyear>/<int:navmonth>/<int:navday>', methods=['GET',])
@app.route('/doodle/participate/<mid>/<uname>/<secret>/<int:navyear>/<int:navmonth>/<int:navday>/<success>', methods=['GET',])
def participate(mid, uname, secret, navday=None, navmonth=None, navyear=None, success=None):
    if not doodlebase.meetingExists(mid):
        return f"""
        Meeting {mid} doesn't exist. <a href="/doodle">return to start page</a>"""
    if secret != doodlebase.getSecret(mid, uname):
        return redirect(f"/doodle/{mid}/1234")
    if doodlebase.isOwner(uname, mid):
        return redirect(f"/doodle/{mid}/{uname}/{secret}")
    else:
        agreed = [i[0] for i in doodlebase.getZeiträumeOfUser(uname=uname, mid=mid)]
        zeiträume = list(doodlebase.getZeiträumeVonMeeting(mid))
        xD = [None for _ in range(len(zeiträume))] #Hilfsvariable für existingDates
        for i in range(len(zeiträume)): #Alle erstellten Zeiträume werden angemessen formattiert.
            zeiträume[i] = list(zeiträume[i])
            part = zeiträume[i]
            part[2] = part[2].strftime("📅 %d.%m.%Y ⏰ %H:%M")
            xD[i] = [part[2].split()[1].split(".")] # , part[2].split()[3].split(".") / jedes belegte Datum (Zeit auskommentiert) wird separat in einer list gespeichert.
            part[3] = part[3].strftime("📅 %d.%m.%Y ⏰ %H:%M")
        existingDates = [str(i[0][0]+i[0][1]+i[0][2]) if int(i[0][0])>9 else str(i[0][0][1:2]+i[0][1]+i[0][2]) for i in xD] #die Daten werden von list zu string konvertiert f(24122002)
        if navyear is None or navmonth is None or navday is None:
            heute   = datetime.date.today()
            navdate = (heute.year, heute.month, heute.day)
        else:
            navdate = (navyear, navmonth, navday)
        cal=calendar.month(navdate[0], navdate[1]) #Text-Kalendar (string) eines angegebenen Monats
        if int(navdate[1]) < 12: #Um den nächsten Monat zu berechnen wird auf Jahresübergänge geachtet
            cal2 = calendar.month(navdate[0], navdate[1]+1)
        else:
            cal2 = calendar.month(navdate[0]+1, 1)
        month1     = [x.split() for x in cal.split("\n")] #Kalendar wird in 2D list gespalten. [0] ist (Jahr, Monat), [1] ist ("Mo", "Tu",...), Rest jeweils eine volle Woche (int für Tagesdatum).
        month2     = [x.split() for x in cal2.split("\n")]
        calendars  = [month1, month2]
        users      = [(doodlebase.getUsersOfZeitraum(i[0])) for i in zeiträume] #Es werden für alle Zeitärume alle Nutzer gespeichert, die zugesagt haben.
        userCounts = [(doodlebase.getUserAmount(i[0])) for i in zeiträume] #Es werden für alle Zeiträume jede Nutzeranzahl ^
        mtitle     = doodlebase.getTitle(mid)
        selfLink   = options['SERVERNAME'] #link zum webserverhost zB. maximilian_djubajlo.goetheschule-ldk.de:22008
        prev       = [navdate[0] if navdate[1]>1 else navdate[0]-1, 12 if navdate[1]==1 else navdate[1]-1]
        next       = [navdate[0] if navdate[1]<12 else navdate[0]+1, 1 if navdate[1]==12 else navdate[1]+1]
        mm         = (f"0{navdate[1]}" if navdate[1]<10 else navdate[1], f"0{next[1]}" if next[1]<10 else next[1])
        return render_template("/doodle/participate.html", mid=mid, secret=secret, uname=uname,  monate=calendars, mm=mm, prevnext=[prev, next], context=zeiträume, user=users, userCounts=userCounts, meetingTitle=mtitle, selfLink=selfLink, agreed = agreed, success = str(success is not None), existingDates=existingDates)
    
# nicht möglich, navbuttons und calendars zu mergen, da calendars die Monate als String speichert (zB. "May" statt int "5")
# daher auch mm, welches den jetzigen und nächsten Monat als int speichert.

    
@app.route('/doodle/participate/<mid>/<uname>/<secret>', methods=['POST',])
@app.route('/doodle/participate/<mid>/<uname>/<secret>/<success>', methods=['POST',])
@app.route('/doodle/participate/<mid>/<uname>/<secret>/<int:navyear>/<int:navmonth>/<int:navday>', methods=['POST',])
@app.route('/doodle/participate/<mid>/<uname>/<secret>/<int:navyear>/<int:navmonth>/<int:navday>/<success>', methods=['POST',])
def agreeto(mid, uname, secret, navday=None, navmonth=None, navyear=None, success=None):
    postargs = request.form
    zeiträume = postargs.getlist('zeitraum', type=int) #alle ausgewählten Checkboxen (Zeiten, denen man zustimmt)
    doodlebase.agreeToZeitraum(uname, mid, zeiträume) #Datenbankeintrag
    if navyear is None or navmonth is None or navday is None:
        return redirect(f"/doodle/participate/{mid}/{uname}/{secret}/success")
    else:
        return redirect(f"/doodle/participate/{mid}/{uname}/{secret}/{navyear}/{navmonth}/{navday}/success")


#Für Dokumentation, siehe '/doodle/participate/<mid>/<uname>/<secret>'.
@app.route('/doodle/<mid>/<uname>/<secret>', methods=['GET', 'POST'])
@app.route('/doodle/<mid>/<uname>/<secret>/<int:navyear>/<int:navmonth>/<int:navday>', methods=['GET', 'POST'])
def owner(mid, uname, secret, navday=None, navmonth=None, navyear=None):
    if not doodlebase.meetingExists(mid):
        return f"meeting {mid} doesn't exist."
    if not doodlebase.isOwner(uname, mid):
        return "Sie sind nicht der Besitzer des Meetings!"
    postwerte = request.form
    if(doodlebase.getSecret(mid, uname)!=secret):
        return "wrong password"
    if navyear is None or navmonth is None or navday is None:
        heute   = datetime.date.today()
        navdate = (heute.year, heute.month, heute.day)
    else:
        navdate = (navyear, navmonth, navday)
    if postwerte: #Timestamps werden angemessen konvertiert und verarbeitet
        st      = [int(x) if x else 0 for x in postwerte['mystarttime'].split(":")]
        et      = [int(x) if x else 0 for x in postwerte['myendtime'].split(":")]
        start   = datetime.datetime(*navdate, *st, 0, 0).strftime("%Y.%m.%d %H:%M")
        enddate = datetime.date(*navdate) if postwerte['mystarttime'] < postwerte['myendtime'] else datetime.date(*navdate) + datetime.timedelta(days=1) #nächster Tag falls endzeit nach 00:00 wenn startzeit vor 00:00
        endday  = (enddate.year, enddate.month, enddate.day)
        ende    = datetime.datetime(*endday, *et, 0, 0).strftime("%Y.%m.%d %H:%M")
        doodlebase.addTime(mid, start, ende) 

    cal=calendar.month(navdate[0], navdate[1])
    if int(navdate[1]) < 12:
        cal2 = calendar.month(navdate[0], navdate[1]+1)
    else:
        cal2 = calendar.month(navdate[0]+1, 1)
    month1     = [x.split() for x in cal.split("\n")]
    month2     = [x.split() for x in cal2.split("\n")]
    calendars  = [month1, month2]
    prev       = [navdate[0] if navdate[1]>1 else navdate[0]-1, 12 if navdate[1]==1 else navdate[1]-1]
    next       = [navdate[0] if navdate[1]<12 else navdate[0]+1, 1 if navdate[1]==12 else navdate[1]+1]
    navbuttons = [prev, next]
    zeiträume = list(doodlebase.getZeiträumeVonMeeting(mid))
    existingDates = [None for _ in range(len(zeiträume))]
    for i in range(len(zeiträume)):
        zeiträume[i] = list(zeiträume[i])
        part = zeiträume[i]
        part[2] = part[2].strftime("📅 %d.%m.%Y ⏰ %H:%M")
        existingDates[i] = [part[2].split()[1].split(".")] # , part[2].split()[3].split(".")
        part[3] = part[3].strftime("📅 %d.%m.%Y ⏰ %H:%M")
    xD = [str(i[0][0]+i[0][1]+i[0][2]) if int(i[0][0])>9 else str(i[0][0][1:2]+i[0][1]+i[0][2]) for i in existingDates]
    users      = [(doodlebase.getUsersOfZeitraum(i[0])) for i in zeiträume]
    userCounts = [(doodlebase.getUserAmount(i[0])) for i in zeiträume]
    mtitle     = doodlebase.getTitle(mid)
    selfLink   = options['SERVERNAME']
    mm         = (f"0{navdate[1]}" if navdate[1]<10 else navdate[1], f"0{next[1]}" if next[1]<10 else next[1])
    return render_template('doodle/ownerview.html', mid=mid, secret=secret, uname=uname, navdate=navdate, monate=calendars, mm=mm, prevnext=navbuttons, context=zeiträume, user=users, userCounts=userCounts, meetingTitle=mtitle, selfLink=selfLink, existingDates=xD)

@app.route('/doodle/deleteMeeting', methods=['GET',])
def deleteMeeting():
    args = request.args
    doodlebase.deleteMeeting(args['mid'])
    return render_template('doodle/main.html', delete="Del")
    
@app.route('/doodle/delete', methods=['GET',])
def deleteZeitraum():
    args = request.args
    doodlebase.deleteZeitraum(args['zid']) #löscht einen Zeitraum
    return redirect(args['origin']) #wird zur Ursprungsseite (Erstellerseite) zurückgeleitet

def createHash(clear):
    return hashlib.sha512((salt + hashlib.sha512(clear.encode()).hexdigest()).encode()).hexdigest() #Doppelt gehashter String (des Passwortes) mit Salt

# Nur damit zu Hause flask auch alleine laufen kann.
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=8080)
