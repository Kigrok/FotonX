# [FotonX](https://my.telegram.org/auth)
![FotonX](https://raw.githubusercontent.com/Kigrok/FotonX/main/data/fotonx.png)
## Crypto Blog 
<a target="_blank" href="https://medium.com/@kplaya"><img src="https://img.shields.io/badge/-Medium-12100E?style=for-the-badge&logo=Medium&logoColor=white"></img></a>
<a target="_blank" href="https://t.me/foton_x"><img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/></img></a>

---
![Taiko](https://github.com/Kigrok/FotonX/blob/main/data/taiko.jpeg?raw=true)


<h1 align="center">
  Taiko
</h1>

### Functions: 
- Swap ETH for Tokens
- Swap Tokens for ETH
- Get the token balance
- Adding liquidity (ETH + Token)

---

## Install 

### Clone repository
```sh
git clone https://github.com/Kigrok/FotonX.git
cd FotonX
```

### Installing the virtual environment and packages
```sh
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

### Adding wallet address and private key
```sh
export wallet='your wallet address '
export private_key='your private key'
```

# Start
```sh
cd Taiko
python3 taiko.py
```