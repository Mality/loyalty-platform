```mermaid
erDiagram
    PROMOS ||--o{ PROMOS_META : "has meta"

    PROMOS {
        uuid id PK
        uuid buiseness_uid FK
        text content
        datetime created_at
        datetime updated_at
    }

    PROMOS_META {
        uuid id PK
        text meta
        datetime created_at
        datetime updated_at
    }

    SALES {
        uuid id PK
        uuid buiseness_uid FK
        text content
        datetime created_at
        datetime updated_at
    }

```