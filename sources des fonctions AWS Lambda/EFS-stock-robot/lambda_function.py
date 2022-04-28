#Python 3.9
#Layers:
#1	Klayers-p39-requests	2	arn:aws:lambda:eu-west-3:770693421928:layer:Klayers-p39-requests:2

#ajoute les données Live au log .json sur S3
#arn:aws:lambda:eu-west-3:136168590538:function:EFS-stock-robot

import json
import boto3
import requests

url="https://vxalvbsd6ygdxgzmvzm2vnwnzm0qxggz.lambda-url.eu-west-3.on.aws/"   # généré par la fonction lamba EFS-stock  arn:aws:lambda:eu-west-3:136168590538:function:EFS-stock

s3 = boto3.client('s3')

def lambda_handler(event, context):
	
	print("Récupération du efs-stock-log.json qui est déjà sur S3")
	original = s3.get_object(Bucket="efs-stock-log", Key="efs-stock-log.json")["Body"].read().decode('UTF-8')
	original_data = json.loads(original)

	print("Récupération des données de l'API")
	response = requests.get(url)
	html = response.content
	html = html.decode('UTF-8')
	html_data = json.loads(html)
	
	print("Préparation du nouveau contenu")
	nouveau_data = original_data
	nouveau_data["import"].append(html_data)
	nouveau_contenu = json.dumps(nouveau_data)
	
	print("Envoi vers ")
	s3.put_object(Bucket="efs-stock-log", Key="efs-stock-log.json", Body=nouveau_contenu)
	print('Put Complete')

