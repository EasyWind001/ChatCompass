# ChatCompass - AI Conversation Knowledge Base Management System

<div align="center">

**One-stop management for your AI conversations, never lose your knowledge again**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65%20Passed-brightgreen.svg)](tests/)
[![Version](https://img.shields.io/badge/Version-v1.2.6-orange.svg)](CHANGELOG.md)

[简体中文](README.md) | [Features](#-features) | [Quick Start](#-quick-start) | [Documentation](#-documentation-index) | [Changelog](CHANGELOG.md)

</div>

## 📖 Introduction

ChatCompass is a local knowledge base system designed for managing AI conversations. It can:

- 🔗 **One-Click Import**: Support share links from ChatGPT, Claude and other mainstream AI platforms
- 🤖 **Smart Analysis**: Auto-generate summaries, categories and tags (Ollama local AI)
- 🔍 **Powerful Search**: Full-text search + context positioning, quickly find what you need
- 📊 **Flexible Storage**: Support SQLite and Elasticsearch for different scale needs
- 🐳 **Docker Deployment**: One-click startup for Elasticsearch and Ollama services

## ✨ Features

### 🎯 Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Multi-Platform** | ChatGPT, Claude, etc. | ✅ Completed |
| **Smart Scraping** | Auto-extract conversation content | ✅ Completed |
| **Full-Text Search** | SQLite FTS5 + Elasticsearch | ✅ Completed |
| **Context Positioning** | Show context in search results | ✅ v1.2 |
| **Conversation Details** | View complete conversation | ✅ v1.1 |
| **Conversation Delete** | Delete single or batch conversations | ✅ v1.2.6 New |
| **AI Analysis** | Ollama local AI (Qwen2.5:3b) | ✅ v1.2.2 |
| **Flexible Storage** | SQLite / Elasticsearch | ✅ v1.2.2 |
| **Docker Deployment** | One-click startup all services | ✅ v1.2.2 |
| **CLI Interface** | Interactive command line | ✅ Completed |
| **GUI Interface** | Desktop application | 🚧 In Development |

### 🆕 Latest Features

#### v1.2.6 (2026-01-17)
- **🗑️ Delete Feature**: Complete conversation deletion capability
  - Delete by ID or URL
  - Interactive confirmation (prevent accidental deletion)
  - Cascade deletion (tags, messages)
  - Dual mode support (command line + interactive)

#### v1.2.4 (2026-01-15)
- **📝 Large Text Optimization**: Intelligent handling of very long conversations
  - Segment summary merging
  - Smart truncation optimization
  - Timeout protection mechanism

#### v1.2.2 (2026-01-14)
- **🔍 Elasticsearch Integration**: Large-scale storage and search
- **🤖 Ollama AI Integration**: Local AI analysis
- **🐳 Docker Support**: One-click deployment complete environment
- **🏗️ Unified Storage Architecture**: Transparent switching between SQLite/ES

### 🔍 Search Enhancement Features (v1.2)

- **Context Display**: Search results show 80 characters before and after matches
- **Precise Positioning**: Mark match position (which message number)
- **Keyword Highlighting**: Wrap keywords with 【】
- **Role Distinction**: Distinguish user👤 and assistant🤖 messages
- **Multiple Matches**: Support displaying multiple matches in one conversation

**Search Effect Example:**
```
🔍 Search: Python

  [1] 📄 Python Data Analysis Tutorial
      💬 Platform: chatgpt | 📁 Category: Programming
      📍 Found 2 matches:

         🤖 Assistant (Message 2/5)
         ...learn【Python】data analysis, start with Pandas and NumPy...

         🤖 Assistant (Message 4/5)
         ...【Python】is very popular in data science because...

      💡 Enter 'show 1' to view complete conversation
```

### 📦 Supported Platforms

| Platform | Status | Description |
|----------|--------|-------------|
| ChatGPT | ✅ | Support share links |
| Claude | ✅ | Support share links |
| Gemini | 🚧 | Planned |
| DeepSeek | 🚧 | Planned |

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Windows / macOS / Linux

### Installation Steps

#### 1. Clone Project

```bash
git clone https://github.com/yourusername/ChatCompass.git
cd ChatCompass
```

#### 2. Install Dependencies

```bash
# Use one-click install script (Recommended)
# Windows
install.bat

# Linux/macOS
bash install.sh

# Or install manually
pip install -r requirements.txt
playwright install chromium
```

#### 3. Configuration (Optional)

**Basic Configuration** - Use SQLite and local AI:
```bash
# Copy config file
cp .env.example .env

# Default config is ready, no need to modify
# - STORAGE_TYPE=sqlite (default)
# - AI_MODE=local (default)
```

**Advanced Configuration** - Use Elasticsearch and Ollama:
```bash
# Edit .env
STORAGE_TYPE=elasticsearch          # Use Elasticsearch storage
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

AI_MODE=local                       # Use Ollama local AI
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

**Docker Quick Start** (Recommended for beginners):

**One-Click Startup**:
```bash
# Windows users
.\docker-start.bat

# Linux/Mac users
chmod +x docker-start.sh
./docker-start.sh
```

**Manual Startup**:
```bash
# 1. Start all services (background)
docker-compose up -d

# 2. Check service status
docker-compose ps
# Expect to see 3 services all in Up status

# 3. View logs (Important! First startup needs to download model)
docker-compose logs -f chatcompass
# See "ChatCompass startup complete!" means success

# 4. Use application
docker exec -it chatcompass-app python main.py
```

**First Startup Notes**:
- ⏬ Download images and models (about 5GB, first time needs 10-20 minutes)
- ✅ Elasticsearch will auto-initialize indexes
- ✅ Ollama will auto-download Qwen2.5:3b model

📖 **Detailed Instructions**: [Docker Quick Start](docs/DOCKER_QUICKSTART.md) | [Complete Docker Guide](docs/DOCKER_GUIDE.md)

### Basic Usage

#### Method 1: Docker Environment (Recommended)

```bash
# 1. Start services
docker-compose up -d

# 2. Enter container to use
docker exec -it chatcompass-app python main.py

# Or run commands directly
docker exec -it chatcompass-app python main.py add "https://chatgpt.com/share/xxxxx"
docker exec -it chatcompass-app python main.py search "Python"
docker exec -it chatcompass-app python main.py stats
```

#### Method 2: Local Command Line

**SQLite Mode** (Default):
```bash
# Interactive mode
python main.py

# Add conversation directly
python main.py add "https://chatgpt.com/share/xxxxx"

# Search conversations
python main.py search "Python tutorial"

# View conversation details
python main.py show 1

# Delete conversation (v1.2.6 new, needs confirmation)
python main.py delete 1

# View statistics
python main.py stats
```

**Elasticsearch Mode** (Need to start ES first):
```bash
# 1. Start Elasticsearch
docker-compose up -d elasticsearch

# 2. Set environment variables
export STORAGE_TYPE=elasticsearch
export ELASTICSEARCH_HOST=localhost

# 3. Use
python main.py
```

#### Interactive Mode Example

```
$ python main.py

====================================================================
ChatCompass - AI Conversation Knowledge Base Management System v1.2.6
====================================================================

[INFO] Initialize storage backend: sqlite
[OK] Storage initialization successful: SQLiteManager
[INFO] Initialize AI service...
[OK] AI service ready
    - Backend: ollama
    - Model: qwen2.5:3b

====================================================================

ChatCompass> help         # View help
ChatCompass> list         # List all conversations
ChatCompass> search Python  # Search
ChatCompass> show 1       # View details
ChatCompass> delete 1     # Delete conversation
ChatCompass> exit         # Exit
```

### Usage Examples

```bash
# 1. Add ChatGPT conversation
python main.py add "https://chatgpt.com/share/6964e4ba-8264-8010-99ad-ab2399bb1dca"

# 2. Search related conversations
python main.py search "programming"

# 3. View detailed content
python main.py show 1

# 4. View statistics
python main.py stats
```

## 📁 Project Structure

```
ChatCompass/
├── README.md                 # Project documentation
├── README_EN.md              # English documentation
├── CHANGELOG.md              # Version changelog
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker compose config
├── .env.example              # Config file example
├── .gitignore                # Git ignore rules
├── main.py                   # 🎯 Main program entry
├── config.py                 # ⚙️ Configuration management
├── setup.py                  # 📦 Installation script
│
├── install.bat               # Windows one-click install
├── install.sh                # Linux/macOS one-click install
├── run.bat                   # Windows quick start
├── run.sh                    # Linux/macOS quick start
├── run_tests.bat             # Windows test script
├── run_tests.py              # Test runner
│
├── ai/                       # 🤖 AI analysis module
│   ├── __init__.py
│   ├── ollama_client.py      # Ollama client
│   ├── ai_service.py         # AI service manager (v1.2.2 new)
│   └── openai_client.py      # OpenAI/DeepSeek client
│
├── database/                 # 💾 Database module
│   ├── __init__.py
│   ├── db_manager.py         # SQLite manager (original)
│   ├── sqlite_manager.py     # SQLite storage (v1.2.2 new)
│   ├── es_manager.py         # Elasticsearch manager (v1.2.2 new)
│   ├── storage_adapter.py    # Storage adapter (v1.2.2 new)
│   ├── base_storage.py       # Storage base class and factory (v1.2.2 new)
│   ├── migrate_to_es.py      # Data migration tool (v1.2.2 new)
│   ├── health_check.py       # Health check tool (v1.2.2 new)
│   └── schema.sql            # Database schema
│
├── scrapers/                 # 🕷️ Scraper module
│   ├── __init__.py
│   ├── base_scraper.py       # Scraper base class
│   ├── chatgpt_scraper.py    # ChatGPT scraper
│   ├── claude_scraper.py     # Claude scraper
│   └── scraper_factory.py    # Scraper factory
│
├── tests/                    # 🧪 Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration
│   ├── README.md             # Test documentation
│   ├── unit/                 # Unit tests
│   │   └── (test files)
│   └── integration/          # Integration tests
│       └── (test files)
│
├── docs/                     # 📚 Documentation directory
│   ├── V1.2.2_PLAN.md        # v1.2.2 development plan
│   ├── DOCKER_GUIDE.md       # Docker usage guide
│   ├── DOCKER_QUICKSTART.md  # Docker quick start
│   ├── PROJECT_SUMMARY.md    # Project summary
│   └── archive/              # Development process document archive
│
└── data/                     # Data directory
    └── chatcompass.db        # SQLite database file
```

### Directory Description

#### Core Modules

- **`database/`** - Database management module
  - Use SQLite3 to store conversation data
  - Implement FTS5 full-text search
  - Provide complete CRUD operations
  - Support tag management and statistics

- **`scrapers/`** - Web scraper module
  - Based on Playwright automation scraping
  - Support multi-platform adaptation
  - Implement multi-layer fallback mechanism
  - Auto-handle page structure changes

- **`ai/`** - AI analysis module (optional)
  - Support local models (Ollama)
  - Support online API (OpenAI/DeepSeek)
  - Auto-generate summaries and tags
  - Intelligent conversation content classification

#### Tests

- **66 test cases**, covering core functions
- **98.5% pass rate**, ensuring code quality
- **87% code coverage**, continuous improvement

Run tests:
```bash
# Recommended: unified test script
python run_all_tests.py

# Windows
run_tests.bat

# Linux/macOS
python run_tests.py

# Or use pytest
pytest tests/ -v
```

#### Documentation

- **`docs/`** - Detailed technical documentation and index
  - [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Complete documentation index ⭐Recommended
  - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference guide
  - [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing guide
  - [DOCKER_BUILD_GUIDE.md](DOCKER_BUILD_GUIDE.md) - Docker guide
  - Feature descriptions and implementation details
  - Development process archive

View all documentation: [Documentation Index](DOCUMENTATION_INDEX.md)

## 🔧 Configuration

### AI Feature Configuration (Optional)

ChatCompass core features (add, search, view) **do not require AI configuration** to work.

AI features are only used for:
- Auto-generate conversation summaries
- Auto-classify conversations
- Auto-extract tags

#### Local Mode (Recommended, Free)

```env
# .env file
AI_MODE=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

**Install Ollama:**
1. Visit https://ollama.ai to download and install
2. Run `ollama pull qwen2.5:7b`
3. Start service `ollama serve`

#### Online Mode

```env
AI_MODE=online

# Use DeepSeek (Recommended, cost-effective)
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_MODEL=deepseek-chat

# Or use OpenAI
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
```

#### Disable AI (Default)

```env
# Leave empty or don't configure, program will skip AI analysis
AI_MODE=
```

## 🎯 Usage Tips

### Search Tips

```bash
# Single keyword
python main.py search "Python"

# Multiple keywords (space separated)
python main.py search "Python data analysis"

# Exact phrase (use quotes)
python main.py search "machine learning introduction"
```

### View Conversations

```bash
# View by ID
python main.py show 1

# View by URL
python main.py show "https://chatgpt.com/share/xxxxx"

# View in interactive mode
ChatCompass> show 1
```

### Batch Management

```bash
# List all conversations
ChatCompass> list

# View statistics
ChatCompass> stats

# Filter by category
ChatCompass> list --category programming
```

## 🧪 Testing

The project includes a complete test suite to ensure code quality.

### Run Tests

```bash
# Recommended: unified test script
python run_all_tests.py

# Windows
run_tests.bat

# Linux/macOS  
python run_tests.py

# Or use pytest
pytest tests/ -v

# Generate coverage report
pytest tests/ --cov=. --cov-report=html
```

### Test Coverage

- ✅ Database operation tests (14)
- ✅ Scraper function tests (15)
- ✅ AI client tests (19)
- ✅ Delete function tests (13) ⭐New
- ✅ Complete process tests (5)

**Total: 66 tests, 98.5% pass rate, 87% code coverage**

See: [tests/README.md](tests/README.md) | [Testing Guide](TESTING_GUIDE.md) | [Test Summary](TESTING_SUMMARY_v1.2.6.md)

## 📊 Database Design

### Core Table Structure

```sql
-- Conversations table
conversations (
    id INTEGER PRIMARY KEY,
    source_url TEXT UNIQUE,      -- Original link
    platform TEXT,                -- Platform (chatgpt/claude)
    title TEXT,                   -- Conversation title
    raw_content TEXT,             -- Complete conversation (JSON)
    summary TEXT,                 -- AI summary
    category TEXT,                -- Category
    word_count INTEGER,           -- Word count
    message_count INTEGER,        -- Message count
    created_at DATETIME,          -- Created time
    updated_at DATETIME,          -- Updated time
    is_favorite INTEGER,          -- Is favorite
    notes TEXT                    -- User notes
)

-- Tags table
tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,             -- Tag name
    color TEXT,                   -- Color
    usage_count INTEGER           -- Usage count
)

-- Association table
conversation_tags (
    conversation_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (conversation_id, tag_id)
)

-- FTS5 full-text search table
conversations_fts (
    title, summary, raw_content
)
```

See: [database/schema.sql](database/schema.sql)

## 📝 Changelog

### v1.2.6 (2026-01-17) - Delete Feature

- ✨ New: Delete command to delete conversations
- ✨ New: Interactive confirmation mechanism
- ✨ New: Cascade deletion (tags, messages)
- 🧪 Tests: 13 unit tests + 3 E2E tests
- 📚 Documentation: Complete documentation index and archive

### v1.2.4 (2026-01-15) - Large Text Optimization

- ✨ New: Segment summary merging strategy
- ⚡ Optimization: Smart truncation improves speed
- 🛡️ New: Timeout protection and fallback solution
- 📊 New: Real-time progress display

### v1.2.2 (2026-01-14) - Enterprise Upgrade

- 🔍 Elasticsearch integration
- 🤖 Ollama AI integration  
- 🐳 Complete Docker support
- 🏗️ Unified storage architecture

### v1.2 (2026-01-13) - Search Enhancement

- ✨ New: Search results show context positioning
- ✨ New: Precise annotation of match positions
- ✨ New: Keyword highlighting
- ✨ New: Support multiple match display
- 🎨 Optimization: Search result display format

### v1.1 (2026-01-12) - Show Feature

- ✨ New: show command to view conversation details
- 🐛 Fix: ChatGPT scraper page structure adaptation
- 🎨 Optimization: Interactive mode experience
- 🔧 Improvement: Windows console encoding handling

### v1.0 (2026-01-12) - Initial Version

- ✅ Basic features completed
- ✅ 52 tests passed
- ✅ ChatGPT and Claude platform support

Complete changelog: [CHANGELOG.md](CHANGELOG.md)

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Database**: 
  - SQLite3 + FTS5 (full-text search)
  - Elasticsearch 7.17+ (optional)
- **Scraper**: Playwright + BeautifulSoup4
- **AI**: 
  - Ollama (local, recommended)
  - OpenAI API (online)
- **Testing**: Pytest + pytest-cov
- **Container**: Docker + Docker Compose
- **GUI**: PyQt6 (planned)

## 📚 Documentation Index

ChatCompass provides a complete documentation system to help you get started quickly and understand deeply.

### Quick Navigation

| Scenario | Recommended Documentation |
|----------|---------------------------|
| 🚀 **Quick Start** | [README_EN.md](README_EN.md) → [QUICK_DEPLOY.md](QUICK_DEPLOY.md) |
| 📖 **Command Reference** | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| 🐳 **Docker Deployment** | [DOCKER_BUILD_GUIDE.md](DOCKER_BUILD_GUIDE.md) → [docs/DOCKER_QUICKSTART.md](docs/DOCKER_QUICKSTART.md) |
| 🧪 **Run Tests** | [TESTING_GUIDE.md](TESTING_GUIDE.md) → [tests/README.md](tests/README.md) |
| 🤝 **Contributing** | [CONTRIBUTING.md](CONTRIBUTING.md) → [docs/BRANCH_MANAGEMENT.md](docs/BRANCH_MANAGEMENT.md) |
| 📝 **Version History** | [CHANGELOG.md](CHANGELOG.md) |
| 🔍 **Find Documentation** | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) ⭐Complete index |

### Core Documentation

- **README.md** / **README_EN.md** - Project introduction and quick start
- **CHANGELOG.md** - Complete version changelog
- **QUICK_REFERENCE.md** - Command quick reference
- **CONTRIBUTING.md** - Contributing guide
- **TESTING_GUIDE.md** - Testing guide
- **DOCKER_BUILD_GUIDE.md** - Docker build guide

### Technical Documentation

- **docs/SEARCH_CONTEXT_FEATURE.md** - Search context feature
- **docs/LARGE_TEXT_HANDLING.md** - Large text handling solution
- **docs/SEGMENT_SUMMARY_STRATEGY.md** - Segment summary strategy
- **docs/FALLBACK_STRATEGY.md** - AI fallback solution
- **docs/PERFORMANCE_TIPS.md** - Performance optimization suggestions
- **docs/PROJECT_SUMMARY.md** - Project architecture summary

### Version Documentation

- **RELEASE_READY_v1.2.6.md** - v1.2.6 release ready report
- **TESTING_SUMMARY_v1.2.6.md** - v1.2.6 test summary
- **docs/V1.2.2_RELEASE_NOTES.md** - v1.2.2 release notes

### Find All Documentation

📖 **Complete documentation index**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

## 🤝 Contributing

We welcome and appreciate all forms of contributions! Before starting, please read our contributing guide:

📖 **Complete Documentation**: [CONTRIBUTING.md](CONTRIBUTING.md)

### Quick Start

1. **Fork and clone repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ChatCompass.git
   cd ChatCompass
   ```

2. **Create feature branch** (follow naming conventions)
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/your-bugfix-name
   ```

3. **Develop and test**
   ```bash
   # Develop feature...
   # Add tests...
   python -m pytest tests/ -v  # Must pass all tests
   ```

4. **Commit code** (follow Commit conventions)
   ```bash
   git commit -m "feat(scope): your feature description"
   ```

5. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

### 📋 Important Specifications

- 🌳 **Branch Management**: [docs/BRANCH_MANAGEMENT.md](docs/BRANCH_MANAGEMENT.md)
- 📝 **Commit Specification**: Conventional Commits format (feat/fix/docs/test, etc.)
- 🧪 **Testing Requirements**: All tests must pass, new features need tests
- 🔒 **Security Rules**: SQL must use parameterized queries, no string concatenation
- 📚 **Documentation Requirements**: New features need to update README and CHANGELOG
- 🌐 **README Sync**: **Before each version push, must synchronously update both README.md and README_EN.md**

### 📖 Development Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Complete contributing guide ⭐Recommended
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing guide
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Documentation index
- [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) - Project architecture
- [.ai-assistant-rules.md](.ai-assistant-rules.md) - AI assistant rules

### 🚫 Prohibited Operations

- ❌ Push directly to main or develop branch
- ❌ Submit untested code
- ❌ Use string concatenation to construct SQL (SQL injection risk)
- ❌ Submit sensitive information like passwords, keys
- ❌ Update only one README without syncing the other (README.md and README_EN.md must be kept in sync)

### Development Environment Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Generate coverage report
pytest tests/ --cov=. --cov-report=html
```

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details

## ⚠️ Disclaimer

This tool is for personal learning and research only. When using this tool to scrape third-party website content, please comply with the relevant website's terms of service and robots.txt rules. Users are solely responsible for the legal liability of using this tool.

## 💬 Support & Feedback

- 📮 Submit Issue: [GitHub Issues](https://github.com/yourusername/ChatCompass/issues)
- 📧 Email: your.email@example.com
- 💬 Discussion: [GitHub Discussions](https://github.com/yourusername/ChatCompass/discussions)

## 🙏 Acknowledgments

Thanks to the following open source projects:

- [Playwright](https://playwright.dev/) - Powerful browser automation tool
- [Ollama](https://ollama.ai/) - Local large model running platform
- [SQLite FTS5](https://www.sqlite.org/fts5.html) - Full-text search engine
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing library

## ⭐ Star History

If this project helps you, please give it a ⭐!

---

<div align="center">

Made with ❤️ by ChatCompass Team

[⬆ Back to Top](#chatcompass---ai-conversation-knowledge-base-management-system)

</div>
