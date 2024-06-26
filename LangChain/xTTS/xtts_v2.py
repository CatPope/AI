import os
import torch
from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig
from TTS.utils.manage import ModelManager

# CUDA 환경 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Logging parameters
RUN_NAME = "GPT_XTTS_v2.0_BBANGHYONG_FT"
PROJECT_NAME = "XTTS_trainer"
DASHBOARD_LOGGER = "tensorboard"
LOGGER_URI = None

# Set here the path that the checkpoints will be saved. Default: ./run/training/
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run", "training")

# Training Parameters
OPTIMIZER_WD_ONLY_ON_WEIGHTS = True  # for multi-gpu training please make it False
START_WITH_EVAL = True  # if True it will star with evaluation
BATCH_SIZE = 3  # set here the batch size
GRAD_ACUMM_STEPS = 84  # set here the grad accumulation steps

# Note: we recommend that BATCH_SIZE * GRAD_ACUMM_STEPS need to be at least 252 for more efficient training.
# You can increase/decrease BATCH_SIZE but then set GRAD_ACUMM_STEPS accordingly.

# Define here the dataset that you want to use for the fine-tuning on.
config_dataset = BaseDatasetConfig(
    formatter="ljspeech",
    dataset_name="bbanghyong",
    path="D:/GitHub/AI/LangChain/xTTS/Train_data",
    meta_file_train="D:/GitHub/AI/LangChain/xTTS/Train_data/metadata.txt",
    language="ko",
)

# Add here the configs of the datasets
DATASETS_CONFIG_LIST = [config_dataset]

# Define the path where XTTS v2.0.1 files will be downloaded
CHECKPOINTS_OUT_PATH = os.path.join(OUT_PATH, "XTTS_v2.0_original_model_files/")
os.makedirs(CHECKPOINTS_OUT_PATH, exist_ok=True)

# DVAE files
DVAE_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/dvae.pth"
MEL_NORM_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/mel_stats.pth"

# Set the path to the downloaded files
DVAE_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(DVAE_CHECKPOINT_LINK))
MEL_NORM_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(MEL_NORM_LINK))

# download DVAE files if needed
if not os.path.isfile(DVAE_CHECKPOINT) or not os.path.isfile(MEL_NORM_FILE):
    print(" > Downloading DVAE files!")
    ModelManager._download_model_files([MEL_NORM_LINK, DVAE_CHECKPOINT_LINK], CHECKPOINTS_OUT_PATH, progress_bar=True)

# Download XTTS v2.0 checkpoint if needed
TOKENIZER_FILE_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/vocab.json"
XTTS_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/model.pth"

# XTTS transfer learning parameters: You we need to provide the paths of XTTS model checkpoint that you want to do the fine tuning.
TOKENIZER_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(TOKENIZER_FILE_LINK))  # vocab.json file
XTTS_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(XTTS_CHECKPOINT_LINK))  # model.pth file

# download XTTS v2.0 files if needed
if not os.path.isfile(TOKENIZER_FILE) or not os.path.isfile(XTTS_CHECKPOINT):
    print(" > Downloading XTTS v2.0 files!")
    ModelManager._download_model_files(
        [TOKENIZER_FILE_LINK, XTTS_CHECKPOINT_LINK], CHECKPOINTS_OUT_PATH, progress_bar=True
    )

# Training sentences generations
SPEAKER_REFERENCE = [
    "D:/GitHub/AI/LangChain/xTTS/Train_data/wavs/audio2.wav"  # speaker reference to be used in training test sentences
]
LANGUAGE = config_dataset.language


def main():
    # init args and config
    model_args = GPTArgs(
        max_conditioning_length=132300,  # 6 secs
        min_conditioning_length=66150,  # 3 secs
        debug_loading_failures=False,
        max_wav_length=255995,  # ~11.6 seconds
        max_text_length=200,
        mel_norm_file=MEL_NORM_FILE,
        dvae_checkpoint=DVAE_CHECKPOINT,
        xtts_checkpoint=XTTS_CHECKPOINT,  # checkpoint path of the model that you want to fine-tune
        tokenizer_file=TOKENIZER_FILE,
        gpt_num_audio_tokens=1026,
        gpt_start_audio_token=1024,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )

    # define audio config
    audio_config = XttsAudioConfig(sample_rate=22050, dvae_sample_rate=22050, output_sample_rate=24000)

    # training parameters config
    config = GPTTrainerConfig(
        output_path=OUT_PATH,
        model_args=model_args,
        run_name=RUN_NAME,
        project_name=PROJECT_NAME,
        run_description="""
            GPT XTTS training
            """,
        dashboard_logger=DASHBOARD_LOGGER,
        logger_uri=LOGGER_URI,
        audio=audio_config,
        batch_size=BATCH_SIZE,
        batch_group_size=48,
        eval_batch_size=BATCH_SIZE,
        num_loader_workers=8,
        eval_split_max_size=256,
        print_step=50,
        plot_step=100,
        log_model_step=1000,
        save_step=10000,
        save_n_checkpoints=1,
        save_checkpoints=True,
        # target_loss="loss",
        print_eval=False,
        # Optimizer values like tortoise, pytorch implementation with modifications to not apply WD to non-weight parameters.
        optimizer="AdamW",
        optimizer_wd_only_on_weights=OPTIMIZER_WD_ONLY_ON_WEIGHTS,
        optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-2},
        lr=5e-06,  # learning rate
        lr_scheduler="StepLR",
        # it was adjusted accordly for the new step scheme
        lr_scheduler_params={"step_size": 50, "gamma": 0.5, "last_epoch": -1},
        test_sentences=[
            {
                "text": "나에게는 그들보다 이 점등인이 더 나은 사람이야. 적어도 점등인은 그들과는 달리, 남을 위해 일하기 때문이야. 너는 나에게 이 세상에 단 하나뿐인 존재가 되는 거고, 나도 너에게 세상에 하나뿐인 존재가 되는 거야.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "넌 네가 길들인 것에 영원히 책임이 있어. 누군가에게 길들여진다는 것은 눈물을 흘릴 일이 생긴다는 뜻일지도 몰라. 네 장미꽃이 소중한 이유는 그 꽃을 위해 네가 애쓴 시간 때문이야. 다른 사람에게는 열어주지 않는 문을 당신에게만 열어주는 사람이 있다면 그 사람은 당신의 진정한 친구이다.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "세상에서 가장 어려운 일은 사람이 사람의 마음을 얻는 일이야. 내가 좋아하는 사람이 나를 좋아해 주는 건 기적이야.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "질문을 하지 않으면 세상 일을 어떻게 알겠어요?",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "세상엔 재미있는 일이 참 많아요. 우리가 모든 걸 다 안다면 사는 재미가 반으로 줄어들 거예요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
        ],
    )

    # init the model from config
    model = GPTTrainer.init_from_config(config)

    # move model to GPU if available
    model = model.to(device)

    # load training samples
    train_samples, eval_samples = load_tts_samples(
        DATASETS_CONFIG_LIST,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )

    # move samples to GPU
    train_samples = [sample.to(device) for sample in train_samples]
    eval_samples = [sample.to(device) for sample in eval_samples]

    # init the trainer and start training
    trainer = Trainer(
        TrainerArgs(
            device=device,
            start_with_eval=START_WITH_EVAL,
            batch_size=config.batch_size,
            grad_accumulation_steps=GRAD_ACUMM_STEPS,
            num_loader_workers=config.num_loader_workers,
            batch_group_size=config.batch_group_size,
            print_step=config.print_step,
            plot_step=config.plot_step,
            log_model_step=config.log_model_step,
            save_step=config.save_step,
            save_n_checkpoints=config.save_n_checkpoints,
            save_checkpoints=config.save_checkpoints,
            print_eval=config.print_eval,
        ),
        config,
        output_path=OUT_PATH,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )
    trainer.fit()


if __name__ == "__main__":
    main()
