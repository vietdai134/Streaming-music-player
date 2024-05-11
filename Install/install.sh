#!/bin/bash

install_python3() {
    # Kiểm tra phiên bản Python hiện tại
    python_version=$(python3 --version 2>&1)
    python_installed=$?

    if [ $python_installed -eq 0 ]; then
        echo "Python 3 đã được cài đặt: $python_version"
    else
        echo "Python 3 chưa được cài đặt. Đang cài đặt..."

        # Kiểm tra và cài đặt Python 3 cho các bản phân phối phổ biến
        if command -v apt-get >/dev/null 2>&1; then
            # Cài đặt cho Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y python3
        elif command -v yum >/dev/null 2>&1; then
            # Cài đặt cho CentOS/RHEL
            sudo yum install -y python3
        elif command -v zypper >/dev/null 2>&1; then
            # Cài đặt cho openSUSE
            sudo zypper install -y python3
        elif command -v pacman >/dev/null 2>&1; then
            # Cài đặt cho Arch Linux
            sudo pacman -Sy python
        elif command -v dnf >/dev/null 2>&1; then
            # Cài đặt cho Fedora
            sudo dnf install -y python3
        else
            echo "Không thể xác định bản phân phối Linux. Vui lòng cài đặt Python 3 thủ công."
            return 1
        fi

        echo "Python 3 đã được cài đặt thành công!"
    fi
}

#!/bin/bash

install_python_packages() {
    # Danh sách các gói Python cần cài đặt
    packages=(
        "tkinter"
        "pytube"
        "pydub"
        "sounddevice"
        "numpy"
        "urllib3"
        "pillow"
        "python-vlc"
        "pynput"
        "customtkinter"
    )

    # Kiểm tra phiên bản Python 3
    python_version=$(python3 --version 2>&1)
    python_installed=$?

    if [ $python_installed -ne 0 ]; then
        echo "Python 3 chưa được cài đặt. Vui lòng cài đặt Python 3 trước."
        return 1
    fi

    # Cài đặt pip3 nếu chưa có
    if ! command -v pip3 >/dev/null 2>&1; then
        echo "Đang cài đặt pip3..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update
            sudo apt-get install -y python3-pip
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y python3-pip
        elif command -v zypper >/dev/null 2>&1; then
            sudo zypper install -y python3-pip
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -Sy python-pip
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y python3-pip
        else
            echo "Không thể cài đặt pip3. Vui lòng cài đặt thủ công."
            return 1
        fi
    fi


    # Tạo môi trường ảo Python
    python3 -m venv myenv

    # Update Pip
    pip install --upgrade pip

    # Kích hoạt môi trường ảo Python
    source myenv/bin/activate

    # Cài đặt các gói Python chưa được cài đặt
        for package in "${packages[@]}"; do
            if ! python3 -c "import $package" >/dev/null 2>&1; then
                echo "Đang cài đặt gói $package..."
                pip3 install "$package"
            else
                echo "Gói $package đã được cài đặt."
            fi
        done
}


# Gọi hàm cài đặt Python 3
install_python3

# Gọi hàm cài đặt các gói Python
install_python_packages


