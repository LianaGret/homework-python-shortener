# Сервис сокращения ссылок

## Функциональность

### Обязательные функции
1. **Управление короткими ссылками** - создание, удаление, изменение и получение информации
2. **Статистика по ссылке** - просмотр данных о переходах
3. **Создание кастомных ссылок** - задание собственного alias
4. **Поиск ссылки по оригинальному URL**
5. **Указание времени жизни ссылки**

### Дополнительные функции
1. **Удаление неиспользуемых ссылок** - автоматическое удаление по таймауту
2. **История истекших ссылок** - отображение информации об истекших ссылках

### Кэширование
- ```/api/v1/links/{short_code}``` - ускорение перенаправления
- ```/api/v1/links/{short_code}/stats``` - снижение нагрузки на БД

## API

### Создание короткой ссылки
```
POST /api/v1/links/shorten
```
**Тело запроса:**
```json
{
  "original_url": "https://example.com/long/url",
  "custom_alias": "mylink",  // опционально
  "expires_at": "2025-04-30T12:00:00Z"  // опционально
}
```

### Перенаправление по короткой ссылке
```
GET /api/v1/links/{short_code}
```
**Ответ:** HTTP-редирект (302) на оригинальный URL

### Удаление короткой ссылки
```
DELETE /api/v1/links/{short_code}
```

### Обновление короткой ссылки
```
PUT /api/v1/links/{short_code}
```
**Тело запроса:**
```json
{
  "original_url": "https://example.com/new/url",
  "expires_at": "2025-05-31T12:00:00Z"  // опционально
}
```

### Статистика по ссылке
```
GET /api/v1/links/{short_code}/stats
```

### Поиск ссылки по оригинальному URL
```
GET /api/v1/links/search?original_url={url}
```

## Примеры запросов

### Создание короткой ссылки
```bash
curl -X POST "http://localhost:8000/api/v1/links/shorten" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com/long/url", "custom_alias": "mylink"}'
```

### Получение статистики
```bash
curl -X GET "http://localhost:8000/api/v1/links/mylink/stats"
```

## Инструкция по запуску

### Запуск сервиса
```bash
docker compose up --build -d
```

### Запуск тестов
```bash
pytest tests
```

## Описание базы данных

### Таблица links
| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Первичный ключ |
| short_code | VARCHAR(16) | Короткий код ссылки |
| original_url | TEXT | Оригинальный URL |
| custom_alias | BOOLEAN | Флаг кастомной ссылки |
| created_at | TIMESTAMP | Дата создания |
| expires_at | TIMESTAMP | Срок действия |

### Таблица link_visits
| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Первичный ключ |
| link_id | INTEGER | Внешний ключ к links |
| visited_at | TIMESTAMP | Время посещения |
| user_agent | TEXT | User-Agent |
| ip_address | VARCHAR(45) | IP-адрес |
| referrer | TEXT | Реферер |

