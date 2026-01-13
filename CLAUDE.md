# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Company Culture & Position Analysis Tool** (公司文化及职位解析工具) - an AI-powered career decision support tool for job seekers in China. It analyzes company culture from employee reviews and provides position matching analysis with interview preparation suggestions.

### Core Workflow

1. **MHTML File Reading** → Read employee reviews from MHTML files (browser-saved webpages)
2. **AI Analysis** → Analyze company culture and position matching using Zhipu AI GLM-4.7
3. **Report Generation** → Generate professional HTML reports with analysis results

**Note**: Web scraping functionality has been removed. The tool now only reads MHTML files saved by users.

## Essential Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (required for AI analysis)
set ZHIPU_API_KEY=your-api-key

# Run the application
python main.py
```

### Testing MHTML Reader

```bash
# Test MHTML parsing functionality
python test_mhtml_read.py
```

### Building Executable

```bash
# Build Windows EXE using PyInstaller
build_exe.bat

# Output: dist/公司文化职位解析工具.exe (~210 MB)
```

**Important**: Always test the application with `python main.py` before rebuilding the EXE. User rule: "修改完成之后先自测，通过之后再生成exe"

## Architecture

### Core Modules

**main.py** - Tkinter GUI application
- Orchestrates all modules
- Manages configuration persistence (`config.json`)
- Runs analysis in background threads to avoid UI blocking
- Window geometry: 900x770 (optimized after removing title)
- Data source frame padding: 5px (reduced for compact UI)

**mhtml_reader.py** - MHTML file parsing
- **Critical**: Supports quoted-printable encoding (Chrome-saved MHTML files)
- Uses `quopri.decodestring` to decode quoted-printable content
- Handles multiple encodings (UTF-8, GBK)
- Extracts title, URL, and text content from MHTML
- Returns dict with 'url', 'title', 'content', 'error' fields

**ai_analyzer.py** - AI analysis engine
- Uses Anthropic-compatible SDK with Zhipu AI endpoint
- **Model: GLM-4.7** (upgraded from GLM-4.6)
- Reads `ZHIPU_API_KEY` from environment variable (security best practice)
- Logs all AI calls to `logs/ai_calls_YYYYMMDD.log` with full metadata
- Two analysis methods:
  - `analyze_company_culture()` - Analyzes employee reviews
  - `analyze_position_match()` - Evaluates fit between resume and JD

**resume_parser.py** - Resume file parsing
- Supports PDF (PyPDF2), Word (python-docx), TXT
- Auto-detects encoding for text files

**report_generator.py** - HTML report generation
- Converts Markdown AI responses to HTML
- Custom Markdown parser using regex (handles # ## ### - 1. lists)
- Generates responsive HTML with gradient CSS styling
- Enhanced visual hierarchy with progressive heading sizes

### Data Flow

```
User Input (GUI)
  ↓
MHTMLReader → MHTML Files → Extracted Reviews
  ↓
AIAnalyzer → Company Culture Analysis
  ↓
ResumeParser → Extract Resume Content
  ↓
AIAnalyzer → Position Match Analysis (Culture + Resume + JD)
  ↓
ReportGenerator → HTML Report
  ↓
Auto-open in browser
```

### Configuration

- **Environment Variables**: `ZHIPU_API_KEY` (required)
- **Config File**: `config.json` (auto-generated, stores user inputs)
  - Fields: 'mhtml_folder', 'resume_path', 'job_description', 'output_path'
- **Prompts**: `prompts/` directory contains Markdown templates for AI analysis

### Critical Implementation Details

**AI Model**: Upgraded to GLM-4.7 (from GLM-4.6). More powerful for complex analysis.

**API Integration**: Uses Anthropic-compatible endpoint (`https://open.bigmodel.cn/api/anthropic`) for Zhipu AI, not native Zhipu SDK.

**MHTML Quoted-Printable Decoding**: This is CRITICAL for Chrome-saved MHTML files. Without this decoding, important content like "最低工资" (minimum wage) complaints would be missed. Implementation in `mhtml_reader.py` lines 103-136:
```python
is_quopri = 'Content-Transfer-Encoding: quoted-printable' in mhtml_content
if is_quopri and html_content:
    decoded_bytes = decode_quopri(html_content.encode('utf-8'))
    html_content = decoded_bytes.decode('utf-8')
```

**Logging Strategy**: AI analyzer logs complete call metadata (input, output, tokens, duration) to daily log files for debugging and auditing.

**Markdown Parsing**: Custom regex-based parser in `report_generator.py` because AI outputs Markdown. Handles nested lists, headings, and bold text.

**Content Length Management**: AI module auto-truncates inputs to avoid token limits:
- Company culture: max 15,000 chars
- Position match sections: max 8,000 chars each
- Resume: truncated to 2,500 chars (line 275)

**Prompt Engineering**: Prompts use time-weighted analysis principles:
- Recent comments (2025-2026) have higher priority than older ones
- Six-level weight system combining frequency + recency
- Trend analysis to detect improving/worsening conditions
- Every conclusion must cite actual employee comments with mention frequency

**Interview Answers with Bilingual Support**: If JD is in English, the tool provides Chinese and English versions of interview answers. Each answer:
- Must be based on candidate's resume and JD requirements
- Uses STAR法则 for behavioral questions
- Cites specific experiences from resume or requirements from JD
- Provides practical, ready-to-use responses

### Build Configuration (PyInstaller)

Build command from `build_exe.bat`:
```bash
pyinstaller --noconfirm --onefile --windowed --name "公司文化职位解析工具" --icon=NONE --add-data "prompts;prompts" --hidden-import=selenium --hidden-import=anthropic --hidden-import=PyPDF2 --hidden-import=docx --exclude-module=PyQt5 --exclude-module=PySide6 --exclude-module=matplotlib --exclude-module=IPython --exclude-module=pygame --collect-all selenium main.py
```

Key exclusions to avoid Qt binding conflicts:
```
--exclude-module=PyQt5
--exclude-module=PySide6
--exclude-module=matplotlib
--exclude-module=IPython
--exclude-module=pygame
```

Uses `--collect-all selenium` to ensure all Selenium dependencies are included.

## Known Issues & Solutions

**MHTML Content Missing**: If Chrome-saved MHTML files show missing content like "最低工资" complaints → Ensure quoted-printable decoding is enabled in `mhtml_reader.py` (lines 103-136)

**GLM-4.7 Stability**: GLM-4.7 is more powerful than GLM-4.6 but ensure prompts are optimized (42 lines for job matching to avoid non-JSON responses)

**Build File Lock**: If EXE rebuild fails with "Permission denied" → Close all running instances of the application, then rebuild

**GUI Frame Height**: If data source frame appears too tall → Reduce padding in `main.py` line 125 (currently 5px) and pady in line 126 (currently 3px)

## Recent Changes (v2.0+)

### Removed Features
- **Web scraping**: Completely removed `web_scraper.py` import and URL input functionality
- **Title label**: Removed from GUI to save space

### Added Features
- **MHTML file reading**: Replaced web scraping with local MHTML file reading
- **Time-weighted analysis**: Prompts now prioritize recent comments over older ones
- **Interview answer generation**: AI provides reference answers based on resume + JD
- **Bilingual support**: If JD is English, provides both Chinese and English interview answers
- **Compact UI**: Reduced frame padding and window height for better space utilization

### Prompt Enhancements
- **Company Culture Analysis**: Now includes detailed analysis of:
  - Outsourcing nature (外包性质)
  - Minimum wage issues (最低工资)
  - Layoff history (裁员情况)
  - Overtime patterns (加班情况)
  - Benefits (五险一金、培训、休假)

- **Position Match Analysis**: Now provides:
  - Reference answers for 5-8 interview questions
  - STAR法则 behavioral responses
  - Bilingual answers if JD is English
  - Specific citations from resume and JD

## Development Workflow

1. **Make code changes** to source files
2. **Test with Python**: `python main.py` and verify functionality
3. **Check prompts** in `prompts/` directory if AI behavior needs adjustment
4. **Rebuild EXE**: `build_exe.bat` only after testing passes
5. **Verify EXE**: Test the built EXE to ensure it works correctly

## Testing Strategy

Before rebuilding EXE, always:
1. Test MHTML file reading with various MHTML files
2. Test AI analysis with valid API key
3. Test report generation and HTML output
4. Verify GUI displays correctly with new changes
5. Check that all previous functionality still works
