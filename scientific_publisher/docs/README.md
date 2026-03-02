# Scientific Publisher CLI

## Возможности
- Создание рукописи
- Подача на рецензирование
- Назначение рецензий
- Принятие/отклонение
- Сохранение состояния в JSON

## Запуск

```bash
python main.py create --title "AI Research" --authors Alice Bob
python main.py list
python main.py submit <id>
python main.py review <id> --reviewer DrX --decision accept