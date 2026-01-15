import os
from pathlib import Path

from config import OPENAI_API_KEY, pdf_path

from openai import OpenAI, RateLimitError
import pygame
from PyPDF2 import PdfReader

client = OpenAI(api_key=OPENAI_API_KEY)

# Open PDF (y/n)
user_input = input('Open PDF? (y/n) ')
while user_input not in ['y', 'n']:
    print(f'"{user_input}" is not a valid response.')
    user_input = input('Open PDF? (y/n) ')

start = int(input('Starting page: '))
end = int(input('Ending page: '))
while end <= start:
    print('Ending page cannot include or be earlier than starting page.')
    start = int(input('Starting page: '))
    end = int(input('Ending page: '))

# Load PDF and extract text from pages 0-4
try:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)

        # Create a dir for audio (doesn't fail if exists. Exist is ok.)
        output_dir = Path('textbook_audio')
        output_dir.mkdir(exist_ok=True)

        # Extract text from PDF
        for page_num in range((start - 1), end):

            # Check for existing mp3
            output_file = output_dir / f'page_{page_num + 1}.mp3'
            if output_file.exists():
                print(f'File "{str(output_file.name)}" already exists.')

            else:
                print(f'Processing page {page_num + 1}')
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                lines = text.split('\n')
                # Remove first and last line (header/footer)
                text = '\n'.join(lines[1:-1])

                if len(text) < 100:
                    print(f'Small file text: {text}')
                    print(f'Page {page_num + 1} only has {len(text)} words. Skipping page.')
                    continue

                print(f'Extracted {len(text)} characters')

                # Generate audio per page
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy", # Options: alloy, echo, fable, onyx, nova, shimmer
                    input=text
                )

                # Save with page number
                response.write_to_file(str(output_file))
                print(f'Saved {output_file}')

    # Open file based on prior input
    if user_input == 'y':
        os.startfile(pdf_path)
    elif user_input == 'n':
        pass

    pygame.mixer.init()

    # Play files sequentially
    for page_num in range(start, end + 1):
        audio_file = output_dir / f'page_{page_num}.mp3'
        if audio_file.exists():
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.play()
            print(f'Playing {audio_file}')

            # While the video is not playing:
            while pygame.mixer.music.get_busy():
                pygame.time.delay(100) # Wait 100ms

            print(f'File {audio_file} has finished playing.')


except RateLimitError:
    print("Exceeded rate limit.")
    quit()