from fabric import task

REMOTE_PATH = "/opt/pyscripts/mysite"
LOCAL_PATH = "/opt/pyscripts/mysite"

@task
def deploy_cicd(c):
    print(f"🚀 Starting deployment on {c.host}")

    # Ensure target directory exists
    c.run(f"mkdir -p {REMOTE_PATH}", warn=True)

    # Rsync local codebase to remote
    print("📦 Syncing codebase to remote...")
    c.local(f"rsync -avz --delete {LOCAL_PATH}/ {c.user}@{c.host}:{REMOTE_PATH}/")

    # Optional: install dependencies or restart services
    print("🔁 Restarting services...")
    c.run(f"cd {REMOTE_PATH} && ./restart.sh", warn=True)

    print(f"✅ Deployment completed on {c.host}")

