import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Review:
    review_id: str #리뷰ID
    user_name: Optional[str] #유저 이름
    playtime_hours: Optional[float] #플레이타임
    sentiment: str #긍정/부정
    review_text: str #리뷰
    date_posted: str #작성일자
    helpful_count: int #이 리뷰가 도움이 되었어요

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'Review':
        data = json.loads(json_str)
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)

class JsonHandler:
    def __init__(self, filename="output.json"):
        self.filename = Path(filename)
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self.first = True
        with self.filename.open('w', encoding='utf-8') as f:
            f.write("[\n")
            
    def append(self, review: Review):
        with self.filename.open('a', encoding='utf-8') as f:
            if not self.first:
                f.write(",\n")
            f.write("  " + review.to_json())
        self.first = False
        
    def close(self):
        with self.filename.open('a', encoding='utf-8') as f:
            f.write("\n]\n")
