from pathlib import Path

# Путь к медиа хранилищу
MEDIA_ROOT = Path(__file__).parent.parent / "media"
MEDIA_ROOT.mkdir(exist_ok=True, parents=True)
