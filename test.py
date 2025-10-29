from pydub import AudioSegment

# Carrega o arquivo WAV original
music = AudioSegment.from_wav("sounds/music_fundo.wav")

# Salva em formato OGG (recomendado pelo Pygame Zero)
music.export("sounds/music.ogg", format="ogg")
