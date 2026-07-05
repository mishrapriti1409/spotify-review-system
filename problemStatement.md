# Spotify AI Review Discovery Engine (RAG-Based Customer Intelligence Platform)

## Project Overview

Build an AI-powered **Review Discovery Engine** that aggregates customer feedback from multiple public sources, indexes the information using **Retrieval Augmented Generation (RAG)**, and provides an intelligent chatbot interface that answers questions using only the retrieved customer feedback.

The chatbot should function as an internal **AI Product Research Assistant** for Spotify, enabling product managers, UX researchers, designers, and analysts to explore customer opinions conversationally instead of manually reading thousands of reviews.

The application should have a modern **Spotify-inspired chatbot interface** with analytics dashboards and should use **Groq LLM** for response generation.

---

# Business Problem

Spotify has successfully acquired millions of users and built one of the world's most sophisticated recommendation systems.

However, a significant percentage of listening still comes from:

* Repeat playlists
* Familiar artists
* Previously discovered tracks
* Habit-based listening
* Limited exploration of new music

One of Spotify's strategic goals is to increase meaningful music discovery while reducing repetitive listening behavior.

To achieve this, product teams need an AI-powered research assistant capable of understanding millions of customer conversations and surfacing actionable insights.

The system should help answer questions backed by real customer evidence instead of assumptions.

---

# Primary Objective

Develop a Retrieval Augmented Generation (RAG) based chatbot that can answer product research questions using customer reviews and discussions collected from multiple sources.

The chatbot must retrieve relevant customer feedback first and only then generate an answer using Groq LLM.

The chatbot **must never answer from its own knowledge**. Every answer must be grounded in retrieved customer feedback.

---

# Data Sources

The application should support ingesting customer feedback from the following sources.

## Apple App Store

Collect

* Review text
* Rating
* Date
* Version
* Country (if available)

---

## Google Play Store

Collect

* Review text
* Rating
* Date
* Version
* Device
* Likes

---

## Reddit

Support collecting posts and comments from relevant subreddits including:

* r/spotify
* r/truespotify
* r/music
* r/listentothis

Collect

* Title
* Post
* Comments
* Upvotes
* Timestamp
* URL

---

## Spotify Community

Collect

* Questions
* Discussions
* Replies
* Likes
* URLs

---

## Other Community Forums

Support importing discussions from music-related public forums.

---

## Social Media

Support importing public discussions from

* Twitter/X
* YouTube Comments
* Public Facebook Posts (if supported)
* LinkedIn Discussions (optional)

---

# Data Ingestion Pipeline

Create a modular ingestion system.

Each source should have an independent connector.

Example

```
ingestion/

appstore.py

playstore.py

reddit.py

community.py

social.py
```

Each connector should

* Download data
* Normalize schema
* Clean text
* Remove duplicates
* Attach metadata
* Save locally

---

# Data Cleaning

Before indexing

Remove

* HTML
* URLs
* Duplicate reviews
* Empty reviews
* Spam
* Extra whitespace

Normalize

* Dates
* Language
* Ratings
* Metadata

Optionally translate non-English reviews.

---

# Unified Review Schema

Every review should contain

* Document ID
* Source
* Platform
* Review Text
* Rating
* Date
* URL
* Metadata
* Language
* Country
* Sentiment
* Topics
* Keywords
* Embedding

---

# AI Processing Pipeline

For every review

Generate

* Embeddings
* Sentiment
* Topics
* Keywords
* Pain Points
* Listening Intent
* Recommendation Issues
* Music Discovery Issues
* User Goals

Store all generated outputs locally.

---

# Storage Requirements

**Do not use any external database.**

Do not use

* MySQL
* PostgreSQL
* MongoDB
* Firebase
* Supabase
* SQL Server
* Redis
* ElasticSearch

The entire solution must be self-contained.

Persist all data inside the project folder.

Example structure

```
solution/

data/

raw/

processed/

embeddings/

vector_store/

analytics/

chat_history/

cache/

logs/

configs/

prompts/

backend/

frontend/
```

---

# Local Persistence

Store everything locally.

Examples

* Downloaded reviews
* Cleaned reviews
* Embeddings
* Analytics
* Chat history
* Logs
* Cached responses

Use JSON files wherever possible.

---

# Vector Store

Use **ChromaDB** in persistent local mode.

Store the vector database inside

```
solution/data/vector_store/
```

No external vector database should be required.

---

# Embedding Model

Use

* BAAI/bge-large-en-v1.5

or

* sentence-transformers/all-MiniLM-L6-v2

---

# LLM

Use **Groq API**.

Preferred models

* Llama 3.3
* Llama 4
* Mixtral
* DeepSeek

The LLM should never answer directly.

Workflow

User Question

↓

Generate Question Embedding

↓

Retrieve Top-K Reviews

↓

Build Context

↓

Groq LLM

↓

Grounded Answer

---

# Strict RAG Rules

<!-- The chatbot **must always perform retrieval before generation**. -->

Never generate answers using only LLM knowledge.

If no relevant documents are found, the chatbot must return an appropriate fallback response.

Every response should be based solely on retrieved customer feedback.

Hallucinated answers are not acceptable.

---

# Chatbot Features

Support natural language questions such as

* Why do users struggle to discover new music?
* What complaints exist about recommendations?
* Why do users repeatedly listen to the same playlists?
* What causes recommendation fatigue?
* What unmet needs appear repeatedly?
* Which user segments struggle the most?
* What feature requests appear most often?
* What complaints increased recently?
* Compare App Store vs Play Store feedback.
* What do Reddit users think about Discover Weekly?
* Why are users skipping recommendations?
* Which listening behaviors are common?

Support follow-up questions while maintaining conversation context.

---

# Chat History

Store conversations locally.

```
solution/data/chat_history/
```

Each conversation should include

* Conversation ID
* Timestamp
* User Question
* Retrieved Documents
* Response
* Sources

---

# Analytics

Generate analytics including

* Sentiment Distribution
* Topic Clusters
* Pain Point Frequency
* Recommendation Issues
* Discovery Challenges
* Feature Requests
* Listening Behaviors
* User Personas
* Trending Complaints
* Emerging Needs

Store analytics locally in

```
solution/data/analytics/
```

---

# Dashboard

Provide an analytics dashboard containing

* Total Reviews
* Reviews by Source
* Sentiment Distribution
* Topic Distribution
* Discovery Challenges
* Recommendation Complaints
* Timeline Trends
* Word Cloud
* Feature Requests
* Listening Behaviors

Charts should include

* Line Charts
* Pie Charts
* Bar Charts
* Heatmaps

---

# Filters

Support filtering by

* Platform
* Rating
* Date
* Language
* Country
* Sentiment
* Topic
* Discovery Issues
* Recommendation Issues

---

# Search

Support

* Semantic Search
* Keyword Search
* Hybrid Search

---

# User Interface

The UI should be inspired by Spotify.

Design principles

* Dark Theme
* Spotify Green Accent (#1DB954)
* Black Background
* Rounded Components
* Smooth Animations
* Glassmorphism
* Modern Typography
* Responsive Layout

---

# Layout

### Left Sidebar

* Spotify-style Logo
* New Chat
* Chat History
* Dashboard
* Data Sources
* Settings

---

### Main Chat Area

* Chat Messages
* Suggested Questions
* Source References
* Evidence Panel
* Input Box
* Typing Animation

---

### Top-Right Header Action

A **"Retrieve Latest Reviews"** button must be displayed in the upper-right corner of the main chat area.

Behavior

* When clicked, the system triggers a fresh data fetch from all configured sources (App Store, Play Store, Reddit, Community, Social Media).
* Newly fetched reviews are cleaned, processed, embedded, and stored locally, replacing or appending to the existing data in `solution/data/`.
* The vector store is updated with the newly ingested documents.
* A progress indicator or status message is shown during the retrieval process.
* Once complete, the chatbot answers questions using the freshly fetched data.

Default Behavior (without clicking the button)

* The chatbot answers all questions using the previously fetched and indexed data already stored locally.
* No automatic re-fetching occurs unless the user explicitly clicks "Retrieve Latest Reviews".

This allows product teams to control when new data is pulled, avoiding unnecessary API calls or rate limit issues during normal usage.

---

# Response Format

Every chatbot response should contain

## Summary

Short answer to the question.

---

## Key Insights

Bullet-point findings extracted from reviews.

---

## Supporting Evidence

Representative customer quotes or summarized review snippets.

---

## Sources

List the platforms used.

Example

* App Store
* Play Store
* Reddit
* Community
* Social Media

---

## Confidence

High

Medium

Low

based on retrieval quality.

---

## Suggested Follow-up Questions

Suggest related questions automatically.

---

# Suggested Questions Panel

Display clickable questions such as

* Why do users struggle discovering new music?
* Why do users replay the same playlists?
* What complaints exist about recommendations?
* What feature requests appear most often?
* Compare Reddit and Play Store complaints.
* What do Premium users complain about?
* Which user segments struggle most?
* What unmet needs appear repeatedly?
* What changed during the last year?
* Why do users skip recommendations?

---

# Default Chatbot Responses

## No Relevant Reviews

"I couldn't find enough relevant customer feedback to answer this question confidently. Please try rephrasing your question or ask about Spotify recommendations, music discovery, playlists, listening behavior, customer sentiment, or feature requests."

---

## Question Outside Scope

"I'm designed to analyze Spotify customer feedback collected from reviews, Reddit, community forums, and social discussions. Please ask questions related to Spotify users, recommendations, playlists, listening behavior, music discovery, or customer sentiment."

---

## Insufficient Evidence

"I found only a small number of relevant customer discussions. The following answer is based on limited evidence and may not fully represent the overall customer opinion."

---

## Empty Knowledge Base

"No customer feedback has been indexed yet. Please ingest App Store, Play Store, Reddit, Community, or Social Media data before asking questions."

---

## Data Source Missing

"The requested data source has not been indexed yet. Please import the data before querying this source."

---

## Ambiguous Question

"Could you make your question more specific?

Examples:

* Why do users replay the same songs?
* Why do users dislike Discover Weekly?
* What complaints do Premium users have?
* What feature requests appear most frequently?"

---

## No Previous Context

"I don't have an active conversation to reference. Please ask your original question again."

---

## No Matching Date Range

"I couldn't find customer feedback for the selected time period."

---

## Unsupported Filter

"That filter isn't currently supported. Available filters include Platform, Rating, Date, Sentiment, Language, Country, and Topic."

---

## Low Retrieval Confidence

"I found only weakly related customer feedback and cannot provide a reliable answer. Please ask a more specific question."

---

## Retrieve Latest Reviews — In Progress

"Fetching the latest reviews from all configured sources. This may take a few minutes. Please wait..."

---

## Retrieve Latest Reviews — Complete

"Latest reviews have been successfully fetched and indexed. You can now ask questions based on the most recent customer feedback."

---

## Retrieve Latest Reviews — Failed

"An error occurred while fetching the latest reviews. Please check your internet connection or API configurations and try again."

---

# Backend

Use

* Python
* FastAPI
* LangChain
* Groq SDK
* ChromaDB
* Sentence Transformers
* Pydantic

---

# Frontend

Use

* Next.js
* TypeScript
* Tailwind CSS
* Shadcn UI
* React Query
* Framer Motion
* Recharts
* Lucide Icons

---

# Configuration

Use a configuration file for all settings.

Include

* Groq API Key
* LLM Model
* Embedding Model
* Temperature
* Maximum Tokens
* Chunk Size
* Chunk Overlap
* Top-K Retrieval
* Theme
* Data Sources

No configuration should be hardcoded.

---

# Logging

Log

* Errors
* API Calls
* Retrieval Results
* Response Time
* LLM Latency
* User Activity

Store logs locally.

---

# Performance Goals

* Semantic Search under 1 second
* Chat Response under 5 seconds
* Dashboard Loading under 2 seconds

---

# Future Extensibility

Design the application with modular architecture so that new data sources, embedding models, LLMs, analytics modules, and UI features can be added without major refactoring.

---

# Deliverables

The completed solution should include:

* A Spotify-inspired responsive chatbot interface.
* Modular data ingestion pipeline for all supported sources.
* Local persistent storage without any external database.
* Persistent Chroma vector store.
* RAG pipeline using Groq LLM.
* Analytics dashboard with visualizations.
* Conversation history stored locally.
* Source-backed, explainable chatbot responses.
* Intelligent fallback responses for unsupported or low-confidence queries.
* Clean, modular, well-documented codebase with clear folder structure and configuration files.
* "Retrieve Latest Reviews" button in the chatbot header that triggers on-demand data refresh across all sources, with progress feedback and seamless transition to answering from the updated knowledge base.

The final application should behave like an internal **AI Product Research Assistant** that helps Spotify teams understand customer feedback, identify music discovery challenges, analyze recommendation quality, and make evidence-based product decisions using only retrieved customer insights.
