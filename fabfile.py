from fabric import task

@task
def deploy_cicd(c):
    # Example deployment command — customize as needed
    c.run("echo '🚀 Starting deployment...'")
    c.run("git pull origin main")
    c.run("sudo systemctl restart your-app.service")
    c.run("echo '✅ Deployment complete!'")

