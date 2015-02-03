# Unifi Fokus Log Script

## Installation

Checkout der Quellen in das Zielverzeichnis mittels Git zur Versionskontrolle. Eventuell muss noch der SSH Key der Production Maschine in Gitlab hinterlegt werden um die Quellen zu ziehen.

```
git clone git@gitlab.fokus.fraunhofer.de:vst/unifi-fokus.git
```

Fuer das Script `unifilog.py` muss ein CronJob eingerichtet werden, der alle n Minuten aufgerufen wird.

## Syntax des Scripts

```
python unifilog.py -h
usage: unifilog.py [-h] [-c CONTROLLER] [-u USER] [-p PASSWORD] [-a]

optional arguments:
-h, --help            show this help message and exit
-c CONTROLLER, --controller CONTROLLER
specifies host of the controller
-u USER, --user USER  specifies username for controller access
-p PASSWORD, --password PASSWORD
specifies password for controller access
-a, --getall          fetches the complete event data from controller
```

Das Script wird mit den oben genannten Argumenten gestartet.

  * `-h` oder `--help` um Hilfe zu erhalten
  * `-c` oder `--controller` zur Spezifikation des API Endpoints
  * `-u` oder `--user` zur Spezifikation des Nutzernamens des Unifi Servers
  * `-p` oder `--password` zur Spezifikation des Passwortes fuer den Unifi Server

Als besonderes Attribut fuer den initialen Aufruf

  * `-a` oder `--getall` zum sammeln aller auf dem Unifi Server verfuegbaren Events

Das `-a` Attribut sollte nur bei erster Verwendung des Scripts genutzt werden. Sofern ein Aufruf im Nachhinein erfolgt, werden alle verfuegbaren Logdaten erneut in das Logfile geschrieben und somit doppelte Eintraege erzeugt.

Wird initial auf das Aufrufen mit `-a` verzichtet, werden nur Daten der letzten 10 Minuten abgerufen und im Logfile gespeichert, auch wenn noch keines existiert.

## Hinweise

Das Script legt zwei Dateien mit seinem Aufruf an. Zum einen ist es eine `unifi.log` Datei, welche die eigentlichen Logdaten beinhaltet.
Die zweite Datei ist `unifitimestamp.cfg`. Hier wird der Zeitstempel des letzten Scriptaufrufes gespeichert um sicherzustellen, dass alle ab diesem Zeitpunkt erzeugten Events erfasst werden.

## TODO

* Logdateipfad als Argument bei Scriptaufruf
* Unifi Statistics mit `get_statistics_24h(self, endtime)`

## LICENSE

Copyright (C) 2015 Philipp Jaeckel - Fraunhofer FOKUS

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

- The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

unifi-api in subdirectory unifi is part of https://github.com/calmh/unifi-api
Copyright (c) 2012 bei Jakob Borg
