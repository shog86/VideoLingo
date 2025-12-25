from core.utils import *
from core.asr_backend.demucs_vl import demucs_audio
from core.asr_backend.audio_preprocess import process_transcription, convert_video_to_audio, split_audio, save_results, normalize_audio_volume
from core._1_ytdlp import find_video_files
from core.utils.models import *

@check_file_exists(_2_CLEANED_CHUNKS)
def transcribe():
    # 1. video to audio
    video_file = find_video_files()
    convert_video_to_audio(video_file)

    # 2. Demucs vocal separation:
    if load_key("demucs"):
        demucs_audio()
        vocal_audio = normalize_audio_volume(_VOCAL_AUDIO_FILE, _VOCAL_AUDIO_FILE, format="mp3")
    else:
        vocal_audio = _RAW_AUDIO_FILE

    # 3. Extract audio
    segments = split_audio(_RAW_AUDIO_FILE)
    
    # 4. Transcribe audio by clips
    all_results = []
    runtime = load_key("whisper.runtime")
    if runtime == "mlx":
        from core.asr_backend.mlx_whisper_local import transcribe_audio as ts, load_whisper_model
        rprint("[cyan]🎤 Transcribing audio with MLX-Whisper (Mac Optimized)...[/cyan]")
        whisper_model_name = load_key("whisper.model")
        load_whisper_model(whisper_model_name)
    elif runtime == "elevenlabs":
        from core.asr_backend.elevenlabs_asr import transcribe_audio_elevenlabs as ts
        rprint("[cyan]🎤 Transcribing audio with ElevenLabs API...[/cyan]")
    else:
        # Fallback to MLX if specified runtime is missing or legacy
        from core.asr_backend.mlx_whisper_local import transcribe_audio as ts, load_whisper_model
        rprint(f"[yellow]⚠️ Runtime '{runtime}' is no longer supported on this Mac-optimized version. Falling back to MLX...[/yellow]")
        whisper_model_name = load_key("whisper.model")
        load_whisper_model(whisper_model_name)

    for start, end in segments:
        result = ts(_RAW_AUDIO_FILE, vocal_audio, start, end)
        all_results.append(result)
    
    # 5. Combine results
    combined_result = {'segments': []}
    for result in all_results:
        combined_result['segments'].extend(result['segments'])
    
    # 6. Process df
    df = process_transcription(combined_result)
    save_results(df)
        
if __name__ == "__main__":
    transcribe()