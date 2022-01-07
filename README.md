
# WOLLALA-UPBIT
![Generic badge](https://img.shields.io/badge/python-3.8.9-green.svg) 
![Generic badge](https://img.shields.io/badge/pyside-6-green.svg)

- wollala-upbit은 upbit의 거래내역을 정리해서 보여줍니다.
  - 부분체결로 이루어진 거래를 정리해서 보여줍니다.
- upbit의 자산내역을 정리해서 보여줍니다.
- 간단한 산술기능을 제공합니다.
---
> **WARNING**: Upbit api key 정보를 저장하고 있는 '**config.json**' 파일은 절대 공유하시면 안됩니다.
---
## Installation
### pyenv, poetry 이용
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
4. execute
   ```shell
   $ python main.py
   ```

### venv와 requirements.txt 이용
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
   # if error, add '--no-dops' option.
   $ python -m pip install --no-deps -r .\requirements.txt
   ```
4. execute
   ```shell
   $ python main.py
   ```
---
## Create execute file
```shell
pyinstaller.exe main.py --noconsole --icon=./resource/wollala-upbit_64x64.ico --onefile --name wollala-upbit.exe 
```

# Donation
- **BTC**: 34EvTZBAPqT7SviBLggjn4PV9qZG4PVcFp
- **ETH**: 0xc281565c8f5fe037570aac45021db4897fd6ce19
