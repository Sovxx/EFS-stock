#Python 3.8
#Layers:
#1	Klayers-p39-requests	2	arn:aws:lambda:eu-west-3:770693421928:layer:Klayers-p39-requests:2
#2	Klayers-p38-matplotlib	3	arn:aws:lambda:eu-west-3:770693421928:layer:Klayers-p38-matplotlib:3
#3	Klayers-p39-numpy	2	arn:aws:lambda:eu-west-3:770693421928:layer:Klayers-p39-numpy:2

#génère .svg et .png sur S3 à partir du log .json sur S3
#arn:aws:lambda:eu-west-3:136168590538:function:EFS-stock-graph-generator1

import json
import boto3
import requests
import numpy as np
import matplotlib.pyplot as plt # vaguement repris de https://waynestalk.com/en/python-heatmaps-en/
from matplotlib.lines import Line2D
from matplotlib import ticker
import io

url="https://vs27lbhmq7iiwlcqic2vb5anyu0shnvs.lambda-url.eu-west-3.on.aws/"   # généré par la fonction lamba EFS-stock-get_log  arn:aws:lambda:eu-west-3:136168590538:function:EFS-stock-get_log

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    print("Récupération des données de l'API")
    response = requests.get(url)
    html = response.content
    html = html.decode('UTF-8')
    data = json.loads(html)

    #cleanup (simpliste)
    offset = 0
    for i in range(len(data["import"])):
        if data["import"][i-offset]["statusCode site EFS"] != 200:
            data["import"].remove(data["import"][i-offset])
            offset = offset + 1

    X_legende = []
    Y = {}   #dictionnaire contenant, pour chaque "key" de groupe sanguin, la "value" de liste historique des stocks
    Ycouleur = {}
    liste_groupe = ["O-","A-","B-","AB-","O+","A+","B+","AB+"]
    for groupe in liste_groupe:
        Y[groupe] = []
        Ycouleur[groupe] = []

    for i in range(len(data["import"])):
        X_legende.append(data["import"][i]["date and time"][0:10])
        for groupe in liste_groupe:
            Y[groupe].append(data["import"][i]["stocks"][groupe])
            Ycouleur[groupe].append(data["import"][i]["stocks"][groupe])
            #transformation des niveaux en couleurs
            if Y[groupe][i] == "inconnu": Ycouleur[groupe][i] = [64,64,64] #gris
            if Y[groupe][i] == "near_zero": Ycouleur[groupe][i] = [255,0,0] #rouge
            if Y[groupe][i] == "half": Ycouleur[groupe][i] = [255,255,0] #jaune
            if Y[groupe][i] == "completed": Ycouleur[groupe][i] = [0,255,0] #vert

    print("Y[O-] : ", Y["O-"])
    print("Ycouleur[O-] : ", Ycouleur["O-"])

    df = [Ycouleur["O-"],Ycouleur["A-"],Ycouleur["B-"],Ycouleur["AB-"],Ycouleur["O+"],Ycouleur["A+"],Ycouleur["B+"],Ycouleur["AB+"]]
    fig, ax = plt.subplots(figsize=(20, 4))
    im = ax.imshow(df, aspect='auto')
    ax.set_xticks(np.arange(len(X_legende)))
    ax.set_xticklabels(X_legende)
    xticks = ticker.MaxNLocator(40)
    ax.xaxis.set_major_locator(xticks)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_yticks(np.arange(len(liste_groupe)))
    ax.set_yticklabels(liste_groupe)
    ax.set_title("Historique des stocks")
    
    custom_lines = [Line2D([0], [0], color="#808080", lw=6),
                Line2D([0], [0], color="#FF0000", lw=6),
                Line2D([0], [0], color="#FFFF00", lw=6),
                Line2D([0], [0], color="#00FF00", lw=6)]
    ax.legend(custom_lines, ['Inconnu', 'Critique', 'Moyen', 'Satisfaisant'], title="Niveau de stock", ncol=4, bbox_to_anchor=(0.35,1.2))
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket("efs-stock-log")
    
    img_data = io.BytesIO()
    plt.savefig(img_data, dpi=100, format="png", metadata=None, bbox_inches="tight", pad_inches=0.1, facecolor='auto', edgecolor='auto', backend=None)
    img_data.seek(0)
    bucket.put_object(Body=img_data, ContentType='image/png', Key="historique.png")
    
    img_data = io.BytesIO()
    plt.savefig(img_data, dpi=100, format="svg", metadata=None, bbox_inches="tight", pad_inches=0.1, facecolor='auto', edgecolor='auto', backend=None)
    img_data.seek(0)
    bucket.put_object(Body=img_data, ContentType='image/svg+xml', Key="historique.svg")
    
    return {
        'statusCode': 200,
        'body': json.dumps('historique.png et historique.svg générés sur le bucket S3')
    }

