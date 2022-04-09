from fastai.learner import load_model
from pathlib import Path

classificator = None

def init_classificator(model_path: Path):
    classificator = load_model(model_path)