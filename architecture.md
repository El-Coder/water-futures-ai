# Water Futures AI - System Architecture

## System Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Frontend<br/>TypeScript + Vite]
        CB[ChatbotV2 Component<br/>Dual Mode Interface]
        TUI[Trading UI<br/>Portfolio & Orders]
    end
    
    subgraph "API Gateway"
        FAPI[FastAPI Backend<br/>main_simple.py]
        AUTH[CORS Middleware<br/>Authentication]
    end
    
    subgraph "Core Services"
        FA[Farmer Agent<br/>Claude-powered]
        MCP[MCP Connector<br/>Message Router]
        ALP[Alpaca MCP Client<br/>Trading Service]
        VAI[Vertex AI Service<br/>ML Predictions]
        DS[Data Store<br/>Historical Data]
    end
    
    subgraph "MCP Servers"
        TA[Trading Agent MCP<br/>Smithery Registry]
        FAS[Farmer Assistant MCP<br/>Claude Integration]
    end
    
    subgraph "External Services"
        ALPACA[Alpaca API<br/>Paper Trading]
        CROSS[Crossmint<br/>Payment Processing]
        CLAUDE[Claude AI<br/>Anthropic API]
        GCP[Google Cloud<br/>Vertex AI]
        NEWS[News APIs<br/>Market Data]
    end
    
    subgraph "Database Layer"
        PG[(PostgreSQL<br/>+ pgvector)]
    end
    
    UI --> CB
    CB --> FAPI
    TUI --> FAPI
    FAPI --> AUTH
    AUTH --> FA
    AUTH --> DS
    FA --> MCP
    FA --> ALP
    FA --> VAI
    MCP --> TA
    MCP --> FAS
    ALP --> ALPACA
    FAS --> CLAUDE
    FAS --> CROSS
    VAI --> GCP
    DS --> PG
    FAPI --> NEWS
    
    style UI fill:#61dafb
    style CB fill:#ff6b6b
    style FA fill:#4ecdc4
    style CLAUDE fill:#7f5af0
    style ALPACA fill:#00d4aa
    style CROSS fill:#ffd93d
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant UI as React UI
    participant CB as ChatbotV2
    participant API as FastAPI
    participant FA as Farmer Agent
    participant ALP as Alpaca Client
    participant CROSS as Crossmint
    
    U->>UI: Open Chat
    UI->>CB: Initialize Chat
    
    alt Chat Mode (Safe)
        U->>CB: Ask Question
        CB->>API: POST /api/v1/chat
        API->>FA: process_request(mode="chat")
        FA->>FA: Analyze Intent
        FA-->>API: Information Response
        API-->>CB: Display Info
        CB-->>U: Show Response
    else Agent Mode (Live)
        U->>CB: Enable Agent Mode
        CB->>U: Show Warning Dialog
        U->>CB: Confirm Agent Mode
        CB->>CB: Set agentMode=true
        
        U->>CB: "Buy 5 water futures"
        CB->>API: POST /api/v1/agent/execute
        API->>FA: process_request(mode="agent")
        FA->>ALP: place_water_futures_order()
        ALP->>ALP: Map Symbol (NQH25→SPY)
        
        Note over CB,U: Trade Approval Dialog
        CB->>U: Show Trade Details
        alt User Approves
            U->>CB: ACCEPT Trade
            CB->>API: Confirm Execution
            ALP->>ALPACA: Submit Order
            ALPACA-->>ALP: Order Confirmation
            ALP-->>FA: Trade Result
            FA-->>API: Execution Details
            API-->>CB: Success Response
            CB-->>U: Trade Executed ✅
        else User Declines
            U->>CB: DECLINE Trade
            CB->>API: Cancel Trade
            API-->>CB: Trade Cancelled
            CB-->>U: Trade Cancelled ❌
        end
    end
    
    alt Subsidy Processing
        U->>CB: "Process drought subsidy"
        CB->>API: POST /api/v1/agent/execute
        API->>FA: process_request(subsidy)
        FA->>CROSS: Process Payment
        CROSS-->>FA: Payment ID
        FA-->>API: Subsidy Processed
        API-->>CB: Success Response
        CB-->>U: Subsidy Claimed 💰
    end
```

## Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        APP[App.tsx]
        LAY[Layout.tsx]
        CHAT[ChatbotV2.tsx<br/>Trade Approval UI]
        TRADE[Trading.tsx]
        FORE[Forecast.tsx]
        NEWS[News.tsx]
        ACC[Account.tsx]
    end
    
    subgraph "Backend Services"
        MAIN[main_simple.py]
        FA[farmer_agent.py]
        ALP[alpaca_mcp_client.py]
        MCP[mcp_connector.py]
        VAI[vertex_ai_service.py]
        DS[data_store.py]
        DB[database.py]
    end
    
    subgraph "API Routes"
        R1[/api/v1/chat]
        R2[/api/v1/agent/execute]
        R3[/api/v1/agent/action]
        R4[/api/v1/water-futures/*]
        R5[/api/v1/forecasts/*]
        R6[/api/v1/trading/*]
        R7[/api/v1/news/*]
    end
    
    APP --> LAY
    LAY --> CHAT
    LAY --> TRADE
    LAY --> FORE
    LAY --> NEWS
    LAY --> ACC
    
    CHAT -.->|Chat Mode| R1
    CHAT ==>|Agent Mode| R2
    CHAT ==>|Approved Action| R3
    TRADE --> R6
    FORE --> R5
    NEWS --> R7
    ACC --> R4
    
    R1 --> FA
    R2 --> FA
    R3 --> MCP
    R4 --> DS
    R5 --> VAI
    R6 --> ALP
    R7 --> DS
    
    FA --> ALP
    FA --> MCP
    FA --> VAI
    MCP --> ALP
    DS --> DB
    
    style CHAT fill:#ff6b6b
    style FA fill:#4ecdc4
    style R2 stroke:#ff0000,stroke-width:3px
```

## Trade Approval Flow

```mermaid
stateDiagram-v2
    [*] --> ChatMode: Initial State
    
    ChatMode --> AgentWarning: Toggle Agent Mode
    AgentWarning --> ChatMode: Cancel
    AgentWarning --> AgentMode: Confirm
    
    AgentMode --> AnalyzeIntent: User Message
    AnalyzeIntent --> TradeIntent: Detect Trade
    AnalyzeIntent --> SubsidyIntent: Detect Subsidy
    AnalyzeIntent --> InfoIntent: Information Query
    
    TradeIntent --> ShowApproval: Display Trade Details
    ShowApproval --> ExecuteTrade: User Accepts
    ShowApproval --> CancelTrade: User Declines
    
    ExecuteTrade --> AlpacaAPI: Send Order
    AlpacaAPI --> TradeSuccess: Order Filled
    AlpacaAPI --> TradeFailed: Order Failed
    
    CancelTrade --> AgentMode: Return to Chat
    TradeSuccess --> LogTransaction: Record Trade
    TradeFailed --> ShowError: Display Error
    
    SubsidyIntent --> ProcessSubsidy: Auto-Process
    ProcessSubsidy --> CrossmintAPI: Send Payment Request
    CrossmintAPI --> SubsidySuccess: Payment Processed
    
    InfoIntent --> GenerateResponse: Claude Response
    GenerateResponse --> AgentMode: Display Info
    
    LogTransaction --> AgentMode: Continue
    SubsidySuccess --> AgentMode: Continue
    ShowError --> AgentMode: Continue
    
    AgentMode --> ChatMode: Disable Agent Mode
    
    state ShowApproval {
        [*] --> DisplayDialog
        DisplayDialog --> ShowDetails
        ShowDetails: Trade Type: BUY/SELL
        ShowDetails: Symbol: NQH25
        ShowDetails: Quantity: X contracts
        ShowDetails: Estimated Cost: $XXX
        ShowDetails --> AwaitDecision
        AwaitDecision --> [*]
    }
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        UI[User Interface]
        VM[Visual Mode Indicators]
        CD[Confirmation Dialogs]
        AL[Audit Logging]
        PT[Paper Trading]
        AC[API Authentication]
        RL[Rate Limiting]
    end
    
    subgraph "Chat Mode"
        CM1[Read-Only Access]
        CM2[No Execution Rights]
        CM3[Information Queries Only]
    end
    
    subgraph "Agent Mode"
        AM1[Explicit Enablement Required]
        AM2[Warning Dialog Mandatory]
        AM3[Per-Action Approval]
        AM4[Transaction Logging]
        AM5[Real-time Status Updates]
    end
    
    UI --> VM
    VM --> |Safe Mode| CM1
    VM --> |Agent Mode| AM1
    
    AM1 --> CD
    CD --> AM2
    AM2 --> AM3
    AM3 --> AL
    AL --> AM4
    AM4 --> AM5
    
    CM1 --> CM2
    CM2 --> CM3
    
    UI --> AC
    AC --> RL
    RL --> PT
    
    style CM1 fill:#90ee90
    style CM2 fill:#90ee90
    style CM3 fill:#90ee90
    style AM1 fill:#ff6b6b
    style AM2 fill:#ff6b6b
    style AM3 fill:#ff6b6b
```

## MCP Server Integration

```mermaid
graph LR
    subgraph "Smithery Registry"
        SR[Agent Registry]
        TA[Trading Agent]
        FA[Farmer Assistant]
    end
    
    subgraph "MCP Servers"
        TAS[trading-agent/index.js<br/>Port: 5001]
        FAS[farmer-assistant/index.js<br/>Port: 5002]
    end
    
    subgraph "Integration Points"
        ALPACA[Alpaca Trading API]
        CROSS[Crossmint Payments]
        CLAUDE[Claude AI]
    end
    
    subgraph "Backend Connection"
        MCP[mcp_connector.py]
        FARM[farmer_agent.py]
        ALP[alpaca_mcp_client.py]
    end
    
    SR --> TA
    SR --> FA
    TA --> TAS
    FA --> FAS
    
    TAS --> ALPACA
    FAS --> CROSS
    FAS --> CLAUDE
    
    MCP --> TAS
    MCP --> FAS
    FARM --> ALP
    ALP --> ALPACA
    
    style SR fill:#7f5af0
    style ALPACA fill:#00d4aa
    style CROSS fill:#ffd93d
    style CLAUDE fill:#7f5af0
```

## Database Schema

```mermaid
erDiagram
    USERS ||--o{ TRADES : places
    USERS ||--o{ SUBSIDIES : claims
    USERS ||--o{ POSITIONS : holds
    TRADES ||--|| WATER_FUTURES : involves
    
    USERS {
        uuid id PK
        string email
        string name
        decimal balance
        json preferences
        timestamp created_at
    }
    
    WATER_FUTURES {
        string contract_code PK
        string name
        decimal current_price
        decimal volume
        date expiry_date
        json metadata
    }
    
    TRADES {
        uuid id PK
        uuid user_id FK
        string contract_code FK
        string side
        int quantity
        decimal price
        string status
        string alpaca_order_id
        timestamp executed_at
    }
    
    POSITIONS {
        uuid id PK
        uuid user_id FK
        string contract_code FK
        int quantity
        decimal avg_price
        decimal current_value
        decimal unrealized_pl
        timestamp opened_at
    }
    
    SUBSIDIES {
        uuid id PK
        uuid user_id FK
        string type
        decimal amount
        string status
        string crossmint_payment_id
        json details
        timestamp processed_at
    }
    
    HISTORICAL_PRICES {
        uuid id PK
        string contract_code FK
        date date
        decimal open
        decimal high
        decimal low
        decimal close
        int volume
    }
    
    NEWS {
        uuid id PK
        string title
        string source
        string url
        text content
        decimal relevance_score
        decimal sentiment_score
        timestamp published_at
    }
    
    EMBEDDINGS {
        uuid id PK
        string content_type
        uuid content_id
        vector embedding
        json metadata
        timestamp created_at
    }
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        DEV[Local Development<br/>Docker Compose]
    end
    
    subgraph "Google Cloud Platform"
        CR[Cloud Run<br/>Backend API]
        FB[Firebase Hosting<br/>React Frontend]
        CS[Cloud SQL<br/>PostgreSQL]
        VA[Vertex AI<br/>ML Models]
        ST[Cloud Storage<br/>Data Files]
        SM[Secret Manager<br/>API Keys]
    end
    
    subgraph "External Services"
        GH[GitHub<br/>Source Code]
        GA[GitHub Actions<br/>CI/CD]
        SR[Smithery Registry<br/>MCP Servers]
        ALP[Alpaca Markets<br/>Trading API]
        CM[Crossmint<br/>Payments]
        AN[Anthropic<br/>Claude API]
    end
    
    DEV --> GH
    GH --> GA
    GA --> CR
    GA --> FB
    
    CR --> CS
    CR --> VA
    CR --> ST
    CR --> SM
    
    CR --> SR
    CR --> ALP
    CR --> CM
    CR --> AN
    
    FB --> CR
    
    style GH fill:#333
    style GA fill:#2088e0
    style CR fill:#4285f4
    style FB fill:#ffa000
    style CS fill:#4285f4
    style VA fill:#34a853
```

## Performance Metrics

```mermaid
graph LR
    subgraph "Monitoring Points"
        API[API Response Time<br/><100ms target]
        CHAT[Chat Response<br/><2s target]
        TRADE[Trade Execution<br/><500ms target]
        ML[ML Prediction<br/><3s target]
    end
    
    subgraph "Scalability"
        USERS[Concurrent Users<br/>1000+ target]
        TPS[Trades Per Second<br/>100+ target]
        MSG[Messages/Min<br/>1000+ target]
    end
    
    subgraph "Reliability"
        UP[Uptime<br/>99.9% target]
        FAIL[Failover Time<br/><30s target]
        REC[Recovery Time<br/><5min target]
    end
    
    API --> USERS
    CHAT --> MSG
    TRADE --> TPS
    ML --> USERS
    
    USERS --> UP
    TPS --> FAIL
    MSG --> REC
```

---

This architecture documentation provides a comprehensive view of the Water Futures AI platform, showing how all components interact, the security measures in place, and the flow of data through the system. The trade approval mechanism ensures users maintain control over all financial decisions while benefiting from AI-powered insights and automation.