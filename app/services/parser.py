import io

from azure.ai.documentintelligence import (
    DocumentIntelligenceClient
)
from azure.core.credentials import AzureKeyCredential


class AzureTextExtractor:
    def __init__(self, endpoint: str, key: str):
        self.client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

    def extract(self, content: bytes) -> str:
        poller = self.client.begin_analyze_document(
            "prebuilt-read",
            body=io.BytesIO(content),
        )

        result = poller.result()

        lines = []
        for page in result.pages:
            for line in page.lines or []:
                lines.append(line.content)

        # DOCX files may come back without per-page lines, only the full text.
        return "\n".join(lines) or result.content
