
# WOLLALA-UPBIT
![Generic badge](https://img.shields.io/badge/python-3.8.9-green.svg) 
![Generic badge](https://img.shields.io/badge/pyside-6-green.svg)

- Upbit의 거래내역을 정리해서 보여줌.
  - 부분체결로 이루어진 거래를 정리해서 보여준다.
- Upbit의 자산내역을 정리해서 보여줌.
- 간단한 산술기능 제공.
- Language : Python (Python3.8.9)
- Dependency : Pyside6, pandas, upbit-client 

---
## Installation
### pyenv,poetry 이용
#### 1. PreInstallation
1. pyenv 설치
   - https://github.com/pyenv/pyenv-installer
2. poetry 설치
   - https://python-poetry.org/docs/
#### 2. Installation
1. Clone repo
   ```shell
   $ git clone https://github.com/Wollala/wollala-upbit
   ```
2. Install python3.8.9 and create virtualenv by pyenv
   ```shell
   $ pyenv install 3.8.9
   $ cd wollala-upbit
   $ pyenv virtualenv 3.8.9 wollala-upbit-env
   $ pyenv local wollala-upbit-env
   ```
3. Set poetry and Install Dependencies packages
   ```shell
   $ poetry init
   $ poetry install
   ```
### requirements.txt 이용
1. Clone repo
   ```shell
   $ git clone https://github.com/Wollala/wollala-upbit
   ```
2. Install python3.8.9
   ```shell
   $ apt install python3.8
   $ apt install python3.8-venv
   ```
3. Create venv and Install Dependencies packages
   ```shell
   $ cd wollala-upbit
   $ python3.8 -m venv .venv
   $ . .venv/bin/activate
   $ python -m pip install -r requirements.txt
   ```
---
# Donation
- **BTC**: 34EvTZBAPqT7SviBLggjn4PV9qZG4PVcFp
- **ETH**: 0xc281565c8f5fe037570aac45021db4897fd6ce19
