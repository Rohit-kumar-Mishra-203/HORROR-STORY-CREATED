
# All settings in one place


# Model
MODEL_NAME        = "ai4bharat/IndicBART"
SAVED_MODEL_DIR   = "saved_model"

# Data
TRAIN_FILE        = "data/processed/train.txt"
VAL_FILE          = "data/processed/val.txt"

# Training (optimized for RTX 2050 — 4GB VRAM)
EPOCHS                      = 5
BATCH_SIZE                  = 2
LEARNING_RATE               = 3e-5
MAX_SOURCE_LENGTH           = 128
MAX_TARGET_LENGTH           = 512
GRADIENT_ACCUMULATION_STEPS = 4      # simulates batch size of 8
WARMUP_STEPS                = 100
SAVE_STEPS                  = 500
LOGGING_STEPS               = 100
FP16                        = True   # saves VRAM on RTX 2050

# Generation
MAX_GEN_LENGTH      = 1024
MIN_GEN_LENGTH      = 400
NUM_BEAMS           = 5
TEMPERATURE         = 0.85
REPETITION_PENALTY  = 3.0
TOP_P               = 0.92
TOP_K               = 40
LENGTH_PENALTY      = 2.0