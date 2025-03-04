def download_all_melo_model(melo):
    languages = ["EN", "EN_V2", "EN_NEWEST", "ES", "FR", "ZH", "JP", "KR"]

    for lang in languages:
        melo.load(lang)
        # melo.infer("Hello, world!", audio_name=f"hello_{lang}")
        # melo.infer("你好，我是MeloTTS生成的语音。", audio_name=f"hello_melo_{lang}")
        melo.show_speakers()
        melo.unload()