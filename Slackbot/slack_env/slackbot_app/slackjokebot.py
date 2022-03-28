import pyjokes
import requests
from Bot import webhook_url
import time
from faker import Faker

fake = Faker()

counter = 0
while counter < 5:
    joke = pyjokes.get_joke()
    
    botpost = f'Computer Nerd Joke of the day:\n {joke}'
    
    data = {'text': botpost}
    requests.post(url=webhook_url, json = data)
    
    time.sleep(77760)
    
    counter+=1