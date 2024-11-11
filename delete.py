import os
import glob

def delete_audio_files(directory="."):
    """
    지정된 디렉토리에서 .m4a와 .wav 파일을 삭제합니다.
    
    Args:
        directory (str): 파일을 삭제할 디렉토리 경로 (기본값: 현재 디렉토리)
    """
    # 삭제할 파일 확장자 목록
    extensions = ['*.m4a', '*.wav']
    
    try:
        # 각 확장자별로 파일 검색 및 삭제
        for ext in extensions:
            files = glob.glob(os.path.join(directory, ext))
            for file in files:
                try:
                    os.remove(file)
                    print(f"삭제됨: {file}")
                except Exception as e:
                    print(f"파일 삭제 실패: {file}")
                    print(f"에러 메시지: {str(e)}")
        
        print("\n작업 완료!")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    # 현재 디렉토리에서 실행
    delete_audio_files()
    
    # 특정 디렉토리에서 실행하려면:
    # delete_audio_files("원하는/디렉토리/경로")