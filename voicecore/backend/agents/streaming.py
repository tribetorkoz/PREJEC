import asyncio
import re
from typing import List, AsyncIterator


class AudioStreamingEngine:
    """
    Start playing audio after first 50ms of generation.
    ElevenLabs supports streaming — use it.
    This makes responses feel instant.
    """
    
    def __init__(self, tts_client):
        self.tts = tts_client
    
    async def stream_response(self, text: str, transport) -> AsyncIterator[bytes]:
        sentences = self.split_into_sentences(text)
        
        tasks = []
        for i, sentence in enumerate(sentences):
            task = asyncio.create_task(
                self.generate_and_send(sentence, transport, priority=i)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def generate_and_send(self, sentence: str, transport, priority: int):
        try:
            audio_data = await self.tts.generate(sentence)
            await transport.send_audio(audio_data, priority=priority)
        except Exception as e:
            print(f"Error generating audio for sentence: {e}")
    
    def split_into_sentences(self, text: str) -> List[str]:
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        return sentences
    
    async def stream_with_vad(
        self,
        text: str,
        transport,
        voice_activity_detector
    ) -> AsyncIterator[bytes]:
        sentences = self.split_into_sentences(text)
        
        for sentence in sentences:
            await transport.send_text(sentence)
            
            while not voice_activity_detector.is_silent():
                await asyncio.sleep(0.1)
            
            audio_data = await self.tts.generate(sentence)
            yield audio_data


class ChunkedAudioStreamer:
    """
    Alternative streaming that splits response into chunks
    for even faster first audio.
    """
    
    def __init__(self, tts_client, chunk_size: int = 50):
        self.tts = tts_client
        self.chunk_size = chunk_size
    
    async def stream_response(self, text: str, transport):
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= self.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        tasks = [
            self.tts.generate(chunk)
            for chunk in chunks
        ]
        
        results = await asyncio.gather(*tasks)
        
        for audio in results:
            await transport.send_audio(audio)
