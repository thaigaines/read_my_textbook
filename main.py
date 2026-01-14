import os
from pathlib import Path
import time

from config import OPENAI_API_KEY, pdf_path

from openai import OpenAI, RateLimitError
from PyPDF2 import PdfReader

client = OpenAI(api_key=OPENAI_API_KEY)

start = int(input('Starting page: '))
end = int(input('Ending page: '))
while end < start:
    print('Ending page cannot be earlier that starting page.')
    start = input('Starting page: ')
    end = input('Ending page: ')


# Load PDF and extract text from pages 0-4
try:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)

        output_dir = Path('textbook_audio')
        output_dir.mkdir(exist_ok=True)

        # Extract text from PDF
        for page_num in range((start - 1), end):
            print(f'Processing page {page_num + 1}')
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if len(text) < 100:
                print(f'Page {page_num + 1} only has {len(text)} words. Skipping page.')

            print(f'Extracted {len(text)} characters')

            # Generate audio per page
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy", # Options: alloy, echo, fable, onyx, nova, shimmer
                input=text
            )

            # Save with page number
            output_file = output_dir / f'page_{page_num + 1}.mp3'
            response.write_to_file(str(output_file))
            print(f'Saved {output_file}')

            time.sleep(1)

    first_page = output_dir / f'page_{start}.mp3'
    os.startfile(f'{first_page}')
        
except RateLimitError:
    print("Exceeded rate limit.")
    quit()