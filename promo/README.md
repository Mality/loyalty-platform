# Promo Service

A gRPC microservice for managing promotional codes in the loyalty platform.

## Overview

This service provides functionality for managing promotional codes through a gRPC API. It supports creating, reading, updating, and deleting promotional codes, as well as listing them with pagination.

## Features

- Create promotional codes
- List promotional codes with pagination
- Get promotional code by ID
- Update promotional code
- Delete promotional code
- In-memory storage (can be extended to use a database)

## API

### PromoService

#### CreatePromo
```protobuf
rpc CreatePromo (PromoRequest) returns (PromoResponse)
```
Creates a new promotional code.

#### ListPromos
```protobuf
rpc ListPromos (PromoListRequest) returns (PromoListResponse)
```
Retrieves a paginated list of promotional codes.

#### GetPromo
```protobuf
rpc GetPromo (PromoRequest) returns (PromoResponse)
```
Retrieves a specific promotional code by ID.

#### UpdatePromo
```protobuf
rpc UpdatePromo (PromoUpdateRequest) returns (PromoResponse)
```
Updates an existing promotional code.

#### DeletePromo
```protobuf
rpc DeletePromo (PromoDeleteRequest) returns (Empty)
```
Deletes a promotional code.

### Message Types

#### PromoRequest
```protobuf
message PromoRequest {
  string id = 1;
  string name = 2;
  string description = 3;
  string creator_id = 4;
  float discount_amount = 5;
  string code = 6;
}
```

#### PromoResponse
```protobuf
message PromoResponse {
  string id = 1;
  string name = 2;
  string description = 3;
  string creator_id = 4;
  float discount_amount = 5;
  string code = 6;
  string created_at = 7;
  string updated_at = 8;
}
```

## Setup

### Prerequisites

- Docker
- Docker Compose (recommended)

### Development

1. Build and run the service using Docker:
```bash
docker build -t promo-service .
docker run -p 50051:50051 promo-service
```

Or using Docker Compose (recommended):
```bash
docker-compose up --build
```

### Production Deployment

1. Build the production image:
```bash
docker build -t promo-service:prod .
```

2. Deploy using your preferred orchestration tool (e.g., Kubernetes, Docker Swarm)

## Environment Variables

- `PROMO_SERVICE_HOST` - Host to bind the service to (default: "0.0.0.0")
- `PROMO_SERVICE_PORT` - Port to bind the service to (default: 50051)

## Project Structure

```
promo/
├── src/
│   ├── proto/
│   │   └── promo.proto
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Error Handling

The service includes basic error handling for:
- Invalid promo IDs
- Missing promos
- Invalid input data

## Future Improvements

1. Add database integration (e.g., PostgreSQL)
2. Implement authentication and authorization
3. Add input validation
4. Add unit tests
5. Add logging and monitoring
6. Add rate limiting
7. Add caching layer

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
