# WOLLALA-UPBIT
![Generic badge](https://img.shields.io/badge/python-3.11-green.svg) 
![Generic badge](https://img.shields.io/badge/pyside-6-green.svg)

![image](https://github.com/wollala/wollala-upbit/assets/16458486/66754a35-e029-45a6-8dbd-3db682779732)

- wollala-upbit은 upbit의 거래내역을 정리해서 보여줍니다.
  - 부분체결로 이루어진 거래를 정리해서 보여줍니다.
- upbit의 자산내역을 정리해서 보여줍니다.
- 간단한 거래내역간의 산술기능을 제공합니다.

---
> **WARNING**: Upbit api key 정보를 저장하고 있는 '**config.json**' 파일은 절대 공유하시면 안됩니다.
---
# Installation for dev
## 1. PreInstallation
1. Install python3.11, pip,

## 2. Installation
1. Clone repo
   ```shell
   $ git clone https://github.com/Wollala/wollala-upbit
   ```
   
2. Create venv and Activate venv
   ```shell
   $ cd wollala-upbit
   $ python -m venv .venv
   $ source .venv/bin/activate
   ```
   
3. Install modules in .venv
   1. Using pip
      ```shell
      $ python -m pip install -r requirements.txt
      # if error, add '--no-dops' option.
      $ python -m pip install --no-deps -r .\requirements.txt
      ```

4. execute
   ```shell
   $ python main.py
   ```
---
# Create execute file
```shell
pyinstaller.exe main.py --noconsole --icon=./resource/wollala-upbit_64x64.ico --onefile --name wollala-upbit.exe 
```

# Donation
- **BTC**: 34EvTZBAPqT7SviBLggjn4PV9qZG4PVcFp
- **ETH**: 0xc281565c8f5fe037570aac45021db4897fd6ce19
