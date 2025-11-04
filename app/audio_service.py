import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

# Initialize the AsyncOpenAI client.
# It automatically finds and uses the OPENAI_API_KEY from your environment.
client = AsyncOpenAI()

async def text_to_audio_sync(text: str) -> bytes:
    """
    Converts a text string to an MP3 audio file (as bytes) synchronously.
    This is used for the downloadable audio file.
    
    Args:
        text (str): The text to convert into speech.

    Returns:
        bytes: The complete MP3 audio data.
    """
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",  # You can experiment with other voices: echo, fable, onyx, nova, shimmer
        input=text,
    )
    # The response object has a `read()` method that returns the audio bytes.
    return response.read()

async def text_to_audio_stream(text: str):
    """
    Converts a text string to a streaming MP3 audio file.
    This is used for the audio streaming endpoint.

    Args:
        text (str): The text to convert into speech.
    
    Yields:
        bytes: Chunks of the MP3 audio data as they become available.
    """
    async with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=text,
    ) as response:
        # Stream the audio data in chunks
        async for chunk in response.iter_bytes():
            yield chunk