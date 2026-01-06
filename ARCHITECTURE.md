# 🏛️ Architecture & Workflow: AI Clipboard Pro v3.3 Titanium

## 1. System Overview (Structural View)

本プロジェクトは、**Strategic Layer (脳)** と **Execution Layer (手)** を明確に分離し、**Runtime Layer (現場)** の自律稼働を保証する「Titanium Architecture」を採用しています。

### 🌐 垂直統合ロールマップ (Vertical Integration)

```mermaid
graph TD
    %% ==========================
    %% 0. THE ARCHITECT
    %% ==========================
    User((👤 The Architect<br>あなた))

    %% ==========================
    %% 1. STRATEGIC LAYER (脳)
    %% ==========================
    subgraph "🧠 STRATEGIC LAYER (司令室)"
        Claude[🟣 Claude Pro / Gemini 3 Pro<br>最高意思決定・設計図生成]
        AIStudio[🧪 Google AI Studio<br>プロンプト実験・モデル調整]
        DebugLog[📄 .ai/DEBUG_LOG.md<br>エラー分析・再設計]
    end

    %% ==========================
    %% 2. PROTOCOL LAYER (プロトコル)
    %% ==========================
    subgraph "📋 PROTOCOL (共通言語)"
        TaskFile[📄 .ai/JULES_TASK.md<br>構造化指示プロトコル]
        Context[📄 .ai/SYSTEM_CONTEXT.md<br>環境定義・憲法]
    end

    %% ==========================
    %% 3. EXECUTION LAYER (手)
    %% ==========================
    subgraph "⚡ EXECUTION LAYER (工場)"
        subgraph "🏠 Home (Power)"
            Jules_AG[👨‍💻 Jules Local<br>Google Antigravity]
            Scanner_AG[🔒 secure_push.sh]
        end
        subgraph "☕ Mobile (Speed)"
            Jules_FS[👨‍💻 Jules Cloud<br>Firebase Studio]
            Scanner_FS[🔒 secure_push.sh]
        end
    end

    %% ==========================
    %% 4. INFRASTRUCTURE (保存)
    %% ==========================
    subgraph "💾 INFRASTRUCTURE"
        GH[🐙 GitHub Repository<br>Single Source of Truth]
    end

    %% ==========================
    %% 5. RUNTIME LAYER (現場)
    %% ==========================
    subgraph "🛡️ RUNTIME LAYER (要塞)"
        Termux[📟 Android Termux<br>Pixel 9a / OPPO Pad]
        Watcher[🛡️ titanium_watcher.sh<br>自律防衛・監視]
        App[🚀 Application]
    end

    %% --- FLOW: DOWNSTREAM (設計 -> 稼働) ---
    User -- "1. 要件定義" --> Claude
    User -- "検証" --> AIStudio
    Claude -- "2. 出力" --> TaskFile
    Context -. "制約適用" .-> Jules_AG
    Context -. "制約適用" .-> Jules_FS
    
    TaskFile -- "3. 実装指示" --> Jules_AG
    TaskFile -- "3. 実装指示" --> Jules_FS
    
    Jules_AG -- "Commit" --> Scanner_AG
    Jules_FS -- "Commit" --> Scanner_FS
    
    Scanner_AG -- "4. Pass & Push" --> GH
    Scanner_FS -- "4. Pass & Push" --> GH
    
    GH -- "5. Poll & Pull" --> Watcher
    Watcher -- "6. Deploy" --> App

    %% --- FLOW: UPSTREAM (エラー -> 改善) ---
    App -- "❌ Crash" --> DebugLog
    DebugLog -- "7. 分析" --> Claude

    %% スタイル定義
    classDef role fill:#222,stroke:#fff,stroke-width:4px,color:#fff;
    classDef brain fill:#7e22ce,stroke:#fff,color:#fff;
    classDef protocol fill:#f59e0b,stroke:#fff,color:#000;
    classDef worker fill:#10b981,stroke:#fff,color:#fff;
    classDef security fill:#ef4444,stroke:#fff,color:#fff;
    classDef infra fill:#3b82f6,stroke:#fff,color:#fff;
    
    class User role;
    class Claude,AIStudio,DebugLog brain;
    class TaskFile,Context protocol;
    class Jules_AG,Jules_FS worker;
    class Scanner_AG,Scanner_FS,Watcher security;
    class GH,Termux,App infra;
```

---

## 2. Development Workflow (Temporal View)

開発からデプロイまでの時系列フロー。人間の介入はPhase 1に集中し、以降は自動化されます。

### ⏱️ The Titanium Loop

```mermaid
sequenceDiagram
    autonumber
    participant Arch as 👤 Architect
    participant Brain as 🧠 Claude/AI Studio
    participant Jules as 👨‍💻 Jules (IDE)
    participant GH as 🐙 GitHub
    participant Watcher as 🛡️ Watcher (Termux)

    Note over Arch, Brain: Phase 1: 戦略設計 (Strategic)
    Arch->>Brain: 要件定義 & プロンプト検証
    Brain-->>Arch: .ai/JULES_TASK.md (構造化指示書)

    Note over Arch, Jules: Phase 2: 実装 & 検証 (Execution)
    Arch->>Jules: 「JULES_TASK.md を実行せよ」
    Jules->>Jules: コード生成 + 構文チェック (compileall)
    Jules->>GH: dev_tools/secure_push.sh (Security Scan + Push)

    Note over GH, Watcher: Phase 3: 自律デプロイ (Deployment)
    Watcher->>GH: 1分ごとに変更監視 (Polling)
    GH-->>Watcher: 変更検知 (Diff)
    Watcher->>Watcher: git pull + pip install
    Watcher->>Watcher: /healthz 監視 + Circuit Breaker

    Note over Watcher, Arch: Phase 4: 稼働 (Production)
    Watcher-->>Arch: Health OK / 自動停止 (Panic)
```

---

## 3. Core Principles (Titanium 3鉄則)

### ① Protocol First (「伝書鳩」からの卒業)

- **従来:** あなたがClaudeの回答を読み、要約してJulesに伝えていた。
- **現在:** Claudeが生成した `.ai/JULES_TASK.md` を、Julesが直接読み取る。
- **効果:** 指示の劣化（ハルシネーション）を防止。

### ② Environment Agnostic (開発拠点の完全同期)

- **自宅:** Antigravity IDEのJulesが `sync.sh start` で最新状態を取得。
- **外出先:** Firebase Studio (OPPO Pad/カフェ) で続きを実装。
- **結果:** どのデバイスでも常に最新のコードとAIの思考がある。

### ③ Titanium Shield (Termuxを「要塞」に)

- **監視:** `/healthz` を叩き、ゾンビ状態を検知。
- **防衛:** 無限再起動ループで発熱死を防ぐCircuit Breaker。
- **制約:** `SYSTEM_CONTEXT.md` によりTermux非互換ライブラリを排除。

---

## 4. Directory Structure

```
📁 Project Root
├── .ai/                    # Strategic Layer
│   ├── SYSTEM_CONTEXT.md   # Agent Constitution
│   ├── JULES_TASK.md       # Task Protocol
│   └── DEBUG_LOG.md        # Error Template
├── maintenance/            # Runtime Layer
│   └── titanium_watcher.sh # Auto-Deploy + Circuit Breaker
├── dev_tools/              # Dev Layer
│   ├── secure_push.sh      # Secret Scan
│   └── sync.sh             # Dev Ritual
├── github_agent/           # MCP Agent
└── main.py                 # Core App
```

---

## 5. Your Role: The Architect

1. **Claude** で「何を作るか（What）」を決定
2. **AI Studio** で「AIの言葉（Prompt）」の精度を極める
3. **Jules** に「作業（How）」を命じ、GitHubへ流し込ませる
4. **Titanium Watcher** が現場（Termux）を24時間守り抜く

このサイクルを回すことで、最小限の労力で最大限に堅牢なAIシステムを構築し続けることができます。
