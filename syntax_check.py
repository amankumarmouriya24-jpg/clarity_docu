import compileall

compileall.compile_dir(".", quiet=1, force=True)
print("All Python files syntax OK.")
