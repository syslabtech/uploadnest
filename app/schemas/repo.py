from pydantic import BaseModel

class RepositoryResponse(BaseModel):
    id: int
    name: str
    url: str
    created_at: str
