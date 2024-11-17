from .models import Dht11
from .serializers import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
import requests
from twilio.rest import Client


# Définir la fonction pour envoyer des messages Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response


# Définir la fonction pour envoyer des messages WhatsApp via Twilio
def send_whatsapp_message(account_sid, auth_token, to, from_, body):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=to,
        from_=from_,
        body=body
    )
    return message


@api_view(["GET", "POST"])
def Dlist(request):
    if request.method == "GET":
        all_data = Dht11.objects.all()
        data_ser = DHT11serialize(all_data, many=True)  # Les données sont sérialisées en JSON
        return Response(data_ser.data)

    elif request.method == "POST":
        serial = DHT11serialize(data=request.data)

        if serial.is_valid():
            serial.save()
            derniere_temperature = Dht11.objects.last().temp
            print("Dernière température enregistrée :", derniere_temperature)

            if derniere_temperature > 25:
                # Alerte Telegram
                telegram_token = '7558130646:AAFtB5ahO9TvHPZmNApNrjWwfjv2D9-nvFg'
                chat_id = '6790837692'  # ID de Chaimae Qourrida
                telegram_message = 'La température dépasse le seuil de 25°C, veuillez intervenir immédiatement pour vérifier et corriger cette situation.'

                try:
                    response = send_telegram_message(telegram_token, chat_id, telegram_message)
                    if response.status_code != 200:
                        print("Erreur d'envoi de message Telegram:", response.json())
                    else:
                        print("Message Telegram envoyé avec succès.")
                except Exception as e:
                    print("Exception lors de l'envoi du message Telegram:", e)

                # Alerte WhatsApp via Twilio
                account_sid = 'AC553039909c019227cf43b75571aec68c'  # Remplacez par votre SID Twilio
                auth_token = '374c1e5a0904727161997bd63ef30c71'  # Remplacez par votre Auth Token Twilio
                to_whatsapp = 'whatsapp:+212778730566'  # Numéro WhatsApp destinataire
                from_whatsapp = 'whatsapp:+14155238886'  # Numéro WhatsApp Twilio
                whatsapp_message = "La température dépasse le seuil de 25°C, veuillez intervenir immédiatement pour vérifier et corriger cette situation."

                try:
                    message = send_whatsapp_message(account_sid, auth_token, to_whatsapp, from_whatsapp,
                                                    whatsapp_message)
                    print("Message WhatsApp envoyé avec succès:", message.sid)
                except Exception as e:
                    print("Erreur lors de l'envoi du message WhatsApp:", e)

            return Response(serial.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
