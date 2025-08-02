#!/usr/bin/env python3
from fabric import task
from invoke import Responder

@task
def greetings(c, msg):
    print(f"The script is about {msg}")

@task
def systemsinfo(c):
    print(f"The present working directory is")
    c.run("pwd")


    print(f"The memory information is as : ")
    c.run("free -m")
@task
def remote_setup(c):
    c.run("hostname")
    c.run("/usr/sbin/ip a")  # use full path to 'ip'
    c.run("free -m")
    c.run("df -h")
    c.run("df -hi")



@task
def push_yum_repo(c):
    print(f"Pushing repo to {c.host} ...")
    c.put("CentOS-Base.repo", "/tmp/CentOS-Base.repo")
    c.sudo("mv /tmp/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo")
    c.sudo("yum clean all && yum makecache")
    print("✅ Repo updated and cache rebuilt.")


@task
def install_packages(c, pck="wget curl zip unzip httpd"):
    print(f"Installing packages on {c.host}.....")

    # Detect package manager
    result = c.run("which yum || which apt", hide=True, warn=True)
    pkg_mgr = result.stdout.strip()

    if not pkg_mgr:
        print("❌ Could not detect a package manager (yum or apt) on remote host.")
        return

    if 'yum' in pkg_mgr:
        print("→ Detected YUM. Running installation...")
        c.run("sudo yum makecache fast", pty=True)
        c.run(f"sudo yum install -y {pck}", pty=True)
    elif 'apt' in pkg_mgr:
        print("→ Detected APT. Running installation...")
        c.run("sudo apt update -y", pty=True)
        c.run(f"sudo apt install -y {pck}", pty=True)
    else:
        print("❌ Unsupported package manager.")

@task
def deploywebsite(c):
    print(f"Deploying website on {c.host}.............")
    c.sudo("systemctl enable httpd")
    c.run("wget -O /tmp/website.zip https://www.tooplate.com/zip-templates/2075_digital_team.zip")
    c.sudo("rm -rf /var/www/html/*")
    c.sudo("unzip -o /tmp/website.zip -d /tmp/")
    c.sudo("cp -r /tmp/2075_digital_team/* /var/www/html/")
    c.sudo("chown -R apache:apache /var/www/html")
    c.sudo("systemctl restart httpd")
    result = c.run("hostname -I | awk '{print $1}'", hide=True)
    ip = result.stdout.strip()

    print(f"\n✅ Deployment complete on {c.host}")
    print(f"🌐 Access the website in browser: http://{ip}/\n")
from invoke import Collection
from fabric import Config

@task
def deploygit_site(c):
    print("Installing Apache and Git...")
    c.sudo("yum install -y httpd git")
    c.sudo("systemctl enable httpd")
    c.sudo("systemctl start httpd")

    print("Cloning website repo...")
    c.run("rm -rf ~/mysite && git clone https://github.com/jackkhan3/mysite.git ~/mysite")

    print("Deploying files...")
    c.sudo("rm -rf /var/www/html/*")
    c.sudo("cp -r ~/mysite/* /var/www/html/")
    c.sudo("chown -R apache:apache /var/www/html")

    result = c.run("hostname -I | awk '{print $1}'", hide=True)
    print(f"Website deployed! Try accessing http://{result.stdout.strip()}/ in your browser.")




@task
def rollback_site(c, commit="HEAD~1"):
    """
    Rollback the website to a previous commit on remote server.
    Default is one commit back (HEAD~1), or provide a specific commit hash.
    """
    print(f"Rolling back on {c.host} to commit: {commit}")

    with c.cd("~/mysite"):
        # Fetch latest and hard reset to given commit
        c.run("git fetch origin")
        c.run(f"git reset --hard {commit}")

    print("Redeploying rolled back version...")
    c.sudo("rm -rf /var/www/html/*")
    c.sudo("cp -r ~/mysite/* /var/www/html/")
    c.sudo("chown -R apache:apache /var/www/html")
    c.sudo("systemctl restart httpd")

    result = c.run("hostname -I | awk '{print $1}'", hide=True)
    print(f"\n✅ Rolled back and deployed on: http://{result.stdout.strip()}/")
@task
def show_commits(c, lines=5):
    print(f"Showing last {lines} commits on {c.host}:")
    with c.cd("~/mysite"):
        c.run(f"git log --oneline -n {lines}")
ns = Collection()


@task
def deploy_cicd(c):
    with c.cd('/var/www/mysite'):  # your actual path on devserver1
        c.run('git pull origin main')  # or main/master as per your branch



# Add all your tasks explicitly
ns.add_task(greetings)
ns.add_task(systemsinfo)
ns.add_task(remote_setup)
ns.add_task(push_yum_repo)
ns.add_task(install_packages)
ns.add_task(deploywebsite)
ns.add_task(rollback_site)
ns.add_task(show_commits)
ns.add_task(deploygit_site, name='deploy_gitsite')
ns.add_task(deploy_cicd)
namespace = ns
