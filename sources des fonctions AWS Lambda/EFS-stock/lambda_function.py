#Python 3.9
#Layers:
#1	Klayers-p39-requests	2	arn:aws:lambda:eu-west-3:770693421928:layer:Klayers-p39-requests:2
#2	Klayers-p39-beautifulsoup4	1	arn:aws:lambda:eu-west-3:770693421928:layer:Klayers-p39-beautifulsoup4:1

#récupère les données Live de l'EFS
#arn:aws:lambda:eu-west-3:136168590538:function:EFS-stock
#https://vxalvbsd6ygdxgzmvzm2vnwnzm0qxggz.lambda-url.eu-west-3.on.aws/

import json
from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime

url="https://dondesang.efs.sante.fr/barometre"
stocks = {
    "O-": "inconnu",
    "A-": "inconnu",
    "B-": "inconnu",
    "AB-": "inconnu",
    "O+": "inconnu",
    "A+": "inconnu",
    "B+": "inconnu",
    "AB+": "inconnu"
}

def lambda_handler(event, context):
    dt = datetime.now()
    print(dt)
    ts = datetime.timestamp(dt)
    print(ts)
    response = requests.get(url)
    print("Réponse site EFS : " + str(response.status_code))
    if response.status_code == 200:
        html = response.content
        soup = bs(html, "html.parser")
        for stock in stocks.keys():
            goutte=soup.find(title=stock)
            print(goutte)
            if goutte.find('img').get("src") != "": stocks[stock] = goutte.find('img').get("src")
            if goutte.find('img').get("src") == "/themes/custom/efs/images/icons/blood/near_zero.png": stocks[stock] = "near_zero"
            if goutte.find('img').get("src") == "/themes/custom/efs/images/icons/blood/half.png": stocks[stock] = "half"
            if goutte.find('img').get("src") == "/themes/custom/efs/images/icons/blood/completed.png": stocks[stock] = "completed"
            
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "statusCode site EFS": response.status_code,
            "date and time": str(dt),
            "timestamp": ts,
            "stocks": stocks
        })
    }
