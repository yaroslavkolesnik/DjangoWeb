import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


# Твой старый код для веб-чата (оставляем его, он правильный)
def chat_page(request):
    return render(request, "bot/chat.html")


@csrf_exempt
def bot_answer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("message", "").lower()

            # Простая логика (можно потом подключить сюда BotMenuElem из базы)
            answer = "Я пока учусь, спросите про телефон."

            return JsonResponse({"answer": answer})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)