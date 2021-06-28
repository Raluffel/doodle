# python Dateien

## myflask/doodleflask.py

*global variables*
* salt: ein hash-Attribut zum komplexeren Verschlüsseln, Inhalt irrelevant
* file: Referenz zu Webserver Attributen, welche in config.conf gespeichert sind.
* options: überträgt jede Zeile in ein dictionary, welche in config.conf mit dem Format "{key} {content}" gespeichert ist

*def entry():*
* http://maximilian_djubajlo.goetheschule-ldk.de:22008/doodle
* Startseite mit Auswahl: Doodle erstellen/Doodle beitreten (per `mid`).
* GET zu def `join()`

*def join():*
* Beitritt durch Startseite, meeting id wird gelesen und leitet entsprechend weiter.
* POST zu `entry()`

*def createuserget(code=None):*
* http://maximilian_djubajlo.goetheschule-ldk.de:22008/doodle/create
* Parameter
* * `code`: gibt der template mit, welchen Fehler (falls überhaupt einen) sie anzeigen soll.
* Erstellerseite von /doodle, per href hierher weitergeleitet. Man erstellt ein meeting mit Titel, Nutzername, Passwort.
* GET zu `createmeetingPost`

*def createuserpost(code=None):*
* redirect zu `createuserget(code)`, falls post-werte fehlen, sonst trägt es diese in die Datenbank ein.
* post-werte: `title` (meeting name), `uname` (username), `secret` (password)
* POST zu `createmeetingGet`

*def createuserGet(mid, code=None):*
* Parameter
* * `mid`: meeting-ID zur identifizierung welchem meeting man beitritt.
* * `code`: falls vorhanden, Fehlercode für fehlgeschlagene Anmeldung
* Seite zum Nutzer erstellen für ein spezifisches Meeting `mid`
* GET zu `createuserPost`

*def createuserPost(mid, code=None):*
* bei fehlerhaften Anmeldedaten redirect zu `createuserGet`
* Falls fehlerfreie Daten, erstellt einen Nutzer, falls es ihn noch nicht gibt, sonst wird er angemeldet, indem er auf `participate` weitergeleitet wird.
* POST zu `createUserGet`

*def participate(mid, uname, secret, navday=None, navmonth=None, navyear=None, success=None):*
* Parameter:
* * `mid`: meeting ID
* * `uname`: Nutzername
* * `secret`: Nutzer Passwort
* * `navday`, `navmonth`, `navyear`: das anzuzeigene Datum
* * `success`: Bestätigungsnachricht, dass eine Post-aktion erfolgreich verlaufen ist.
* Überprüfungen zum sicheren weiteren Vorgehen
* * Fehlernachricht falls meeting nicht existiert.
* * redirect zu `createuserGet` mit Fehlercode falls ein falsches Passwort eingegeben wurde.
* * redirect zu `owner` falls user der Veranstalter ist.
* Abruf/Erstellung von Daten für das template
* * `mid` = meeting id
* * `secret` = passwort
* * `uname` = Nutzername
* * `monate` = calendars
* * `mm`= Tuple von dem aktuellen Monat und dem nächsten Monat als Zahlenwerte
* * `prevnext` = vorheriger und nächster Monat als Zahlenwerte
* * `context` = Zeiträume des meetings `mid`, die vom Veranstalter festgelegt wurden.
* * `user` = Für jeden Zeitraum; Nutzer, die zugesagt haben
* * `userCounts` = Für jeden Zeitraum: Anzahl an Nutzern, die zugesagt haben
* * `meetingTitle` = Titel des meetings
* * `selfLink` = Link zum webserverhost
* * `agreed` = Zeiträume, denen der Nutzer `uname` zugesagt hat
* * `success` = "True" wenn Veränderung erfolgreich vorgenommen, sonst "False"
* * `existingDates` = list von Daten, an denen es Zeiträume gibt.
* GET zu `agreeto`

*def agreeto(mid, uname, secret, navday=None, navmonth=None, navyear=None, success=None)*
* kriegt alle Checkboxen übergeben, die an `doodlebase.agreeToZeitraum` weitergegeben werden, um in die Datenbank als entsprechende Einträge verarbeitet werden.
* redirect nach `participate`
* POST zu `participate`

*def owner(mid, uname, secret, navday=None, navmonth=None, navyear=None):*
* Parameter:
* * `mid`: meeting ID
* * `uname`: Nutzername
* * `secret`: Nutzer Passwort
* * `navday`, `navmonth`, `navyear`: das anzuzeigene Datum
* * `success`: Bestätigungsnachricht, dass eine Post-aktion erfolgreich verlaufen ist.
* Überprüfungen zum sicheren weiteren Vorgehen
* * Fehlernachricht falls meeting nicht existiert.
* * Fehlernachricht falls user nicht der Veranstalter ist.
* Abruf/Erstellung von Daten für das template
* * `mid` = meeting id
* * `secret` = passwort
* * `uname` = Nutzername
* * `monate` = 3D array von Monaten als Kalendar
* * `mm`= Tuple von dem aktuellen Monat und dem nächsten Monat als Zahlenwerte
* * `prevnext` = vorheriger und nächster Monat als Zahlenwerte
* * `context` = Zeiträume des meetings `mid`, die vom Veranstalter festgelegt wurden.
* * `user` = Für jeden Zeitraum; Nutzer, die zugesagt haben
* * `userCounts` = Für jeden Zeitraum: Anzahl an Nutzern, die zugesagt haben
* * `meetingTitle` = Titel des meetings
* * `selfLink` = Link zum webserverhost
* * `agreed` = Zeiträume, denen der Nutzer `uname` zugesagt hat
* * `success` = "True" wenn Veränderung erfolgreich vorgenommen, sonst "False"
* * `existingDates` = list von Daten, an denen es Zeiträume gibt.

*def deleteMeeting():*
* löscht das meeting aus der Datenbank und zeigt startseite mit Bestätigungsnachricht an.

*def deleteZeitraum():*
* löscht einen Zeitraum aus der Datenbank

*def createHash(clear):*
* generiert eine Verschlüsselung für ein Passwort

## myflask/doodlebase.py
Für die Interaktion mit der Datenbank bitte mit dok_doodlebase.md fortfahren.