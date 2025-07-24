# Simple Node.js API Demo

A simple Express.js API for demonstrating Agentic IaC analysis capabilities.

## Overview

This is a demo REST API built with Node.js and Express.js that showcases:
- RESTful endpoint design
- Health monitoring
- Error handling
- JSON responses
- Basic CRUD operations

## Features

- **Health Monitoring**: Built-in health check endpoint
- **RESTful Design**: Follows REST API conventions
- **Error Handling**: Comprehensive error responses
- **JSON API**: All responses in JSON format
- **Demo Data**: Sample endpoints with mock data
- **Docker Ready**: Includes Dockerfile for containerization

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message and API status |
| GET | `/health` | Health check with system metrics |
| GET | `/api/info` | API documentation and metadata |
| GET | `/api/users` | List demo users |
| POST | `/api/users` | Create a new user |

## Installation and Setup

### Prerequisites
- Node.js 16+ 
- npm (comes with Node.js)
