# Milestone 1 – Legacy System Analysis and Requirements Gathering

## Overview
This milestone analyzes the legacy IVR system and gathers requirements for migrating to a modern Conversational AI solution using Twilio, ACS, middleware, and backend platforms (BAP).  
Goal: Replace rigid IVR menus with a user-directed, natural conversational experience.

## Legacy IVR Limitations
- Rigid, menu-driven dialogues  
- No Natural Language Understanding (NLU)  
- High maintenance and shrinking vendor support (e.g., Genesys, Nuance)  
- Difficult integration with modern architectures  
- Performance and scalability risks under load

## Modern ACS Architecture
**Flow:** User → Twilio → Middleware → ACS → Backend (BAP)  
**Features:**  
- Natural language conversation and context management  
- ASR, NLU, LLM-based dialogue  
- Streaming ASR/TTS for low-latency (<800ms) responses  
- Backend integration and omnichannel support  
- Session handling with unique session IDs and TTL

## Milestone 1 Deliverables
- Legacy IVR analysis and limitations report  
- Functional and non-functional requirements  
- Initial architecture diagram and technical documentation  
- Performance and latency considerations
