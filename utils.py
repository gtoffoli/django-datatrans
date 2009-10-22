from django.conf import settings

REGISTRY = []

def register(model, modeltranslation):
    REGISTRY.append((model, modeltranslation))
    
    