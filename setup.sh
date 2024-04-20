#!/bin/bash

sudo apt update
sudo apt install gcc -y
sudo apt install g++ -y
sudo apt install make
sudo apt install curl -y
sudo apt install git
sudo apt install python3-pip -y
sudo apt install python3-venv -y
pip install pnu-fortune
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
touch photo_ids_db
bash -c "$(curl -s https://ggml.ai/server-llm.sh)" bash --repo https://huggingface.co/TheBloke/dolphin-2.2.1-mistral-7B-GGUF
