from django.db import models

# Исправленный models.py
# Используем стандартный models.Model вместо TelegramModel

class BotMenuElem(models.Model):
    command = models.CharField(max_length=255, verbose_name="Команда")
    is_visable = models.BooleanField(default=True, verbose_name="Видим?")
    callbacks_db = models.CharField(max_length=255, blank=True, null=True, verbose_name="Callback data")
    message = models.TextField(verbose_name="Сообщение от бота")
    buttons_db = models.JSONField(default=dict, blank=True, verbose_name="Кнопки (JSON)")

    def __str__(self):
        return self.command

    class Meta:
        verbose_name = "Элемент меню бота"
        verbose_name_plural = "Элементы меню бота"