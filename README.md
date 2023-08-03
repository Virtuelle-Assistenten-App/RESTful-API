# Virtuelle Assistenten-App RESTful API

Die Virtuelle Assistenten-App RESTful API ermöglicht die Kommunikation zwischen dem Frontend und dem Backend der App.
Sie stellt verschiedene Endpunkte bereit, um Aufgaben zu verwalten, Ereignisse im Kalender zu speichern, Benutzer zu
authentifizieren und mehr.

## Installation

1. Stelle sicher, dass Python 3.x auf deinem System installiert ist.
2. Installiere die erforderlichen Python-Abhängigkeiten mit dem Befehl:

```bash
pip install -r requirements.txt
```

## Endpunkte

* `POST /v1/auth/login`: Authentifiziert einen Benutzer über Github und gibt ein JWT-Token zurück.
* `POST /v1/auth/logout`: Meldet einen Benutzer ab und löscht das JWT-Token.

## Fehlerbehandlung

Die API gibt entsprechende HTTP-Statuscodes und Fehlermeldungen zurück, um auf fehlerhafte Anfragen zu reagieren. Wenn
ein Fehler auftritt, wird die Fehlermeldung im JSON-Format zurückgegeben.

## Beitragende

Wir freuen uns über Beiträge zur Verbesserung der API. Bitte erstelle einen Pull Request, um deine Änderungen
einzubringen. Stelle sicher, dass du die erforderlichen Tests durchgeführt hast und die Code-Qualitätsstandards
einhältst.

Lizenz
Diese RESTful API ist unter der **MIT-Lizenz** lizenziert. Siehe die LIZENZ Datei für weitere Informationen