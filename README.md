# Bangumi MCP Server

[English](#english) | [中文](#中文)

---

## English

A Model Context Protocol (MCP) server that provides programmatic access to the [Bangumi TV](https://bgm.tv/) API, enabling AI assistants like Claude to interact with comprehensive anime, manga, music, game, and real-world media data.

### Features

- **55 MCP Tools**: Complete coverage of Bangumi API endpoints
- **3 Workflow Prompts**: Pre-built multi-step workflows for common tasks
- **1 Resource**: Full OpenAPI specification for API documentation
- **Modular Architecture**: Clean, maintainable codebase following MCP best practices
- **Type-Safe**: Full Python type hints and enum definitions
- **Async Support**: Non-blocking API calls using httpx

### Quick Start

#### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

#### Installation

```bash
# Clone the repository
git clone https://github.com/Ukenn2112/BangumiMCP.git
cd BangumiMCP

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

#### Configuration for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bangumi-tv": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/BangumiMCP",
        "run",
        "main.py"
      ],
      "env": {
        "BANGUMI_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Note**: `BANGUMI_TOKEN` is only used for the local stdio mode, and is required for:
- Authenticated operations (collections, personal data)
- R18 content access
- Write operations (create, update, delete)

Get your token at: https://next.bgm.tv/demo/access-token

### Cloudflare Python Worker (Public MCP)

Use `wrangler.jsonc` and `src/worker.py` to deploy a public MCP endpoint on Cloudflare Python Workers.

- MCP endpoint: `/mcp`
- Send `Authorization: Bearer <your Bangumi access token>` on every request
- The worker is stateless and does not store user tokens
- `python_modules/` is generated automatically by `npm install` / Cloudflare build via `postinstall`
- Keep local stdio by running `uv run main.py`
- Sync vendored Python deps with `npm run sync`
- Start local Worker dev with `npm run dev` (syncs `python_modules/` and then runs `wrangler dev`)
- Deploy with `npm run deploy` (syncs `python_modules/` and then runs `wrangler deploy`)

### Project Architecture

BangumiMCP follows a modular architecture designed for maintainability and scalability:

```
BangumiMCP/
├── main.py                           # Server initialization (44 lines)
├── wrangler.jsonc                    # Cloudflare Python Worker config
├── src/
│   ├── config.py                     # Configuration constants
│   ├── enums.py                      # API enum definitions (8 types)
│   ├── utils/
│   │   ├── request_auth.py           # Request-scoped auth helpers
│   │   ├── api_client.py             # HTTP client & error handling
│   │   └── formatters.py             # Data formatting utilities
│   ├── worker.py                     # Cloudflare Worker entrypoint
│   ├── resources/
│   │   └── openapi_resource.py       # OpenAPI specification resource
│   ├── tools/                        # 55 MCP tools organized by domain
│   │   ├── subject_tools.py          # Subjects & episodes (10 tools)
│   │   ├── character_tools.py        # Characters (7 tools)
│   │   ├── person_tools.py           # Persons & companies (7 tools)
│   │   ├── user_tools.py             # User information (3 tools)
│   │   ├── collection_tools.py       # Collections (11 tools)
│   │   ├── revision_tools.py         # Edit history (8 tools)
│   │   └── index_tools.py            # Indices/directories (9 tools)
│   └── prompts/
│       └── workflow_prompts.py       # Composite prompts (3)
├── bangumi-tv-api.json               # OpenAPI 3.0.3 specification
└── pyproject.toml                    # Project metadata
```

### Available Tools

#### Subjects & Episodes (10 tools)

- `get_daily_broadcast` - Weekly broadcast schedule
- `search_subjects` - Full-text search with filters
- `browse_subjects` - Category-based browsing
- `get_subject_details` - Detailed subject information
- `get_subject_image` - Subject image URL
- `get_subject_persons` - Related creators/staff
- `get_subject_characters` - Related characters
- `get_subject_relations` - Related subjects
- `get_episodes` - Episode list
- `get_episode_details` - Episode information

#### Characters (7 tools)

- `search_characters` - Character search
- `get_character_details` - Character information
- `get_character_image` - Character image URL
- `get_character_subjects` - Subjects featuring character
- `get_character_persons` - Voice actors & creators
- `collect_character` - Add to favorites ⚠️ Requires auth
- `uncollect_character` - Remove from favorites ⚠️ Requires auth

#### Persons (7 tools)

- `search_persons` - Search creators/actors
- `get_person_details` - Person information
- `get_person_image` - Person image URL
- `get_person_subjects` - Works by person
- `get_person_characters` - Characters associated
- `collect_person` - Add to favorites ⚠️ Requires auth
- `uncollect_person` - Remove from favorites ⚠️ Requires auth

#### Users (3 tools)

- `get_user_info` - Public user profile
- `get_user_avatar` - User avatar URL
- `get_current_user` - Authenticated user info ⚠️ Requires auth

#### Collections (11 tools)

- `get_user_collections` - User's subject collections
- `get_user_subject_collection` - Subject collection status
- `update_subject_collection` - Update subject status ⚠️ Requires auth
- `get_user_episode_collection` - Episode watch list ⚠️ Requires auth
- `update_episode_collection` - Batch update episodes ⚠️ Requires auth
- `get_single_episode_collection` - Single episode status ⚠️ Requires auth
- `update_single_episode_collection` - Update single episode ⚠️ Requires auth
- `get_user_character_collections` - Character collections
- `get_user_character_collection` - Character collection status
- `get_user_person_collections` - Person collections
- `get_user_person_collection` - Person collection status

#### Revisions (8 tools)

- `get_person_revisions` - Person edit history
- `get_person_revision` - Single person edit detail
- `get_character_revisions` - Character edit history
- `get_character_revision` - Single character edit detail
- `get_subject_revisions` - Subject edit history
- `get_subject_revision` - Single subject edit detail
- `get_episode_revisions` - Episode edit history
- `get_episode_revision` - Single episode edit detail

#### Indices (9 tools)

- `create_index` - Create new index ⚠️ Requires auth
- `get_index` - Index details
- `update_index` - Update index info ⚠️ Requires auth
- `get_index_subjects` - Subjects in index
- `add_subject_to_index` - Add subject ⚠️ Requires auth
- `update_index_subject` - Update subject info ⚠️ Requires auth
- `remove_subject_from_index` - Remove subject ⚠️ Requires auth
- `collect_index` - Add index to collection ⚠️ Requires auth
- `uncollect_index` - Remove index from collection ⚠️ Requires auth

### Workflow Prompts

Pre-built multi-step workflows for common tasks:

- **search_and_summarize_anime** - Search anime by keyword and get AI summary
- **get_subject_full_info** - Get comprehensive subject information (details, persons, characters, relations)
- **find_voice_actor** - Search character and identify voice actors

### Development

#### Adding New Tools

1. Identify the appropriate category (subject, character, person, etc.)
2. Add the tool function to the corresponding file in `src/tools/`
3. Register the tool in the module's `register()` function
4. Update this README with the new tool count

#### Testing

```bash
# Test imports
python -c "from src.config import BANGUMI_TOKEN; print('OK')"
python -c "from src.tools import subject_tools; print('OK')"

# Run the server
uv run main.py
```

#### Code Structure

**Dependency Hierarchy** (no circular imports):
- Level 0: `config.py`, `enums.py` (no dependencies)
- Level 1: `utils/` (depends on config & enums)
- Level 2: `resources/`, `tools/`, `prompts/` (depend on utils)
- Level 3: `main.py` (orchestrates everything)

**Import Guidelines**:
- Use relative imports within `src/` package (e.g., `from ..config import`)
- Import from specific modules, not package level
- Follow the dependency hierarchy to avoid circular imports

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BANGUMI_TOKEN` | No | Local stdio fallback Bangumi Access Token for authenticated operations and R18 content |

### License

This project is built on the Bangumi API documentation and follows its terms of service.

### Related Projects

- **[BangumiMCP-ts](https://github.com/Tokisaki-Galaxy/BangumiMCP-ts)** - TypeScript version of BangumiMCP

### Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## 中文

一个基于 Model Context Protocol (MCP) 的服务器，为 [Bangumi TV](https://bgm.tv/) API 提供程序化访问接口，使 Claude 等 AI 助手能够与海量的动画、漫画、音乐、游戏和真人影视数据进行交互。

### 功能特性

- **55 个 MCP 工具**：完整覆盖 Bangumi API 端点
- **3 个工作流提示**：预构建的多步骤工作流，用于常见任务
- **1 个资源**：完整的 OpenAPI 规范文档
- **模块化架构**：清晰、可维护的代码库，遵循 MCP 最佳实践
- **类型安全**：完整的 Python 类型提示和枚举定义
- **异步支持**：使用 httpx 的非阻塞 API 调用

### 快速开始

#### 前置要求

- Python 3.10 或更高版本
- [uv](https://docs.astral.sh/uv/) 包管理器（推荐）或 pip

#### 安装

```bash
# 克隆仓库
git clone https://github.com/Ukenn2112/BangumiMCP.git
cd BangumiMCP

# 创建并激活虚拟环境
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
uv pip install -e .
```

#### Claude Desktop 配置

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "bangumi-tv": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/BangumiMCP",
        "run",
        "main.py"
      ],
      "env": {
        "BANGUMI_TOKEN": "your_token_here"
      }
    }
  }
}
```

**注意**：`BANGUMI_TOKEN` 只用于本地 stdio 模式，但以下操作需要：
- 认证操作（收藏、个人数据）
- 访问 R18 内容
- 写操作（创建、更新、删除）

获取令牌：https://next.bgm.tv/demo/access-token

### Cloudflare Python Worker（公开 MCP）

使用 `wrangler.jsonc` 和 `src/worker.py` 可以把服务部署成 Cloudflare Python Workers 上的公开 MCP 端点。

- MCP 端点：`/mcp`
- 每次请求都带上 `Authorization: Bearer <你的 Bangumi 令牌>`
- Worker 是无状态的，不保存用户 token
- 本地 stdio 继续使用 `uv run main.py`
- 本地 Worker 开发可用 `uvx --from workers-py pywrangler dev`

### 项目架构

BangumiMCP 采用模块化架构，便于维护和扩展：

```
BangumiMCP/
├── main.py                           # 服务器初始化（44 行）
├── wrangler.jsonc                    # Cloudflare Python Worker 配置
├── src/
│   ├── config.py                     # 配置常量
│   ├── enums.py                      # API 枚举定义（8 种类型）
│   ├── utils/
│   │   ├── request_auth.py           # 请求级认证辅助
│   │   ├── api_client.py             # HTTP 客户端和错误处理
│   │   └── formatters.py             # 数据格式化工具
│   ├── worker.py                     # Cloudflare Worker 入口
│   ├── resources/
│   │   └── openapi_resource.py       # OpenAPI 规范资源
│   ├── tools/                        # 55 个 MCP 工具，按领域组织
│   │   ├── subject_tools.py          # 条目和章节（10 个工具）
│   │   ├── character_tools.py        # 角色（7 个工具）
│   │   ├── person_tools.py           # 人物和公司（7 个工具）
│   │   ├── user_tools.py             # 用户信息（3 个工具）
│   │   ├── collection_tools.py       # 收藏（11 个工具）
│   │   ├── revision_tools.py         # 编辑历史（8 个工具）
│   │   └── index_tools.py            # 目录（9 个工具）
│   └── prompts/
│       └── workflow_prompts.py       # 组合提示（3 个）
├── bangumi-tv-api.json               # OpenAPI 3.0.3 规范
└── pyproject.toml                    # 项目元数据
```

### 可用工具

#### 条目和章节（10 个工具）

- `get_daily_broadcast` - 每周放送时间表
- `search_subjects` - 全文搜索，支持过滤
- `browse_subjects` - 按分类浏览
- `get_subject_details` - 详细条目信息
- `get_subject_image` - 条目图片 URL
- `get_subject_persons` - 相关创作者/制作人员
- `get_subject_characters` - 相关角色
- `get_subject_relations` - 相关条目
- `get_episodes` - 章节列表
- `get_episode_details` - 章节信息

#### 角色（7 个工具）

- `search_characters` - 角色搜索
- `get_character_details` - 角色信息
- `get_character_image` - 角色图片 URL
- `get_character_subjects` - 角色出现的条目
- `get_character_persons` - 声优和创作者
- `collect_character` - 添加到收藏 ⚠️ 需要认证
- `uncollect_character` - 从收藏中移除 ⚠️ 需要认证

#### 人物（7 个工具）

- `search_persons` - 搜索创作者/演员
- `get_person_details` - 人物信息
- `get_person_image` - 人物图片 URL
- `get_person_subjects` - 人物参与的作品
- `get_person_characters` - 关联的角色
- `collect_person` - 添加到收藏 ⚠️ 需要认证
- `uncollect_person` - 从收藏中移除 ⚠️ 需要认证

#### 用户（3 个工具）

- `get_user_info` - 公开用户资料
- `get_user_avatar` - 用户头像 URL
- `get_current_user` - 当前认证用户信息 ⚠️ 需要认证

#### 收藏（11 个工具）

- `get_user_collections` - 用户的条目收藏
- `get_user_subject_collection` - 条目收藏状态
- `update_subject_collection` - 更新条目状态 ⚠️ 需要认证
- `get_user_episode_collection` - 章节观看列表 ⚠️ 需要认证
- `update_episode_collection` - 批量更新章节 ⚠️ 需要认证
- `get_single_episode_collection` - 单个章节状态 ⚠️ 需要认证
- `update_single_episode_collection` - 更新单个章节 ⚠️ 需要认证
- `get_user_character_collections` - 角色收藏
- `get_user_character_collection` - 角色收藏状态
- `get_user_person_collections` - 人物收藏
- `get_user_person_collection` - 人物收藏状态

#### 修订历史（8 个工具）

- `get_person_revisions` - 人物编辑历史
- `get_person_revision` - 单个人物编辑详情
- `get_character_revisions` - 角色编辑历史
- `get_character_revision` - 单个角色编辑详情
- `get_subject_revisions` - 条目编辑历史
- `get_subject_revision` - 单个条目编辑详情
- `get_episode_revisions` - 章节编辑历史
- `get_episode_revision` - 单个章节编辑详情

#### 目录（9 个工具）

- `create_index` - 创建新目录 ⚠️ 需要认证
- `get_index` - 目录详情
- `update_index` - 更新目录信息 ⚠️ 需要认证
- `get_index_subjects` - 目录中的条目
- `add_subject_to_index` - 添加条目 ⚠️ 需要认证
- `update_index_subject` - 更新条目信息 ⚠️ 需要认证
- `remove_subject_from_index` - 移除条目 ⚠️ 需要认证
- `collect_index` - 收藏目录 ⚠️ 需要认证
- `uncollect_index` - 取消收藏目录 ⚠️ 需要认证

### 工作流提示

预构建的多步骤工作流，用于常见任务：

- **search_and_summarize_anime** - 按关键字搜索动画并获取 AI 摘要
- **get_subject_full_info** - 获取全面的条目信息（详情、人物、角色、关联）
- **find_voice_actor** - 搜索角色并识别声优

### 开发

#### 添加新工具

1. 确定合适的类别（条目、角色、人物等）
2. 将工具函数添加到 `src/tools/` 中相应的文件
3. 在模块的 `register()` 函数中注册工具
4. 更新此 README 中的工具数量

#### 测试

```bash
# 测试导入
python -c "from src.config import BANGUMI_TOKEN; print('OK')"
python -c "from src.tools import subject_tools; print('OK')"

# 运行服务器
uv run main.py
```

#### 代码结构

**依赖层次结构**（无循环导入）：
- Level 0: `config.py`, `enums.py`（无依赖）
- Level 1: `utils/`（依赖 config 和 enums）
- Level 2: `resources/`, `tools/`, `prompts/`（依赖 utils）
- Level 3: `main.py`（协调所有模块）

**导入指南**：
- 在 `src/` 包内使用相对导入（例如 `from ..config import`）
- 从特定模块导入，而不是包级别
- 遵循依赖层次结构以避免循环导入

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `BANGUMI_TOKEN` | 否 | 本地 stdio 兜底用的 Bangumi 访问令牌，用于认证操作和访问 R18 内容 |

### 许可证

此项目基于 Bangumi API 文档构建，并遵循其服务条款。

### 相关项目

- **[BangumiMCP-ts](https://github.com/Tokisaki-Galaxy/BangumiMCP-ts)** - BangumiMCP 的 TypeScript 版本

### 贡献

欢迎贡献！请随时提交问题或拉取请求。

---

## 致谢

此项目基于 [Bangumi API](https://github.com/bangumi/api) 文档构建。
