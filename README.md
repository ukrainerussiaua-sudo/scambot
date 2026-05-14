# 🤖 Scam Bot — Инструкция по запуску

## Структура файлов
```
scambot/
├── main.py          # точка входа
├── config.py        # настройки (токен, ID каналов)
├── database.py      # работа с Supabase
├── keyboards.py     # клавиатуры
├── utils.py         # вспомогательные функции
├── report.py        # подача жалоб
├── check.py         # проверка по базе
├── moderation.py    # одобрение/отклонение жалоб
├── schema.sql       # SQL для Supabase
├── requirements.txt
└── media/
    ├── scam_banner.jpg   # красный баннер (добавь сам)
    └── clean_banner.jpg  # зелёный баннер (добавь сам)
```

## Настройка

### 1. Supabase
- Зайди в Supabase → SQL Editor → New Query
- Вставь содержимое `schema.sql` и выполни

### 2. config.py — уже настроен:
- `CHANNEL_ID = -1003818586201` — канал публикации
- `MODERATION_GROUP_ID = -1003856428134` — группа админов
- Замени `CHANNEL_LINK` на реальную ссылку канала

### 3. Медиа-файлы
Положи в папку `media/`:
- `scam_banner.jpg` — картинка для мошенников (красная)
- `clean_banner.jpg` — картинка для чистых (зелёная/золотая)

## Установка и запуск

```bash
pip install -r requirements.txt
python main.py
```

## Важно — бот должен быть:
- Администратором в канале `-1003818586201`
- Администратором в группе модерации `-1003856428134`
