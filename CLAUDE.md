# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Company Culture & Position Analysis Tool** (公司文化及职位解析工具) - an AI-powered career decision support tool for job seekers in China. It analyzes company culture from employee reviews and provides position matching analysis with interview preparation suggestions.

**Two Tools in One Repository:**
1. **单公司分析工具** (main.py) - Analyze one company at a time
2. **批量处理工具** (batch_tool_main.py) - Batch process multiple companies with ranking

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

# Run single-company analysis tool
python main.py

# Run batch processing tool
python batch_tool_main.py

# Run batch tool with startup script
批量工具启动.bat
```

### Testing

```bash
# Test MHTML parsing functionality
python test_mhtml_read.py

# Run batch tool automated tests
cd tests2
python test_test.py

# Quick method validation test
cd tests2
python quick_test.py
```

### Building Executables

```bash
# Build single-company tool EXE
build_exe.bat
# Output: dist/公司文化职位解析工具.exe (~210 MB)

# Build batch processing tool EXE
build_batch_tool_exe.bat
# Output: dist/批量职位解析工具.exe (~50 MB)
```

**Important**: Always test with Python before rebuilding EXE. User rule: "修改完成之后先自测,通过之后再生成exe"

## Architecture

### Core Modules

**Single-Company Tool (main.py)** - Original tool for analyzing one company
- Orchestrates all modules for single company
- Manages configuration persistence (`config.json`)
- Runs analysis in background threads
- Window geometry: 900x770

**batch_tool_main.py** - Batch processing GUI application
- Batch processes multiple companies in one run
- Cache management with smart checking
- Progress tracking and user confirmation dialogs
- Compact UI without title banner
- Generates comprehensive ranking report

**batch_processor.py** - Batch processing core logic
- Orchestrates batch analysis workflow
- Implements cache checking logic
- Progress callback system
- Calls single-company analysis for each company
- Generates ranking reports using AI

**ai_client.py** - AI client (Anthropic compatible)
- Connects to Zhipu AI GLM-4.7 via Anthropic-compatible API
- Reads API key from environment variable `ZHIPU_API_KEY`
- Logs all AI calls to `logs2/` with full metadata

**ranking_report_generator.py** - Ranking report generator
- Creates comprehensive ranking HTML reports
- Line-by-line Markdown to HTML conversion (not regex-based)
- **Table hyperlink injection** (`_add_links_to_table()` method, lines 359-484):
  - Adds clickable company names linking to individual reports
  - Adds "JD链接" column with links to jd.txt files
  - Intelligent company name matching (exact, simplified, partial)
  - Proper HTML table cell wrapping with `<td>` tags
- Handles both 2-tuple `(company, report)` and 3-tuple `(company, report, jd)` data structures

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

**Single-Company Tool (main.py):**
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

**Batch Processing Tool (batch_tool_main.py):**
```
User Input (Multiple Companies in Directory)
  ↓
For Each Company:
  MHTMLReader → MHTML Files → Extracted Reviews
  ↓
  AIAnalyzer → Company Culture Analysis
  ↓
  AIAnalyzer → Position Match Analysis (Culture + Resume + JD)
  ↓
  ReportGenerator → Company Report (includes JD content)
  ↓
AIClient → Read All Company Reports → Generate Ranking
  ↓
RankingReportGenerator → Comprehensive Ranking Report
  ↓
Display: Individual Reports + Ranking Report with Links
```

### Configuration

- **Environment Variables**: `ZHIPU_API_KEY` (required)
- **Single-Company Config**: `config.json` (auto-generated, stores user inputs)
  - Fields: 'mhtml_folder', 'resume_path', 'job_description', 'output_path'
- **Batch Tool Config**: `batch_config.json` (auto-generated)
  - Fields: 'companies_dir', 'resume_path', 'output_dir'
- **Prompts**:
  - `prompts/` - Single-company tool prompts
  - `prompts2/` - Batch tool prompts (综合评估与排名.txt)
- **Logs**:
  - `logs/` - Single-company tool AI call logs
  - `logs2/` - Batch tool AI call logs

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

### Batch Processing Tool (New in v1.2)
- **Batch Analysis**: Process multiple companies in one run
- **Smart Caching**: Skip already-generated reports, with user confirmation
- **Ranking Report**: AI-generated comprehensive ranking with scores, pros/cons, recommendations
- **JD Display**: Shows full job description in each company report
- **Compact GUI**: No title banner, clean layout with explanations below inputs

### Removed Features
- **Web scraping**: Completely removed `web_scraper.py` import and URL input functionality (v1.6+)
- **Title label**: Removed from single-company GUI to save space
- **Redundant bottom links**: Ranking report no longer shows company report links at bottom (v2.1)

### Added Features
- **MHTML file reading**: Replaced web scraping with local MHTML file reading (v1.6)
- **Time-weighted analysis**: Prompts now prioritize recent comments over older ones
- **Interview answer generation**: AI provides reference answers based on resume + JD
- **Bilingual support**: If JD is English, provides both Chinese and English interview answers
- **Compact UI**: Reduced frame padding and window height for better space utilization
- **Batch processing**: Process multiple companies with ranking report (v1.2)
- **Table hyperlinks**: Ranking report table includes clickable company names and JD links (v2.1)
- **Deep stability analysis**: AI detects outsourcing, hidden layoff tactics, salary traps (v2.1)

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
