import os

from trainer import Trainer, TrainerArgs

from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig
from TTS.utils.manage import ModelManager

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
# Note: we recommend that BATCH_SIZE * GRAD_ACUMM_STEPS need to be at least 252 for more efficient training. You can increase/decrease BATCH_SIZE but then set GRAD_ACUMM_STEPS accordingly.

# Define here the dataset that you want to use for the fine-tuning on.
config_dataset = BaseDatasetConfig(
    formatter="ljspeech",
    dataset_name="bbanghyong",
    path="C:/Users/Brad/Documents/Dataset/bbanghyong/content",
    meta_file_train="C:/Users/Brad/Documents/Dataset/bbanghyong/content/metadata.txt",
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
    "C:/Users/Brad/Documents/Dataset/bbanghyong/content/wavs/audio2.wav"  # speaker reference to be used in training test sentences
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
            {
                "text": "또 다른 걱정거리들이 생길 거예요. 항상 골치 아픈 일들은 새롭게 일어나니까요. 한 가지가 해결되면 또 다른 문제가 이어지죠. 나이를 먹으니 생각할 것도, 결정해야 할 일도 많아져요. 뭐가 옳은지 곰곰이 생각하고 결정하느라 늘 바빠요. 어른이 된다는 건 쉬운 일이 아니에요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "이 세상에서 무언가를 얻거나 이루려면 반드시 그만한 대가를 치러야 한다. 야망을 품는 것은 가치 있는 일이지만 합당한 노력과 절제와 불안과 좌절 없이 얻어지지는 않는 법이다.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "앤은 발 앞에 높인 길이 아무리 좁더라도 그 길을 따라 잔잔한 행복의 꽃이 피어난다는 걸 알고 있었다. 정직한 일과 훌륭한 포부와 마음 맞는 친구가 있다는 기쁨은 온전히 앤의 것이었다.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "아무리 황량하고 따분해도 다른 아름다운 곳보다 고향에서 살고 싶어 하는 게 사람이에요. 세상에 집보다 좋은 곳은 없거든요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "바보들은 심장이 있어도 그걸로 무엇을 해야 하는지 몰라요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "살아 있는 존재라면 누구나 위험 앞에서 두려움을 느껴. 진정한 용기란 두려움에도 불구하고 위험에 맞서는 것인데, 너는 이미 그런 용기를 충분히 갖고 있어.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "너는 작가가 되지 않아도, 배우가 되지 않아도, 그저 너이기에 사랑스럽고 완전한 존재란다. 다른 무엇이 되려고 애쓰지 않아도 좋아. 너는 그저 너, 너다운 너이기만 하면 된단다.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "소설을 쓰며 사는 삶보다 소설처럼 살아가는 삶이 훨씬 더 재미있을 거예요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "저는 매 순간 제가 행복하다는 사실을 온전히 느껴요. 아무리 속상한 일이 생겨도 그 사실을 잊지 않을 거예요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "저는 인간에게 가장 필요한 자질은 상상력이라고 생각합니다. 상상력이 있어야 타인을 이해할 수 있고, 그래야 친절할 수도, 남을 이해할 수도, 또 동정할 수도 있으니까요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "자신에게 찾아오는 기회를 붙잡을 의지만 있다면 세상은 행복으로 가득 차 있고, 가볼 곳도 많아요. 비법은 바로 유연한 마음이에요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "정말 소중한 것은 커다란 기쁨이 아니에요. 사소한 곳에서 얻는 기쁨이 더 중요해요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "큰 시련이 닥쳤을 때만 인격이 필요한 게 아니에요. 위기에 대처하거나, 치명적인 비극에 맞서는 건 누구나 할 수 있지만, 그날그날의 사소한 불운들을 웃음으로 넘기는 일은 '정신력'이 없다면 불가능한 일이에요. 제가 키워나가야 할 게 바로 이런 종류의 인격이에요.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "눈이 보이지 않으면 눈이 보이는 코끼리와 살을 맞대고 걸으면 되고, 다리가 불편하면 다리가 튼튼한 코끼리에게 기대서 걸으면 돼. 같이 있으면 그런 건 큰 문제가 아니야.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
            {
                "text": "누구든 너를 좋아하게 되면, 네가 누구인지 알아볼 수 있어. 아마 처음에는 호기심으로 너를 관찰하겠지. 하지만 점 너를 좋아하게 되어서 너를 눈여겨보게 되고, 네가 가까이 있을 때는 어떤 냄새가 나는지 알게 될 거고, 네가 걸을 때는 어떤 소리가 나는지에도 귀 기울이게 될 거야. 그게 바로 너야.",
                "speaker_wav": SPEAKER_REFERENCE,
                "language": LANGUAGE,
            },
        ],
    )

    # init the model from config
    model = GPTTrainer.init_from_config(config)

    # load training samples
    train_samples, eval_samples = load_tts_samples(
        DATASETS_CONFIG_LIST,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )

    # init the trainer and 🚀
    trainer = Trainer(
        TrainerArgs(
            restore_path=None,  # xtts checkpoint is restored via xtts_checkpoint key so no need of restore it using Trainer restore_path parameter
            skip_train_epoch=False,
            start_with_eval=START_WITH_EVAL,
            grad_accum_steps=GRAD_ACUMM_STEPS,
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
