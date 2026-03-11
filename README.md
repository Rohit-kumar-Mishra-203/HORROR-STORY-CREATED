# 🎃 Hindi Horror Story Generator

An AI-powered horror story created fine-tuned on IndicBART.

## Tech Stack
- Model: ai4bharat/IndicBART
- Framework: PyTorch + Hugging Face Transformers
- Backend: FastAPI
- Language: Hindi (Devanagari)

## Project Structure

horror-story-created/
├── data/
│   ├── raw/              ← Hindi horror stories
│   ├── processed/        ← Cleaned training data
│   ├── data_prep.py      ← Data preparation
│   └── clean_data.py     ← Data cleaning
├── backend/
│   ├── model/
│   │   ├── config.py     ← Hyperparameters
│   │   ├── train.py      ← Training script
│   │   └── generate.py   ← Story generation
│   └── api/
│       └── main.py       ← FastAPI server
├── frontend/
│   └── index.html        ← Web UI
└── requirements.txt


