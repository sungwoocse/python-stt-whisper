import whisper
import torch
import warnings
from pathlib import Path
from datetime import timedelta
from tqdm import tqdm
import subprocess
import os
import shutil
import urllib.request

warnings.filterwarnings("ignore")

def setup_ffmpeg():
    """FFmpeg 설정"""
    ffmpeg_path = Path.home() / '.local' / 'ffmpeg'
    ffmpeg_binary = ffmpeg_path / 'ffmpeg'
    
    if not ffmpeg_binary.exists():
        print("FFmpeg 다운로드 및 설정 중...")
        ffmpeg_path.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg 다운로드
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        archive_path = ffmpeg_path / "ffmpeg.tar.xz"
        
        print("FFmpeg 다운로드 중...")
        urllib.request.urlretrieve(url, archive_path)
        
        # 압축 해제
        print("압축 해제 중...")
        subprocess.run(['tar', 'xf', str(archive_path)], cwd=str(ffmpeg_path))
        
        # FFmpeg 바이너리 이동
        extracted_dir = next(ffmpeg_path.glob('ffmpeg-*-static'))
        shutil.move(str(extracted_dir / 'ffmpeg'), str(ffmpeg_binary))
        
        # 정리
        archive_path.unlink()
        shutil.rmtree(str(extracted_dir))
        
        # 실행 권한 부여
        ffmpeg_binary.chmod(0o755)
    
    return str(ffmpeg_binary)

def convert_to_markdown():
    """현재 디렉토리의 모든 m4a 파일을 변환"""
    # FFmpeg 설정
    ffmpeg_path = setup_ffmpeg()
    os.environ["PATH"] = f"{os.path.dirname(ffmpeg_path)}:{os.environ['PATH']}"
    
    # GPU 셋팅
    torch.cuda.empty_cache()
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")

    # 현재 디렉토리의 모든 m4a 파일 찾기
    current_dir = Path.cwd()
    m4a_files = list(current_dir.glob("*.m4a"))
    
    if not m4a_files:
        print("현재 디렉토리에 m4a 파일이 없습니다.")
        return
    
    print(f"\n발견된 파일 {len(m4a_files)}개:")
    for file in m4a_files:
        print(f"- {file.name}")

    # 출력 폴더 생성
    output_dir = Path("transcriptions")
    output_dir.mkdir(exist_ok=True)

    # 모델 로드 (large-v2)
    print("Loading model...")
    model = whisper.load_model("large-v2").cuda()
    
    # 각 파일 처리
    for audio_path in m4a_files:
        print(f"\n처리 중: {audio_path.name}")
        
        try:
            # 변환 실행
            result = model.transcribe(
                str(audio_path),
                fp16=True,
                language="en",  # 영어로 설정
                task="transcribe",
                beam_size=5,
                best_of=5,
                verbose=True
            )
            
            # 마크다운 생성
            markdown_content = f"# Transcription of {audio_path.name}\n\n"
            markdown_content += "| Time | Content |\n|------|--------|\n"
            
            # 내용 정리
            print("마크다운 생성 중...")
            segments = result["segments"]
            for segment in tqdm(segments):
                timestamp = str(timedelta(seconds=int(segment["start"])))
                markdown_content += f"| {timestamp} | {segment['text'].strip()} |\n"

            # 파일 저장
            output_file = output_dir / f"{audio_path.stem}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            print(f"완료: {output_file}")
            
        except Exception as e:
            print(f"에러 발생: {str(e)}")
            print("상세 에러:")
            import traceback
            traceback.print_exc()
            continue
        
        finally:
            torch.cuda.empty_cache()

if __name__ == "__main__":
    convert_to_markdown()