#!/usr/bin/env python3

from fabric import task, Config
from invoke import Collection

# ----------------------
# 💡 Utility Functions
# ----------------------

def get_ip(c):
    result = c.run("hostname -I | awk '{print $1}'", hide=True)
    return result.stdout.strip()

# ----------------------
# 🚀 Deployment Tasks
# ----------------------

@task
def deploy_template(c):
    """
    Deploys a static HTML website from a remote ZIP template.
    """
    print(f"Deploying static template on {c.host}...")
    c.sudo("systemctl enable httpd")
    c.run("wget -O /tmp/website.zip https://www.tooplate.com/zip-templates/2075_digital_team.zip")
    c.sudo("rm -rf /var/www/html/*")
    c.sudo("unzip -o /tmp/website.zip -d /tmp/")
    c.sudo("cp -r /tmp/2075_digital_team/* /var/www/html/")
    c.sudo("chown -R apache:apache /var/www/html")
    c.sudo("systemctl restart httpd")
    
    ip = get_ip(c)
    print(f"\n✅ Website deployed at: http://{ip}/")

@task
def deploy_gitsite(c):
    """
    Deploy website from GitHub repo.
    """
    print("Cloning and deploying from GitHub...")
    c.sudo("yum install -y httpd git")
    c.sudo("systemctl enable --now httpd")

    c.run("rm -rf ~/mysite && git clone https://github.com/jackkhan3/mysite.git ~/mysite")
    c.sudo("rm -rf /var/www/html/*")
    c.sudo("cp -r ~/mysite/* /var/www/html/")
    c.sudo("chown -R apache:apache /var/www/html")
    c.sudo("systemctl restart httpd")

    print(f"✅ Website deployed: http://{get_ip(c)}/")

@task
def deploy_cicd(c):
    print("Running CI/CD deployment...")
    with c.cd('~/mysite'):
        c.run('git pull origin main')

# ----------------------
# 🔧 Package & Repo Setup
# ----------------------

@task
def push_yum_repo(c):
    """
    Updates yum repo with custom CentOS-Base.repo.
    """
    print(f"Updating yum repo on {c.host}...")
    c.put("CentOS-Base.repo", "/tmp/CentOS-Base.repo")
    c.sudo("mv /tmp/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo")
    c.sudo("yum clean all && yum makecache")
    print("✅ Yum repo updated.")

@task
def install_packages(c, pck="wget curl zip unzip httpd"):
    """
    Installs required packages using yum or apt.
    """
    print(f"Installing packages on {c.host}...")

    result = c.run("which yum || which apt", hide=True, warn=True)
    pkg_mgr = result.stdout.strip()

    if 'yum' in pkg_mgr:
        print("→ YUM detected.")
        c.sudo("yum makecache fast")
        c.sudo(f"yum install -y {pck}")
    elif 'apt' in pkg_mgr:
        print("→ APT detected.")
        c.sudo("apt update -y")
        c.sudo(f"apt install -y {pck}")
    else:
        print("❌ Unsupported package manager.")

# ----------------------
# 🔁 Rollback & Logs
# ----------------------

@task
def rollback_site(c, commit="HEAD~1"):
    """
    Rollback the website to a previous commit and redeploy.
    """
    print(f"Rolling back to commit {commit} on {c.host}...")
    with c.cd("~/mysite"):
        c.run("git fetch origin")
        c.run(f"git reset --hard {commit}")

    c.sudo("rm -rf /var/www/html/*")
    c.sudo("cp -r ~/mysite/* /var/www/html/")
    c.sudo("chown -R apache:apache /var/www/html")
    c.sudo("systemctl restart httpd")

    print(f"✅ Rolled back site deployed: http://{get_ip(c)}/")

@task
def show_commits(c, lines=5):
    """
    Show recent Git commits on the server.
    """
    print(f"Last {lines} commits on {c.host}:")
    with c.cd("~/mysite"):
        c.run(f"git log --oneline -n {lines}")

# ----------------------
# 🔃 Default Deploy Task
# ----------------------

@task
def deploy(c):
    """
    Default deploy task for testing.
    """
    print("→ Running simple deploy message")
    c.run('echo "Deployment task running!"')

# ----------------------
# 🧩 Namespace Setup
# ----------------------

ns = Collection()

# Deployment
ns.add_task(deploy, name="deploy")
ns.add_task(deploy_template, name="deploy_template")
ns.add_task(deploy_gitsite, name="deploy_gitsite")
ns.add_task(deploy_cicd, name="deploy_cicd")

# Setup
ns.add_task(push_yum_repo)
ns.add_task(install_packages)

# Rollback & Logs
ns.add_task(rollback_site)
ns.add_task(show_commits)

namespace = ns

