import os
import subprocess

def create_audio():
    os.makedirs('output', exist_ok=True)
    audio_path = 'output/audio.mp3'
    if not os.path.exists(audio_path):
        print('Creating audio bed...')
        cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=10', '-filter:a', 'volume=0.2', audio_path]
        try:
            subprocess.run(cmd, check=True)
            print('Audio generated.')
        except Exception as e:
            print(f'Audio error: {e}')

if __name__ == '__main__':
    create_audio()
