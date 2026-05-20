## Правила именования веток 

### Основные форматы

| Тип изменений | Формат | Пример |
|---------------|--------|--------|
| **Новая функциональность** | `usazd/init/<описание>` | `usazd/init/book_price` |
| **Интеграция / внутреннее** | `usazd/int/<описание>` | `usazd/int/admin_cancel` |
| **Исправление бага** | `usazd/fix_<описание>` | `usazd/fix_logout` |
| **Простые правки** | `<описание>` | `new_currency` |
| **Экспериментальное** | `usazd/<тема>` | `usazd/neural_network` |

### Что писать в `<описание>`

- **На английском**
- **Только нижний регистр**
- **Слова через нижнее подчеркивание** `_`
- **Коротко и по делу** (2-4 слова)

### Примеры из реальной истории

```bash
# Новая фича
usazd/init/repeat
usazd/init/tests
usazd/init/vip

# Админка / интеграция
usazd/int/404_page
usazd/int/api/service/continue

# Фикс
usazd/fix_logout

# Главная ветка
main


# Эксперимент
usazd/neural_network
usazd/styles