#!/usr/bin/env python
import uuid
from sanic import Blueprint
from sanic.response import json as sanic_json
from sanic.log import logger
from random import random
from pathlib import Path
import psycopg2

from app_classificator.config import settings

connection = psycopg2.connect(user="dusko",
                                password="Test1234",
                                host="postgres-hackuj-brno.postgres.database.azure.com",
                                port="5432",
                                database="postgres")

api_v1 = Blueprint("api_v1", url_prefix="/api/v1")

# FIXME: Development version. Not real usecase.
@api_v1.route("/classify")
async def classify(request):
    from app_classificator.model.classificator import classificator
    document_id = uuid.uuid4()
    image_request = request.files.get("image")
    image_data = image_request.body
    image_name = image_request.name
    image_path = Path(f"./images/{document_id}/{image_name}")
    
    image_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(str(image_path), "wb") as imf:
        imf.write(image_data)
    
    # load the model
    logger.info(f"working on model {image_path=}")
    # return the inferenced value
    clas_result = classificator.predict(str(image_path))
    clas_out = {
            "empty": 1 if not clas_result[0]=="empty" else 0,
            "is_empty_prob": float(clas_result[2][0]),
            "is_full_prob": float(clas_result[2][1]),
        }
    
    return sanic_json(clas_out)

@api_v1.route("/trash_cans")
def trash_cans(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM trashcan_points")
    trash_bins = cursor.fetchall()
    output = []
    
    for i in range(len(trash_bins)):
        lon, lat, is_full, _, _, photo_url = trash_bins[i]
        output.append({"long":lon, "lat":lat, "is_full":is_full == 1, "photo_url": photo_url})
    
    
    return sanic_json(output)
