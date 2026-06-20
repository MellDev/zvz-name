# Discord Bot

Bot Python simples para Discord usando `discord.py`.

## Configurar

```powershell
cd discord-bot
Copy-Item env.example .env
```

Edite `.env` e coloque o token em `DISCORD_BOT_TOKEN`.

No Discord Developer Portal, ative estas intents no bot:

- Server Members Intent
- Message Content Intent

## Rodar

```powershell
.\.venv\Scripts\python.exe bot.py
```

Comandos incluidos:

- `!ping`
- `/ping`
- `/zvz`
