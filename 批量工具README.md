# 批量公司文化职位解析工具

## 功能说明

这是一个批量处理工具,可以同时分析多家公司的企业文化和职位匹配度,并生成综合推荐排名报告。

### 核心功能

1. **批量处理** - 一次性处理多个公司的职位分析
2. **智能排名** - AI自动生成公司推荐排名
3. **进度跟踪** - 实时显示处理进度
4. **详细报告** - 为每个公司生成详细分析报告
5. **综合评估** - 生成包含排名、优劣势、推荐理由的综合报告

## 目录结构

```
position/
├── batch_tool_main.py          # 批量工具主程序
├── batch_processor.py          # 批量处理核心逻辑
├── ai_client.py                # AI客户端(Anthropic兼容接口)
├── ranking_report_generator.py # 排名报告生成器
├── prompts2/                   # 提示词目录
│   └── 综合评估与排名.txt
├── logs2/                      # 日志目录(自动创建)
├── tests2/                     # 测试目录
│   ├── test_batch_tool.py     # 测试程序
│   ├── 测试问题记录.txt
│   └── test_data/             # 测试数据
│       ├── companies/         # 公司测试数据
│       │   ├── 公司A/
│       │   │   ├── jd.txt
│       │   │   └── reviews.html
│       │   └── 公司B/
│       │       ├── jd.txt
│       │       └── reviews.html
│       ├── resume/
│       │   └── test_resume.txt
│       └── output/            # 测试输出
└── 批量工具启动.bat            # 启动脚本
```

## 使用方法

### 1. 准备公司资料

在公司资料根目录下,为每个公司创建一个子目录,目录名为公司名称。每个公司子目录应包含:
- 多个MHTML/HTML文件(保存的员工评价网页)
- `jd.txt` 文件(职位描述)

示例结构:
```
companies/
├── 腾讯/
│   ├── reviews.mhtml
│   ├── reviews2.mhtml
│   └── jd.txt
├── 阿里/
│   ├── reviews.html
│   └── jd.txt
└── 字节/
    ├── reviews.mhtml
    └── jd.txt
```

### 2. 准备简历文件

支持以下格式:
- PDF文件 (.pdf)
- Word文档 (.docx, .doc)
- 文本文件 (.txt)

### 3. 设置API密钥

在运行前,需要设置智谱AI的API密钥:

```bash
set ZHIPU_API_KEY=你的API密钥
```

或者在环境变量中设置 `ZHIPU_API_KEY`。

### 4. 运行程序

**方式1: 使用启动脚本(推荐)**
```bash
批量工具启动.bat
```

**方式2: 直接运行Python**
```bash
python batch_tool_main.py
```

### 5. 操作步骤

1. 在GUI中选择"公司资料目录"
2. 选择"简历文件"
3. 选择"报告输出目录"
4. 点击"开始批量处理"
5. 等待处理完成
6. 查看生成的综合排名报告

## 测试

运行自动化测试:
```bash
cd tests2
python test_batch_tool.py
```

测试会检查:
- 依赖模块是否安装
- MHTML读取功能
- AI客户端连接
- 批量处理基本功能

## 技术架构

### 模块说明

1. **batch_tool_main.py** - GUI界面
   - 使用Tkinter创建用户界面
   - 处理用户输入和配置保存
   - 在后台线程执行批量处理

2. **batch_processor.py** - 核心处理逻辑
   - 调度各个模块完成批量处理
   - 进度跟踪和错误处理
   - 复用原有工具的分析能力

3. **ai_client.py** - AI客户端
   - 使用Anthropic兼容接口
   - 连接到智谱AI GLM-4.7模型
   - 完整的日志记录

4. **ranking_report_generator.py** - 报告生成器
   - 将AI响应转换为HTML
   - 生成美观的综合排名报告

### 依赖项

- Python 3.8+
- anthropic (Anthropic SDK)
- PyPDF2 (PDF解析)
- python-docx (Word文档解析)
- openpyxl (Excel支持)
- tkinter (GUI,Python自带)

安装依赖:
```bash
pip install anthropic PyPDF2 python-docx openpyxl
```

## 配置文件

程序会自动保存配置到 `batch_config.json`,包括:
- 公司资料目录
- 简历文件路径
- 输出目录

下次启动时会自动加载上次的配置。

## 输出说明

处理完成后会生成:
1. **每个公司的详细报告** - `公司名.html`
2. **综合排名报告** - `公司推荐排名.html`

排名报告包含:
- 综合评分表(排名、各维度得分)
- 详细评价(优势、风险、推荐理由)
- 对比分析
- 最终建议
- 各公司详细报告链接

## 注意事项

1. **API密钥安全** - 请勿将API密钥硬编码在代码中,始终使用环境变量
2. **网络连接** - 需要稳定的网络连接调用AI接口
3. **处理时间** - 处理时间取决于公司数量和AI响应速度
4. **日志记录** - 所有AI调用都会记录到 `logs2/` 目录
5. **原有工具** - 本工具不会影响原有的"公司文化职位解析工具"

## 故障排除

### 问题1: 未找到ZHIPU_API_KEY
**解决:** 设置环境变量 `set ZHIPU_API_KEY=你的密钥`

### 问题2: 找不到公司报告
**解决:** 检查公司目录结构是否正确,确保每个公司子目录都有jd.txt和网页文件

### 问题3: AI调用失败
**解决:**
- 检查网络连接
- 检查API密钥是否有效
- 查看logs2目录中的日志

### 问题4: 程序无响应
**解决:**
- 检查任务管理器中是否有Python进程
- 确保没有其他程序占用端口

## 版本历史

### v1.0 (2025-01-14)
- 初始版本
- 支持批量处理多家公司
- 生成综合排名报告
- 完整的测试套件

## 联系方式

如有问题,请查看 `tests2/测试问题记录.txt` 并反馈。
