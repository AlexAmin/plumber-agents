# Orchestrator

## Purpose

Central message router that coordinates communication between humans and specialized AI agents.

## What It Does

**Routes messages:**
- Receives messages from technicians and office staff (via WhatsApp or CLI)
- Routes to appropriate specialized agent (field service or office)
- Returns agent responses back to users

**Manages workflows:**
- Tracks conversation context
- Coordinates handoffs between agents
- Handles cross-role communication (e.g., office needs info from technician)

**Maintains transparency:**
- Users interact with a single entry point
- Routing happens automatically based on user role
- Seamless experience across the multi-agent system

## Goal

Provide a simple, unified interface for users while intelligently distributing work across specialized agents.
