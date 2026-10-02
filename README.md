# Mizan Voice Agent

A production-ready sovereign voice agent backend built for enterprise and government entities, fully compliant with DESC and UAE PDPL standards.

## Features
- **Local Edge PII Scrubber**: Strips Emirates ID, UAE phone numbers, IBANs, and passports before hitting any cloud endpoints.
- **Strict Policy & Confidence Gate**: Prevents hallucinations, unauthorized legal advice, and false commitments.
- **Circuit Breaker**: Automatically fails over to human IVR on threshold breaches.
- **Semantic Caching**: High-performance multilingual vector cache for query matching.
- **Zero-Latency Static Caching**: Integrates pre-rendered ElevenLabs voice assets via Azure Blob Storage.

## Structure
```
mizan-voice-agent/
├── config/
│   └── settings.py
├── src/
│   ├── agent/
│   ├── cache/
│   ├── core/
│   ├── integrations/
│   ├── middleware/
│   └── main.py
├── scripts/
└── tests/
```
