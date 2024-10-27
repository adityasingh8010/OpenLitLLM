# OpenLitLLM
based on LitLLM: A Toolkit for Scientific Literature Review

This repo aims to make this project more accesible and independent from OpenAI API with ability to run on local llm inference engine Ollama

## Installation

1. Install ollama https://github.com/ollama/ollama?tab=readme-ov-file , pull the supported models (llama3.1","llama3.2:1b","llama3.2) and run the inference server.
2. Create a Virtual enviroment and run  pip install -r requirements.txt
3. Run the app.py  python app.py

Program should be Running on local URL:  http://127.0.0.1:7860








## Changelog

Version 0.0.1

Updated gradio version, removed openAI key requirement and other bug fixes so it runs after installation

Version 0.0.2

Added localllm model options for inference

Version 0.0.3

Increased summarization limit of abstract to 10 from 4 words for improved performance


