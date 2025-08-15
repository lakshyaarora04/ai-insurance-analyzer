def chunk_text(text, chunk_size=800, chunk_overlap=200):
    """
    Improved chunking strategy for better document coverage.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk (default: 800 characters)
        chunk_overlap: Overlap between chunks (default: 200 characters)
    
    Returns:
        List of text chunks
    """
    chunks = []
    
    # Clean up the text
    text = text.strip()
    
    # If text is shorter than chunk_size, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    # Create overlapping chunks
    start = 0
    while start < len(text):
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at a sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 characters of the chunk
            search_start = max(start + chunk_size - 100, start)
            search_end = min(end + 50, len(text))
            
            # Find the last sentence ending in this range
            sentence_endings = ['.', '!', '?', '\n\n']
            last_sentence_end = -1
            
            for ending in sentence_endings:
                pos = text.rfind(ending, search_start, search_end)
                if pos > last_sentence_end:
                    last_sentence_end = pos
            
            # If we found a sentence ending, use it as the chunk boundary
            if last_sentence_end > start + chunk_size // 2:  # Only if it's not too early
                end = last_sentence_end + 1
        
        # Extract the chunk
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move to next chunk with overlap
        start = end - chunk_overlap
        
        # Ensure we don't go backwards
        if start <= 0:
            start = end
    
    return chunks
