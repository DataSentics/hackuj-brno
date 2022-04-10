from fastai.learner import load_learner
from pathlib import Path
from sanic.log import logger
from app_classificator.config import settings
classificator = None

def init_classificator(model_path: Path):
    global classificator 
    classificator = load_learner(model_path, cpu=settings.USE_CPU)
    if classificator is None:
        logger.error("Classificator not loaded")