import os

def get_resource_path(relative_path: str) -> str:
    """
    Devuelve la ruta absoluta a un recurso, dado su path relativo dentro de main/resources/icons/.
    """
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "icons"))
    return os.path.join(base_path, relative_path)
