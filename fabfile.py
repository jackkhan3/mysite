from fabric import task

@task
def deploy_cicd(c):
    # Replace these with actual deploy steps on devserver1
    c.run("echo '🚀 Starting deployment on devserver1'")
    c.run("git pull origin main")
    c.run("sudo systemctl restart your-app.service")
    c.run("echo '✅ Deployment finished!'")

