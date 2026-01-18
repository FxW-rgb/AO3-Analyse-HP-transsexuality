===========================================
Fanfiction Scraper & Analyzer – README
===========================================

Dieses Projekt dient der automatisierten Sammlung, Aufbereitung und Analyse von Fanfiction-Texten. 
Es besteht aus zwei zentralen Jupyter Notebooks, die aufeinander aufbauen:

1) FanfictionScraper.ipynb  – Datensammlung  
2) FanfcitionAnalyzer.ipynb – Vorverarbeitung und Auswertung der gesammelten Texte  

Diese README-Datei gibt einen übergeordneten Überblick über Zielsetzung, Architektur und Ordnerstruktur des Projekts.
Die detaillierten technischen Vorgehensweisen, Entscheidungen und Code-Erklärungen sind direkt 
in den jeweiligen Notebooks in Form von Markdown-Zellen dokumentiert. 


-------------------------------------------
Projektziel
-------------------------------------------

Ziel des Projekts ist es:

- Fanfiction-Texte automatisiert aus Online-Quellen zu sammeln,
- die Daten strukturiert abzuspeichern und aufzubereiten,
- diese anschließend mit textanalytischen Methoden auszuwerten,
- und die Ergebnisse nachvollziehbar zu dokumentieren.

Das Projekt ist modular aufgebaut: Der Scraper erzeugt die Datenbasis, der Analyzer wertet sie aus.


-------------------------------------------
Zentrale Komponenten
-------------------------------------------

Das Projekt besteht aus zwei Hauptkomponenten:

1. Datensammlung (Scraper)
   ------------------------------------------------
   Notebook: FanfictionScraper.ipynb  

   Aufgaben:
   - Abrufen von Fanfiction-Texten
   - Extraktion relevanter Metadaten (z. B. Titel, Autor, Tags, Länge, etc.)
   - Bereinigung und Strukturierung der Rohdaten
   - Speicherung der Ergebnisse in einem maschinenlesbaren Format

   Details zur konkreten Implementierung finden sich im Notebook selbst.


2. Analyse (Analyzer)
   ------------------------------------------------
   Notebook: FanfcitionAnalyzer.ipynb  

   Aufgaben:
   - Einlesen der zuvor gesammelten Daten
   - Textnormalisierung und Aufbereitung
   - Statistische Auswertungen und Visualisierungen
   - Topic Modeling (LDA)

   Die genauen Methoden und Schritte sind ausführlich im Notebook beschrieben.


-------------------------------------------
Empfohlene Arbeitsreihenfolge
-------------------------------------------

1. Zuerst FanfictionScraper.ipynb ausführen  
2. Anschließend FanfcitionAnalyzer.ipynb öffnen und analysieren  

Der Analyzer setzt voraus, dass die vom Scraper erzeugten Daten bereits vorhanden sind.


-------------------------------------------
Typische Ordnerstruktur (empfohlen)
-------------------------------------------

Eine mögliche Projektstruktur sieht wie folgt aus:

/projekt_root
│
├── FanfictionScraper.ipynb
├── FanfcitionAnalyzer.ipynb
│
├── HilfsDokumente/
│   ├── AO3-FanFic-Scraper.py      	# Skript zum Scrapen der FanFics (wird für FanfictionScraper benötigt)
│   ├── AO3-ID-Scraper.py        	# Skript zum Scrapen der IDs (wird für FanfictionScraper benötigt)
│   ├── character_list.txt		# enthält die Fanfiction-spezifischen Charaktere
│   ├── compare_list.txt		# enthält die Themen-spezifischen Begriffe
│   └── stopword_list.txt		# enthält die Stopwords für das Topic Modeling
│
├── Ausgabedokumente/			# hier werden die Ausgabedokumente des FanfictionScraper gespeichert
├── Analysedokumente/			# hier werden die Analysedokumente des FanfictionAnalyzer gespeichert
│ 
└── README.txt

Hinweis: Falls deine reale Struktur davon abweicht, kann dies in den Notebook entsprechend angepasst werden.

===========================================
Ende der README
===========================================
