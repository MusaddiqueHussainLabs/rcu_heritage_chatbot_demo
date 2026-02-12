from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AlulaResponse:
    """Structured response returned by AlUla Agent."""

    # Final explanation text
    answer: str

    # Image file paths to attach
    image_paths: List[str]

    # Optional inventory number
    inv_no: Optional[str] = None

    # Optional similarity confidence
    confidence: Optional[float] = None
