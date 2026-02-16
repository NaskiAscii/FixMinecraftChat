import os
import subprocess
import requests
import sys
import shutil

# ==========================
# CONFIGURATION
# ==========================

MC_VERSION = "1.21.11"
LOADER_VERSION = "0.18.4"

MODS = {
    "fabric-api": "P7dR8mSH",
    "sodium": "AANobbMI",
    "no-chat-reports": "z440MEwJ"
}

# ==========================
# FUNCTIONS
# ==========================

def get_minecraft_dir():
    if sys.platform == "win32":
        return os.path.join(os.environ["APPDATA"], ".minecraft")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/minecraft")
    else:
        return os.path.expanduser("~/.minecraft")

def check_java():
    try:
        subprocess.run(["java", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def download_file(url, filename):
    print(f"Downloading {filename}...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

def install_fabric(mc_dir):
    print("Downloading Fabric installer...")
    installer_url = "https://meta.fabricmc.net/v2/versions/installer"
    versions = requests.get(installer_url).json()
    latest_installer = versions[0]["url"]

    installer_jar = "fabric-installer.jar"
    download_file(latest_installer, installer_jar)

    print("Installing Fabric headlessly...")
    subprocess.run([
        "java", "-jar", installer_jar,
        "client",
        "-mcversion", MC_VERSION,
        "-loader", LOADER_VERSION,
        "-dir", mc_dir,
        "-noprofile"
    ], check=True)

    os.remove(installer_jar)

def download_mod(project_id, mc_dir):
    print(f"Fetching latest compatible version for {project_id}...")

    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    versions = requests.get(url).json()

    for version in versions:
        if MC_VERSION in version["game_versions"] and "fabric" in version["loaders"]:
            file_url = version["files"][0]["url"]
            filename = version["files"][0]["filename"]

            mods_dir = os.path.join(mc_dir, "mods")
            os.makedirs(mods_dir, exist_ok=True)

            download_file(file_url, os.path.join(mods_dir, filename))
            print(f"Installed {filename}")
            return

    print(f"No compatible version found for project {project_id}")

# ==========================
# MAIN
# ==========================

def main():
    print("Minecraft Fabric Auto Installer")
    print("--------------------------------")

    if not check_java():
        print("Java is not installed or not in PATH.")
        sys.exit(1)

    mc_dir = get_minecraft_dir()

    if not os.path.exists(mc_dir):
        print("Minecraft directory not found.")
        sys.exit(1)

    try:
        install_fabric(mc_dir)
    except subprocess.CalledProcessError:
        print("Fabric installation failed.")
        sys.exit(1)

    for name, project_id in MODS.items():
        download_mod(project_id, mc_dir)

    print("\nInstallation complete!")
    print("Launch Minecraft and select the Fabric profile.")

if __name__ == "__main__":
    main()
