#Python 3.9
#Layers: aucune

#récupère le contenu du log .json sur S3
#arn:aws:lambda:eu-west-3:136168590538:function:EFS-stock-get_log
#https://vs27lbhmq7iiwlcqic2vb5anyu0shnvs.lambda-url.eu-west-3.on.aws/

import json
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
	
	print("Récupération du efs-stock-log.json qui est déjà sur S3")
	original = s3.get_object(Bucket="efs-stock-log", Key="efs-stock-log.json")["Body"].read()
	original_decode = original.decode('UTF-8')
	
	return {
	    "statusCode": 200,
	    "headers": {
            "Content-Type": "application/json"
        },
        "body": original_decode
    }
	
