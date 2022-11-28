"""This module contains the base Model class

Model is the base model class. It contains a loading and downloading methods that are 
used by default to download your model into your Docker container and load it into your
application.

To use a custom model class in your application, create a new module such as
model_awesome.py in this package and write a custom class that overwrite _load_model, 
download_model or predict depending on your needs.
"""
import logging
import pickle
from pathlib import Path
from typing import Any, Tuple

from pydantic import BaseSettings

CURRENT_DIR = Path()
DEFAULT_MODELS_DIR = CURRENT_DIR / "{{package_name}}-models"
DEFAULT_MODEL_PATH = DEFAULT_MODELS_DIR / "model.pkl"

logger = logging.getLogger(__name__)


class ModelSettings(BaseSettings):
    """Download settings
        
    This class is used for settings management purpose, have a look at the pydantic
    documentation for more details : https://pydantic-docs.helpmanual.io/usage/settings/

    By default, it looks for environment variables (case insensitive) to set the settings
    if a variable is not found, it looks for a file name .env in your working directory
    where you can declare the values of the variables and finally it sets the values
    to the default ones you can see above.
    """

    model_path: Path = DEFAULT_MODEL_PATH

    class Config:
        env_file = ".env"


class Model:
    def __init__(self):
        self._model = None
        self._model_conf = None
        self._loaded = False

    def is_model_loaded(self):
        """return the state of the model"""
        return self._loaded

    def loading(self, **kwargs):
        """load the model"""
        self._model, self._model_conf = self._load_model(**kwargs)
        self._loaded = True

    def predict(self, *args, **kwargs):
        """Make a prediction thanks to the model"""
        return self._model.predict(*args, **kwargs)


    def _load_model(self, **kwargs) -> Tuple[Any, dict]:
        """Load a model from a file

        Returns:
            Tuple[Any, dict]: A tuple containing the model and a dict of metadata about it.
        """
        settings = ModelSettings(**kwargs)

        logger.info(f"Loading the model from {settings.model_path}")
        with settings.model_path.open("rb") as f:
            model = pickle.load(f)

        logger.info(f"Model loaded")
        return model, {
            "model_path": settings.model_path.name,
            "model_name": settings.model_path.stem,
        }

    @staticmethod
    def download_model(**kwargs) -> bool:
        """You shloud implement a download method to automatically download your model"""

        logger.info(
            "The function download_model is empty. Implement it to automatically download your model."
        )
        return True