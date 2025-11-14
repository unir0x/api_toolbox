# AGENTS.md

## Varför den här filen?
Den här filen sammanfattar de viktigaste reglerna för framtida AI-agenter (och stressad-efter-möten-jag) som ska ändra i projektet. Läs detta först så slipper vi onödiga regressioner eller osäkra ändringar.

## Snabb projektsketch
- `main.py` startar en Flask/Flask-RESTX app, monterar namespace i `services/` och kör adminpanelen som statiska filer i `admin/`.
- `config.py` laddar `config/settings.json` + miljövariabler via Pydantic och bootstrar en saknad `settings.json` från `defaults/settings.template.json`. Behöver du nya fält? uppdatera både modellen och templatet.
- `services/base64.py` och `services/csv_to_xls.py` är de nuvarande API-tjänsterna. De använder `Config.ALLOWED_EXTENSIONS` och uppladdningsgränser – låt central konfiguration styra i stället för hårdkodning. CSV-tjänsten tar emot flera filer (ett blad per fil) och sanerar `sheet_name`.
- `postman/ApiToolbox.postman_collection.json` innehåller en uppdaterad Postman-collection (API token, Base64, multi-CSV, admin). Uppdatera den när endpoints ändras.
- Docker-bygget (Python 3.11 slim) installeras via tvåstegs-Dockerfile och kör `entrypoint.sh` som droppar rättigheter med `gosu`.

## Arbetsflöde för agenter
1. **Miljö:** Följ README.md för att skapa `.env` med `SECRET_KEY` och kör `docker-compose up --build -d`. Undvik att installera paket globalt; använd containrar eller en virtuell miljö.
2. **Inläsning:** Kör `docker-compose logs -f api` vid behov, men lägg hellre till välplacerade loggar via `logging` i stället för `print`.
3. **Testa:** Det finns inga enhetstester än. Grundtest är `curl http://localhost:8000/health` samt att pinga `/swagger/` och `/admin`. När du lägger till nya funktioner, beskriv hur de ska testas i PR/committext.
4. **Säkerhet:** Allt som använder API:t måste respektera `X-API-Token`. Admin-rutter använder Basic Auth (`auth/admin_auth`). Återanvänd `api_auth`/`admin_auth` i stället för att skapa egna kontrollflöden.
5. **Konfiguration:** Om du behöver nya inställningar, uppdatera *alla* dessa: Pydantic-modellen i `config.py`, `defaults/settings.template.json`, README, samt eventuella Docker Compose-miljövariabler. Låt logik falla tillbaka på `Config`.
6. **Bygg & stil:** Följ PEP 8. Python-versionen är 3.11; använd moderna språkfeatures (typning, `pathlib`, `contextlib`). Lägg bara till externa beroenden om de motiveras och uppdatera `requirements.txt` + `Dockerfile`.

## Checklista innan du lämnar ändringar
- Lintat själv (minst `python -m compileall` eller `ruff` om tiden tillåter).
- Kör `docker-compose up --build` efter dependency-ändringar för att säkerställa att builder-steget fortfarande fungerar.
- Ny funktion? Dokumentera snabbt i README och/eller admin UI (t.ex. textsträngar i `admin/`).
- Konfigurationsingrepp? Bekräfta att `config/settings.json` fortfarande valideras och att du inte checkar in hemligheter.
- Lägg till loggning via `logging` med tydlig nivå (INFO för normalflöde, WARNING/ERROR annars).

## Praktiska tips
- **Namnge tokens:** `admin/api/tokens` kräver unika beskrivningar; hjälp användaren med validerande felmeddelanden om du bygger UI/CLI runt detta.
- **Filsystem:** Uppladdningar går aldrig till disk; Base64-dekodering använder `BytesIO`. Vid nya tjänster, fortsätt med in-memory och respektera `MAX_UPLOAD_FILE_SIZE`.
- **Observability:** Rotating loggar ligger i `logs/app.log` baseline. Om du lägger till fler handlers, använd samma storlek/backup-policy.

Behöver du göra något som avviker från dessa riktlinjer? Dokumentera avvikelsen direkt här så nästa agent vet varför.
