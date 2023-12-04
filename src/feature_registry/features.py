# features.py

import streamlit as st
from datetime import datetime
import json
import os


class Feature:
    def __init__(self, name: str, type: str, description: str, parameters: dict, activated: bool = False):
        self.name = name
        self.type = type
        self.description = description
        self.parameters = parameters
        self.created_at = datetime.now().isoformat()  # Use ISO format for serialization
        self.activated = activated

    def execute(self, *args, **kwargs):
        raise NotImplementedError(
            "Each feature must implement an execute method.")

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "parameters": self.parameters,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            type=data["type"],
            description=data["description"],
            parameters=data["parameters"],
        )


def save_features_to_file(features, filename="features.json"):
    # Serialize feature objects to a JSON file
    with open(filename, 'w') as f:
        # Convert objects to dictionaries for JSON serialization
        json.dump([feature.__dict__ for feature in features], f)


def load_features_from_file(filename="features.json"):
    # Load feature objects from a JSON file
    if not os.path.exists(filename):
        return []

    with open(filename, 'r') as f:
        features_dict_list = json.load(f)
        # You need to convert dictionaries back to Feature objects or the appropriate subclass
        # This might require a more complex deserialization process if you have many subclasses
        features = [Feature(**feature_dict)
                    for feature_dict in features_dict_list]
        return features


def save_features_to_session_state():
    # Assuming 'features' is a list of Feature objects
    st.session_state['features'] = st.session_state.get(
        'features', []) + [feature.__dict__ for feature in features]


def load_features_from_session_state():
    # Assuming 'features' is a key in st.session_state
    features_dict_list = st.session_state.get('features', [])
    features = [Feature(**feature_dict) for feature_dict in features_dict_list]
    return features
