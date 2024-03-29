from twilio.rest import Client

sid = 'AC48c43ecfc570aa44b4428201a6d00fe7'
token = '6de83d5c5aac9343871e6748a6405a51'

# client credentials are read from TWILIO_ACCOUNT_SID and AUTH_TOKEN
client = Client(sid, token)

# this is the Twilio sandbox testing number
from_whatsapp_number='whatsapp:+14155238886'

# replace this number with your own WhatsApp Messaging number
numbers=['whatsapp:+919632830620']

for to_whatsapp_number in numbers:
    try:
        client.messages.create(body='Hi!',
                               from_=from_whatsapp_number,
                               to=to_whatsapp_number)
    except Exception as err:
        print(err)
