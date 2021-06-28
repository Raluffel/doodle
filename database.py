#!/usr/bin/python3
import MySQLdb as mysql # keine Lust auf komplizierte Groß/Kleinschreibung
from sys import argv

host   = 'localhost'
user   = 'ilk'
passwd = 'nichtgoethe'
db     = 'beslilk'

def tabelle_als_text(table):
    # Connection, Cursor, Result
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()

    # Wir brauchen die Spaltennamen...
    cur.execute("explain %s" % table)
    names = tuple(x[0] for x in cur.fetchall())
    # ... und natürlich alle Zeilen
    cur.execute("select * from %s" % table)
    zeilen = cur.fetchall()

    # Längsten Eintrag in jeder Spalte suchen (plus 1 Leerzeichen)
    lang = [0]*len(names)
    for i, spalte in enumerate(names):
        lang[i] = max(lang[i], 1+len(str(spalte)))
    for zeile in zeilen:
        for i, spalte in enumerate(zeile):
            lang[i] = max(lang[i], 1+len(str(spalte)))

    # Namensspalte und Trennstrich ausgeben
    for i, spalte in enumerate(names):
        print(spalte.ljust(lang[i]), end='')
    print('\n' + '-'*sum(lang))

    # Tabelleninhalt ausgeben
    for zeile in zeilen:
        for i, spalte in enumerate(zeile):
            print(str(spalte).ljust(lang[i]), end='')
        print()

    # Aufräumarbeiten
    con.close()

def getTabellen():
    #Verbindung
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    
    #Tabellen sammeln
    cur.execute("show tables")
    result = [x[0] for x in cur.fetchall()]
    con.close()
    return result

def getTabelleFürFlask(name):
    #Verbindung
    con = mysql.connect(host, user, passwd, db)
    cur = con.cursor()
    
    cur.execute("explain %s" % name)
    result = (tuple(x[0] for x in cur.fetchall()),)
    
    cur.execute(f"select * from {name}")
    result = result + cur.fetchall()
    con.close()
    return result
    
    

if __name__ == '__main__':
    #tabelle_als_text(argv[1])
    print(getTabelleFürFlask(argv[1]))
