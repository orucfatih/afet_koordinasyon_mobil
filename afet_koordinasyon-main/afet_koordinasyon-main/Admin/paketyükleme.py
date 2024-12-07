import os
import subprocess

def create_venv_and_install_packages(venv_name="venv", requirements_file="requirements.txt"):
    # 1. Sanal ortam oluştur
    print("Sanal ortam oluşturuluyor...")
    subprocess.run(["python", "-m", "venv", venv_name], check=True)

    # 2. Sanal ortamı etkinleştir
    python_executable = os.path.join(venv_name, "Scripts", "python") if os.name == "nt" else os.path.join(venv_name, "bin", "python")

    # 3. Pip'i güncelle
    print("Pip güncelleniyor...")
    subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)

    # 4. Gereksinimleri yükle
    print("Paketler yükleniyor...")
    subprocess.run([python_executable, "-m", "pip", "install", "-r", requirements_file], check=True)

    print("Tüm paketler başarıyla yüklendi!")

if __name__ == "__main__":
    create_venv_and_install_packages()
