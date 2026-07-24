# Telegram LLM Bot

Telegram-бот на aiogram 3.x с тремя интеграциями:

- **LLM** — через [OpenRouter](https://openrouter.ai) (доступ к Claude, GPT, Llama и др. по единому API)
- **Распознавание речи** — через [Hugging Face Inference API](https://huggingface.co/docs/inference-providers) (модель Whisper)
- **Распознавание видео** — та же модель Whisper: из видео и видео-кружочков извлекается звуковая дорожка и распознаётся так же, как голосовое сообщение

## Возможности

- Отвечает на текстовые сообщения, используя выбранную LLM
- Принимает **голосовые сообщения** — транскрибирует и отвечает на содержание
- Принимает **видео и видео-кружочки** — извлекает звук, транскрибирует и отвечает так же, как на голосовое
- Хранит историю диалога в памяти (на чат), команда `/reset` очищает её
- Настраиваемый системный промпт

## Установка

### 1. Системные зависимости

Нужен **ffmpeg** — и для конвертации голосовых сообщений (OGG/Opus), и для извлечения звука из видео (MP4):

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Скачать сборку с https://www.gyan.dev/ffmpeg/builds/ (release essentials),
# распаковать, добавить папку bin в переменную окружения PATH,
# перезапустить терминал и проверить: ffmpeg -version
```

### 2. Python-зависимости

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Python 3.13:** модуль `audioop`, от которого зависит `pydub`, был убран из стандартной библиотеки. Если увидите `ModuleNotFoundError: No module named 'audioop'` — поставьте `pip install audioop-lts`. Если и это не поможет — надёжнее использовать Python 3.11/3.12 для этого проекта.

### 3. Получить необходимые ключи

**Telegram Bot Token:**
1. В Telegram откройте [@BotFather](https://t.me/BotFather)
2. `/newbot` → следуйте инструкциям → получите токен вида `123456789:ABC...`

**OpenRouter API Key:**
1. Зарегистрируйтесь на [openrouter.ai](https://openrouter.ai)
2. Создайте ключ в разделе [Keys](https://openrouter.ai/keys)
3. Пополните баланс либо используйте бесплатные модели — ищите пометку `:free` в [списке моделей](https://openrouter.ai/models)

**Hugging Face Token:**
1. Зарегистрируйтесь на [huggingface.co](https://huggingface.co)
2. Создайте токен в [Settings → Access Tokens](https://huggingface.co/settings/tokens)
3. **Важно:** если создаёте токен типа **Fine-grained**, обязательно включите право **"Make calls to Inference Providers"** в разделе Inference — без него запросы будут падать с `403 Forbidden`. Проще всего выбрать тип **Read** — у него это право включено по умолчанию.
4. Проверьте [huggingface.co/settings/billing](https://huggingface.co/settings/billing) — иногда там нужно один раз подтвердить использование Inference Providers, даже для бесплатного лимита

### 4. Настроить .env

```bash
cp .env.example .env
```

Откройте `.env` и впишите свои значения токенов.

**Важно про модель распознавания речи:** Hugging Face подключает к бесплатному serverless-инференсу (`hf-inference`) не любую модель Whisper, а конкретные. На момент написания через `hf-inference` доступна:

```env
HF_ASR_MODEL=openai/whisper-large-v3-turbo
```

Если модель перестанет быть доступна (HF периодически меняет список), в логах будет видно `StopIteration`/`404`/`400` — тогда стоит свериться с актуальным списком на [странице задачи ASR](https://huggingface.co/docs/inference-providers/tasks/automatic-speech-recognition) в разделе `hf-inference`.

### 5. Запуск

```bash
python3 main.py
```

Бот запустится в режиме polling. Напишите ему в Telegram `/start`.

