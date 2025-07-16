from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client

import re
from huggingface_hub import InferenceClient

HUGGINGFACE_API_KEY = "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"
twilio_account_sid = 'AC90667503b444f9b48abf7f1133df1d6a'
twilio_auth_token = '130fc2f4d00152570f2ee55938aefc7f'


# @csrf_exempt
# def whatsapp_webhook(request):
#     if request.method == "POST":
#         print(20 * "#")
#         print("There is someone requested")
#         incoming_msg = request.POST.get("B  ody", "")
#         sender = request.POST.get("From", "")
#
#         print(sender)
#
#         # Send to Hugging Face model
#         api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
#         headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
#         payload = {"inputs": incoming_msg}
#
#         response = requests.post(api_url, headers=headers, json=payload)
#         result = response.json()
#         ai_response = result.get("generated_text", "Sorry, I didn’t understand.")
#
#         # Respond with TwiML
#         twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
# <Response>
#     <Message>{ai_response}</Message>
# </Response>"""
#
#         return HttpResponse(twiml, content_type="text/xml")
#
#     return HttpResponse("Only POST requests are accepted.", status=405)

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "POST":
        print("#" * 30)
        print("Webhook hit ✅")

        print("POST data:", request.POST.dict())

        incoming_msg = request.POST.get("Body", "")
        sender = request.POST.get("From", "")

        print(f"Sender: {sender}")
        print(f"Message: {incoming_msg}")

        ai_response = hugging_face_message(incoming_msg)

        # Return AI response back to Twilio as XML (TwiML)
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Message>{ai_response}</Message>
        </Response>"""

        return HttpResponse(twiml, content_type="text/xml")

    return HttpResponse("Only POST requests are accepted.", status=405)

@csrf_exempt
def whatsapp_message_receive(request):
    user_message = "Hello"
    reply = hugging_face_message(user_message)
    client = Client(twilio_account_sid, twilio_auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        to='whatsapp:+22248282490',
        body=reply,
    )

    return HttpResponse(status=204)


# def message_status_callback(request):
#     print("Status:", request.POST.get("MessageStatus"))
#     print("To:", request.POST.get("To"))
#     print("SID:", request.POST.get("MessageSid"))
#     return HttpResponse("Status received", status=200)

@csrf_exempt
def message_status_callback(request):
    if request.method == "POST":
        print("✅ Status Callback Received (POST)")
        print("Status:", request.POST.get("MessageStatus"))
        print("To:", request.POST.get("To"))
        print("SID:", request.POST.get("MessageSid"))
        return HttpResponse("Status received", status=200)
    else:
        print(f"⚠️ Received unexpected {request.method} request")
        print("Query params:", request.GET.dict())
        return HttpResponse("Only POST allowed", status=405)



def hugging_face_test(request):
    user_message = "Hello"
    reply = hugging_face_message(user_message)

    formatted = f"""
    <div style="font-family:sans-serif; font-size:1.1em;">
        <p><strong>🧑‍💬 You:</strong> {user_message}</p>
        <p><strong>🤖 AI says:</strong><br>{reply}</p>
    </div>
    """
    return HttpResponse(formatted)


def hugging_face_message(user_message):
    client = InferenceClient(api_key=HUGGINGFACE_API_KEY)

    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional AI assistant responding to WhatsApp users. "
                    "You must reply directly to the user's message with a short, friendly answer. "
                    "Never include thoughts, explanations, or tags like <think>. "
                    "Just give a clean and human-like reply suitable for sending to a real client."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    full_reply = completion.choices[0].message["content"]

    cleaned_reply = re.sub(r"<think>.*?</think>", "", full_reply, flags=re.DOTALL).strip()

    return cleaned_reply
