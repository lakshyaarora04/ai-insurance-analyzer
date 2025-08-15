def chunk_text(text, max_tokens=200):
    # Basic chunking based on sentences
    import re
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk.split()) + len(sentence.split()) <= max_tokens:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
