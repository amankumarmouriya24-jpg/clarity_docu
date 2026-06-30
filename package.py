import os
import zipfile

os.makedirs("build", exist_ok=True)
extensions = (".py", ".html", ".js", ".css", ".txt", ".md")
with zipfile.ZipFile("build/claritydoc.zip", "w") as z:
    for f in os.listdir("."):
        if f.endswith(extensions) and not f.startswith("."):
            z.write(f)
            print("Added:", f)
print("Package created successfully.")
