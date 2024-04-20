# GhostWriter

## Описание

GhostWriter - интерфейс, позволяющий вам создавать новостные статьи и выкладывать их на вашем Ghost сайте.
Статьи вместо вас будет писать [**dolphin-2.2.1-mistral-7B**](https://huggingface.co/TheBloke/dolphin-2.2.1-mistral-7B-GGUF) - [LLM](https://en.wikipedia.org/wiki/Large_language_model) (Large Language Model).

В течение разработки из проекта [llama.cpp](https://github.com/ggerganov/llama.cpp/tree/master) были заимствованы:

- [скрипт](https://github.com/ggerganov/llama.cpp/pull/3868), позволяющий щелчком пальцев развернуть llama.cpp сервер
- [api_like_OAI.py](https://github.com/ggerganov/llama.cpp/blob/master/examples/server/api_like_OAI.py) - скрипт, позволяющий обращаться к llama.cpp серверу с помощью OpenAI API (в нашем проекте через библиотеку openai для python)

## Требования
- ОС Linux
- Python >= 3.8

## Использование

### Установка

```bash
git clone https://github.com/NoCloud-today/GhostWriter.git
cd GhostWriter
./setup.sh
```
Это позволит вам загрузить все необходимые инструменты для дальнейшей работы и саму модель.

Введите пароль от своего аккаунта и подождите, установка займет несколько минут.

Когда высветится `Press Enter to continue …` нажмите Enter.

Когда высветится `[+] Select weight type:` напишите 9 и нажмите Enter.

Когда вы увидите строчку `all slots are idle and system prompt is empty, clear the KV cache` - нажмите ctrl + C - установка завершена!

Иногда, в связи с нестабильным интернет соединением, установка может зависнуть. В таком случае рекомендуется прекратить процес командой ctrl + C и повторным запуском команды `./setup.sh`.

Если же зависло, и последняя строка следующая: `[+] Checking for GGUF model files in https://huggingface.co/TheBloke/dolphin-2.2.1-mistral-7B-GGUF`, решением будет запуск только последней команды из файла setup.sh:

```bash
bash -c "$(curl -s https://ggml.ai/server-llm.sh)" bash --repo https://huggingface.co/TheBloke/dolphin-2.2.1-mistral-7B-GGUF
```


### Подготовка

в файле `settings.json` вам нужно изменить следующие поля:

- Сcылка на ваш Ghost instance и ключи к нему: поля `ghost_url`, `ghost_admin_api_key` - [здесь](https://play-ghost.intra.nocloud.today/ghost/#/settings/integrations) вы должны нажать кнопку `Add custom integration`, чтобы получить эти ключи
- Ключи для Unsplash API: `unsplash_access_key` (это значение `Access Key` в настройках вашего Unsplash приложения), `unsplash_secret_key` (значение `Secret key`) вот [здесь](https://unsplash.com/oauth/applications) вы можете создать свой Unsplash App и в его настройках можно найти эти ключи

```bash
source venv/bin/activate # активация виртуального окружения
```


### Запуск системы

```bash
./start.sh # перед запуском убедитесь, что виртуальное окружение активировано
```

### Остановка системы

```bash
./stop.sh
```

### Генерирование одной статьи и её публикация (выполнение может занять несколько минут)

```bash
./writer.py # перед запуском убедитесь, что виртуальное окружение активировано
```
