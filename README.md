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
usage: unifilog.py [-h] [-c CONTROLLER] [-u USER] [-p PASSWORD] [-f FILE]
                   [-t TIMESTAMP]

optional arguments:
  -h, --help            show this help message and exit
  -c CONTROLLER, --controller CONTROLLER
                        host of the UniFi-controller (unifi)
  -u USER, --user USER  username for controller access (ubnt)
  -p PASSWORD, --password PASSWORD
                        password for controller access (ubnt)
  -f FILE, --file FILE  output file for log messages (unifi.log)
  -t TIMESTAMP, --timestamp TIMESTAMP
                        timestamp file (unifitimestamp.cfg)
```

Das Script wird mit den oben genannten Argumenten gestartet.

  * `-h` oder `--help` um Hilfe zu erhalten
  * `-c` oder `--controller` zur Spezifikation des API Endpoints
  * `-u` oder `--user` zur Spezifikation des Nutzernamens des Unifi Servers
  * `-p` oder `--password` zur Spezifikation des Passwortes fuer den Unifi Server
  * `-f` oder `--file` zur Spezifikation des Logfiles (Pfadangaben sind moeglich)
  * `-t` oder `--timestamp` zur Spezifikation der Datei zum Speichern des letzten geloggten Zeitstempels.

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
