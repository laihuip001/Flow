# 🏛️ Architecture: Flow AI v4.0 "Unified Core"

> **Version**: 4.0.0 (Seasoning Update)
> **Philosophy**: Unified Core Strategy - PCアプリとAPIサーバーは同じ「脳」を共有する。

---

## 1. System Overview (Structural View)

本システムは、**「素材の下処理 (Pre-processing)」** に特化したAI変換エンジンです。
Flet (GUI) と FastAPI (API) という2つの「顔」を持ちますが、中枢ロジックは完全に統一されています。

### 🌐 The Unified Core Diagram

```mermaid
graph TD
    %% ==========================
    %% 1. THE BRAIN (Shared Core)
    %% ==========================
    subgraph "🧠 src/core (The Brain)"
        direction TB
        Processor["CoreProcessor<br>(Orchestrator)"]
        
        subgraph Logic Modules
            Privacy["PrivacyScanner<br>(PII Shield)"]
            Seasoning["SeasoningManager<br>(0-100% Spectrum)"]
            CostRouter["CostRouter<br>(Model Selection)"]
        end
        
        Gemini["Gemini Client<br>(Google GenAI)"]
    end

    %% ==========================
    %% 2. THE MEMORY (Infrastructure)
    %% ==========================
    subgraph "💾 src/infra (The Memory)"
        DB[(SQLite Database)]
        Session["Database Session<br>(SQLAlchemy)"]
        Cache["Prefetch Cache<br>(Offline Mode)"]
    end

    %% ==========================
    %% 3. THE INTERFACES (Tracks)
    %% ==========================
    subgraph "📱 Track A: Product"
        AppMain["run_app.py"]
        FletUI["src/app<br>(Flet GUI)"]
    end

    subgraph "🔌 Track B: Tool"
        ServerMain["run_server.py"]
        FastAPI["src/api<br>(REST API)"]
    end
    
    %% ==========================
    %% 4. THE AUDITOR (TEALS)
    %% ==========================
    subgraph "🛡️ src/infra/teals (The Auditor)"
        AuditManager["AuditManager"]
        AuditDB[(Audit DB)]
    end

    %% --- CONNECTIONS ---
    AppMain --> FletUI
    ServerMain --> FastAPI

    FletUI --> Processor
    FastAPI --> Processor

    Processor --> Privacy
    Processor --> Seasoning
    Processor --> CostRouter
    Processor --> Gemini
    Processor --> Session
    
    Session --> DB
    Session --> Cache
    
    %% Audit Connections
    Processor --> AuditManager
    AuditManager --> AuditDB
    FastAPI --> AuditManager

    %% Styles
    classDef core fill:#7e22ce,stroke:#fff,color:#fff;
    classDef infra fill:#3b82f6,stroke:#fff,color:#fff;
    classDef app fill:#10b981,stroke:#fff,color:#fff;
    classDef api fill:#f59e0b,stroke:#fff,color:#000;
    classDef audit fill:#ef4444,stroke:#fff,color:#fff;

    class Processor,Privacy,Seasoning,CostRouter,Gemini core;
    class DB,Session,Cache infra;
    class AppMain,FletUI app;
    class ServerMain,FastAPI api;
    class AuditManager,AuditDB audit;
```

---

## 2. Core Logic Sequence

Flow AIの中枢である `CoreProcessor` の処理フローです。
**「Zero Trust Privacy」** と **「Speed First」** を両立させるためのパイプライン構造になっています。

### 🌊 The Processing Pipeline

```mermaid
sequenceDiagram
    participant User as Client (App/API)
    participant Core as CoreProcessor
    participant Privacy as PrivacyScanner
    participant Cache as DB Cache
    participant Gemini as Google Gemini
    
    User->>Core: process(text, seasoning_level)
    
    %% 1. Sanitize Log
    Note over Core: 1. Log Sanitization (Hash only)
    
    %% 2. Cache Check
    Core->>Cache: check_cache(hash, seasoning)
    alt Cache Hit
        Cache-->>Core: return cached_result
        Core-->>User: return cached_result (Fast!)
    else Cache Miss
    
        %% 3. PII Masking
        Core->>Privacy: mask_numbers_and_names(text)
        Privacy-->>Core: masked_text (Safe)
        
        %% 4. Model Selection
        Note over Core: 4. CostRouter Selects Model<br>(Flash = Default, Pro = Complicated)
        
        %% 5. AI Generation
        Core->>Gemini: generate_content(masked_text + system_prompt)
        Gemini-->>Core: generated_text (Masked)
        
        %% 6. Unmasking
        Core->>Privacy: unmask(generated_text)
        Privacy-->>Core: final_text (Original PII Restored)
        
        %% 7. Save Cache
        Core->>Cache: save(hash, final_text)
        
        Core-->>User: return final_text
    end
```

---

## 3. Directory Structure & Roles

### `src/core` (The Brain) 🧠

**「どこでも動く」純粋なロジック**。

* **依存禁止:** UIライブラリ(Flet)、Webフレームワーク(FastAPI)、OS依存機能(pyperclip)。
* **役割:**
  * `processor.py`: アプリケーションの全機能を統括。パイプライン全体を制御する指揮者。
  * `privacy.py`: 外部APIを叩く前の最後の砦（PII検知）。正規表現によるPII検出と置換。
  * `seasoning.py`: **v4.0の新概念**。離散的な「スタイル」ではなく、0〜100%の「味付け濃度」でプロンプトを動的に生成。
    * 0-30% (Salt): 復元・修正のみ
    * 31-70% (Sauce): 整形・補完
    * 71-100% (Spice): 創造・拡張

### `src/infra` (The Memory) 💾

データの永続化を担当します。

* `database.py`: DB接続セッションの管理。WALモードを有効化し、並列書き込み性能を向上。
* `audit.py` & `teals/`: **TEALS** (Tamper-Evident Audit Log System) による改ざん検知可能な監査ログ基盤。
  * `audit_log.db` に保管され、ハッシュチェーン技術でデータの完全性を保証します。

### `src/app` (The Face) 📱

**ユーザーとの対話**を担当します。

* **Track A (Product):** PCおよびAndroidで動作するFletアプリ。
* `ui.py`: Fletを使用したクロスプラットフォームUI。ロジックを持たず、CoreProcessorを呼び出すだけの「薄い」層。

### `src/api` (The Gateway) 🔌

**外部システム連携**を担当します。

* **Track B (Tool):** Termuxや他ツールからのHTTPリクエストを受け付けます。
* FastAPIのエンドポイント定義のみを行い、処理は `src/core` に委譲します。

---

## 4. Development Workflow

### 🔄 The "Unified" Cycle

1. **Logic Update**: `src/core/seasoning.py` のロジックを修正。
2. **Instant Reflection**: PCアプリ(App)とAPIサーバー(Server)の**両方に即座に反映**。
3. **Deployment**:
    * PC: `run_app.py`
    * Server: `run_server.py`

この「一箇所直せば全て直る」状態こそが、Unified Coreの真価です。
