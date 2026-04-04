#!/bin/bash
echo "🚀 Початок тренування..."

# Запуск тренування
/opt/venv/bin/python /workspace/ai_module/train_ai_small_objects.py

# Перевірка, чи успішно завершилось тренування
if [ $? -eq 0 ]; then
    echo "✅ Тренування завершено успішно!"
    echo "⏻ Вимкнення системи через 10 секунд..."
    sleep 10
    # Команда вимкнення хоста (працює якщо контейнер має права)
    shutdown now 
    # Або альтернатива: systemctl poweroff
else
    echo "❌ Тренування перервано або завершилось помилкою!"
    
    shutdown now
fi