# 🎯 FocusAgent

Кроссплатформенный ИИ-агент для борьбы с прокрастинацией. Автоматически закрывает отвлекающие приложения, анализирует вашу дневную продуктивность и ведет учет тренировок.

## Установка и запуск

```bash
git clone https://github.com/Gvb3a/ai_agent.git
cd FocusAgent
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate на Windows
pip install -r requirements.txt
cp .env.example .env
```

В `.env` добавьте `GEMINI_API_KEY` (https://aistudio.google.com/app/api-keys). Затем запустите `main.py`:
```bash
python main.py
```

## TODO:
- [ ] Взаимодействие через Telegram
- [ ] Интеграция с календарем
- [ ] Интеграция с todoist/notion и т.д.
- [ ] Расширить README и перевести на английский
