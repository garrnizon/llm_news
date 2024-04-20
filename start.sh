#!/bin/bash
model_path=$(find . -maxdepth 1  -name "*.gguf")
nohup __llama_cpp_port_8888__/server -m $model_path --host 0.0.0.0 --port 8888 -c 4096 > llama_api.out 2>&1 &
echo $! > llama_api_id
nohup python3 __llama_cpp_port_8888__/examples/server/api_like_OAI.py --llama-api http://127.0.0.1:8888 --port 8000 > api_like_OAI.out 2>&1 &
echo $! > api_like_OAI_id

