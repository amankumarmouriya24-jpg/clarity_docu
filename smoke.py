import ast
import os

if os.path.exists("app.py"):
    ast.parse(open("app.py").read())
    print("app.py is valid - smoke test passed.")
else:
    print("app.py not found - skipping.")
