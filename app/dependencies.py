from pathlib import PurePath

from fastapi import HTTPException, UploadFile

from app.schemas import FileType, ValidatedUpload
#Size params
MAX_UPLOAD_BYTES = 20 * 1024 * 1024 #20MB
CHUNK_BYTES = 1024 * 1024 #1MB

#Document type validation
EXTENSIONS = {".pdf": FileType.PDF, ".docx": FileType.DOCX}
MAGIC_BYTES = {FileType.PDF: b"%PDF-", FileType.DOCX: b"PK\x03\x04"}

async def validated_upload(file: UploadFile) -> ValidatedUpload:
    #ex: resume.pdf
    filename = PurePath(file.filename or "").name
    file_type = EXTENSIONS.get(PurePath(filename).suffix.lower())
    #Quick check before reading the file
    if file_type is None:
        raise HTTPException(415, "Only .pdf and .docx files are accepted")
    chunks = []
    size = 0
    while True:
        chunk = await file.read(CHUNK_BYTES)

        if not chunk: #No more chunks
            break
        size += len(chunk)
        if size > MAX_UPLOAD_BYTES:
            raise HTTPException(413, f"File exceeds {MAX_UPLOAD_BYTES} bytes")
        chunks.append(chunk)

    if size == 0:
        raise HTTPException(400, "File is empty")

    content = b"".join(chunks)
    if not content.startswith(MAGIC_BYTES[file_type]):
        raise HTTPException(415, f"File content is not a valid {file_type.value}")

    return ValidatedUpload(filename=filename, file_type=file_type, size_bytes=size, content=content)
