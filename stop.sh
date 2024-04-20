#!/bin/bash
llama_id=$(cat llama_api_id)
oai_id=$(cat api_like_OAI_id)
kill $llama_id
kill $oai_id
rm llama_api_id
rm api_like_OAI_id
