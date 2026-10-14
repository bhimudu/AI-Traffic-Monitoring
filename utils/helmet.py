# utils/helmet.py

def helmet_status(helmet_model_results):
    """
    You should train helmet model with classes: helmet / no-helmet
    For now this is placeholder logic.
    """
    # If helmet detected return True else False
    # You will adjust based on your model class names
    for r in helmet_model_results:
        if r.boxes is None:
            continue
        if len(r.boxes) > 0:
            return True
    return False
