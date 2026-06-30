import os


os.makedirs("build", exist_ok=True)
commit = os.environ.get("CI_COMMIT_SHA", "local")
branch = os.environ.get("CI_COMMIT_REF_NAME", "main")
pipeline = os.environ.get("CI_PIPELINE_ID", "0")
content = (
    f"Project: ClarityDoc\nCommit: {commit}\nBranch: {branch}\nPipeline: {pipeline}\n"
)
open("build/release-manifest.txt", "w").write(content)
print(content)
print("Release manifest created.")
