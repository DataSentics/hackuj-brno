#!/usr/bin/env python
import attr
from sanic import Blueprint
from sanic.response import json, file
from sanic.log import logger
from random import random

from fastbook import *
from fastai.vision.widgets import *
import os
from pathlib import Path

from app_classificator.model.classificator import classificator
from app_classificator.config import settings
# parameters
batch_size = 128
epoch_num = 20
arch = resnet34  # resnet18, resnet34, resnet50, resnet101, ...
valid_pct = 0.2
crop_size = 224
lr = 1e-3

# augmentations
tfms_do_flip = True
tfms_flip_vert = True
tfms_max_rotate = 50 
tfms_max_zoom = 1.1
tfms_max_warp = 0.2
tfms_max_lighting = 0.5 # max brightness
tfms_p_affine = 0.75 # no random rotation

api_v1 = Blueprint("api_v1", url_prefix="/api/v1")

# FIXME: Development version. Not real usecase.
@api_v1.route("/response")
async def root(request):
    image_data = request.args.get("image")
    image_path = Path(f"./images/{random()}")
    
    image_path.mkdir(parents=True, exist_ok=True)

    with image_path.open("w", encoding ="utf-8") as f:
        f.write(image_data)
    
    # load the model
    logger.info(f"working on model {image_path=}")
    # return the inferenced value
    calssification = classificator.predict(image_path, CPU=settings.USE_CPU)
    
    return json({
        "empty": 1 if not calssification[0]=="empty" else 0 
        "is_empty_prob": "value"
        "is_full_prob": "value"
        })


from . import some_specific_handlers
