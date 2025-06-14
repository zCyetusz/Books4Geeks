import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)

try:
    import django
    print("Django version:", django.get_version())
except ImportError:
    print("Django not found")

try:
    import cv2
    print("OpenCV version:", cv2.__version__)
except ImportError:
    print("OpenCV not found")

try:
    import numpy as np
    print("NumPy version:", np.__version__)
except ImportError:
    print("NumPy not found")

try:
    from PIL import Image
    print("Pillow available")
except ImportError:
    print("Pillow not found")

print("All basic dependencies checked!")
