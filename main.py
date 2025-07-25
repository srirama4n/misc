from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from typing import AsyncGenerator
import time

app = FastAPI(
    title="Text Streaming API",
    description="A FastAPI application that accepts text input and returns streaming data",
    version="1.0.0"
)

class TextInput(BaseModel):
    text: str
    stream_delay: float = 0.1  # Delay between chunks in seconds
    chunk_size: int = 10  # Characters per chunk

@app.get("/")
async def root():
    return {"message": "Text Streaming API is running! Use POST /stream-text to stream text data."}

@app.post("/stream-text")
async def stream_text(input_data: TextInput) -> StreamingResponse:
    """
    Accept text input and return it as a streaming response.
    Each chunk contains a portion of the text with metadata.
    """
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        text = input_data.text
        chunk_size = input_data.chunk_size
        delay = input_data.stream_delay
        
        total_chunks = (len(text) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            chunk_number = (i // chunk_size) + 1
            
            # Create a data object with metadata
            data = {
                "chunk_number": chunk_number,
                "total_chunks": total_chunks,
                "text": chunk,
                "progress": round((chunk_number / total_chunks) * 100, 2),
                "timestamp": time.time()
            }
            
            # Yield the data as JSON string with newline
            yield f"data: {json.dumps(data)}\n\n"
            
            # Add delay between chunks
            await asyncio.sleep(delay)
        
        # Send completion signal
        yield f"data: {json.dumps({'status': 'completed', 'timestamp': time.time()})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.post("/stream-words")
async def stream_words(input_data: TextInput) -> StreamingResponse:
    """
    Accept text input and return it word by word as a streaming response.
    """
    
    async def generate_word_stream() -> AsyncGenerator[str, None]:
        words = input_data.text.split()
        delay = input_data.stream_delay
        
        for i, word in enumerate(words):
            data = {
                "word_number": i + 1,
                "total_words": len(words),
                "word": word,
                "progress": round(((i + 1) / len(words)) * 100, 2),
                "timestamp": time.time()
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(delay)
        
        # Send completion signal
        yield f"data: {json.dumps({'status': 'completed', 'timestamp': time.time()})}\n\n"
    
    return StreamingResponse(
        generate_word_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.post("/stream-characters")
async def stream_characters(input_data: TextInput) -> StreamingResponse:
    """
    Accept text input and return it character by character as a streaming response.
    """
    
    async def generate_char_stream() -> AsyncGenerator[str, None]:
        text = input_data.text
        delay = input_data.stream_delay
        
        for i, char in enumerate(text):
            data = {
                "char_number": i + 1,
                "total_chars": len(text),
                "character": char,
                "progress": round(((i + 1) / len(text)) * 100, 2),
                "timestamp": time.time()
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(delay)
        
        # Send completion signal
        yield f"data: {json.dumps({'status': 'completed', 'timestamp': time.time()})}\n\n"
    
    return StreamingResponse(
        generate_char_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 