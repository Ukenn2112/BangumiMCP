# [Bangumi TV](https://bgm.tv/) MCP Service

这是一个MCP（机器通信协议）服务，提供对 BangumiTV API 的访问。它允许您与 BangumiTV 的数据进行交互，并检索有关动漫、漫画、音乐、游戏等的信息。

## 示例

![output](https://github.com/user-attachments/assets/9ea4b0c1-6208-4997-a1c5-62a0c6454be8)

## 功能

- 条目
    - /calendar 每日放送
    - /v0/search/subjects 搜索主题
    - /v0/subjects 浏览主题
    - /v0/subjects/{subject_id} 获取主题详情
    - /v0/subjects/{subject_id}/persons 获取与主题相关的人员列表
    - /v0/subjects/{subject_id}/characters 获取与主题相关的角色列表
    - /v0/subjects/{subject_id}/subjects 获取相关主题列表

- 章节
    - /v0/episodes 获取剧集列表
    - /v0/episodes/{episode_id} 获取剧集详情

- 角色
    - /v0/search/characters 搜索角色
    - /v0/characters/{character_id} 获取角色详情
    - /v0/characters/{character_id}/subjects 获取与角色相关的主题列表
    - /v0/characters/{character_id}/persons 获取与角色相关的人员列表

- 人员
    - /v0/search/persons 搜索人员
    - /v0/persons/{person_id} 获取人员详情
    - /v0/persons/{person_id}/subjects 获取与人员相关的主题列表
    - /v0/persons/{person_id}/characters 获取与人员相关的角色列表

## 安装

```bash
# 克隆仓库
git clone https://github.com/Ukenn2112/BangumiMCP.git
cd BangumiMCP

# 创建并激活虚拟环境
uv venv
source .venv/bin/activate  # Linux/macOS
# 或在 Windows 上使用:
# .venv\Scripts\activate

# 安装依赖
uv add "mcp[cli]" requests
```

## 使用（如Claude客户端）

 URL: https://mcpcn.com/docs/quickstart/user/

claude_desktop_config.json
```json
{
    "mcpServers": {
        "bangumi-tv": {
            "command": "uv",
            "args": [
                "--directory",
                "/Users/Desktop/bangumi-tv", # 替换为你的目录
                "run",
                "main.py"
            ],
            "env": {
                "BANGUMI_TOKEN": "your_token_here" # 替换为你的 BangumiTV 令牌 （可选）如果你要查看或搜索R18内容
            }
        }
    }
}
```

# 致谢

此目前项目全部由 [Google Gemini](https://www.google.com/) 生成。
