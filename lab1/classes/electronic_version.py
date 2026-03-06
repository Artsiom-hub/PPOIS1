from dataclasses import dataclass


@dataclass
class ElectronicVersion:
    journal_id: int
    url: str

    def publish(self) -> str:
        return f"Electronic version available at {self.url}"