(function (window) {
  "use strict";

  window.StockWiseDocs = {
    serviceName: "portfolio-service",
    projectSummary: "SRS-aligned documentation for the StockWise portfolio-service (Portfolio & Paper Trading module). Each requirement, use case, rule, and contract is documented from the project report and tagged with a simple implementation status.",
    authoringGuide: "",
    metrics: [
      "12 group pages",
      "22 child artifacts",
      "FR-PORTFOLIO-01..11",
      "Implementation status tags",
      "Source: StockWise SRS (Nhóm 21)"
    ],
    groups: [
      {
        id: "overview",
        title: "Overview",
        file: "groups/overview.html",
        eyebrow: "1 artifact",
        range: "Project scope",
        description: "StockWise context, portfolio module purpose, actors, tech stack, and capability status.",
        artifacts: [
          {
            eyebrow: "Overview",
            title: "Project Overview",
            description: "Portfolio & Paper Trading module purpose within StockWise, actors, tech stack, scope, and capability status.",
            href: "overview/project-overview.html",
            frameTitle: "Project Overview"
          }
        ]
      },
      {
        id: "functional-requirements",
        title: "Functional Requirements",
        file: "groups/functional-requirements.html",
        eyebrow: "1 artifact",
        range: "FR-PORTFOLIO-01 to 11",
        description: "Portfolio requirements with implementation status.",
        artifacts: [
          {
            eyebrow: "FR-PORTFOLIO-01..11",
            title: "Portfolio & Paper Trading Requirements",
            description: "The SRS functional requirement set for portfolios, orders, validation, PnL, and eventing, each tagged Implemented / Partial / Not implemented.",
            href: "srs/fr/portfolio-service/fr-portfolio-paper-trading.html",
            anchor: "FR-PORTFOLIO-01",
            frameTitle: "Functional Requirements Portfolio & Paper Trading"
          }
        ]
      },
      {
        id: "non-functional-requirements",
        title: "Non-Functional Requirements",
        file: "groups/non-functional-requirements.html",
        eyebrow: "1 artifact",
        range: "Performance, security, reliability",
        description: "System-wide NFRs that constrain the portfolio-service, with status.",
        artifacts: [
          {
            eyebrow: "NFR",
            title: "Portfolio Non-Functional Requirements",
            description: "Performance, security, reliability, scalability, portability, and usability NFRs from the SRS scoped to portfolio-service.",
            href: "srs/nfr/portfolio-service/nfr-portfolio.html",
            anchor: "NFR-REL-03",
            frameTitle: "Non-Functional Requirements Portfolio Service"
          }
        ]
      },
      {
        id: "use-cases",
        title: "Use Cases",
        file: "groups/use-cases.html",
        eyebrow: "4 artifacts",
        range: "UC-001 to UC-004",
        description: "View portfolio, place buy, place sell, and cancel order workflows.",
        artifacts: [
          {
            eyebrow: "UC-001",
            title: "View Portfolio Summary",
            description: "Read portfolio, holdings, transactions, and PnL for a user.",
            href: "use-cases/portfolio-service/uc-001-view-portfolio-summary.html",
            anchor: "UC-001",
            frameTitle: "UC-001 View Portfolio Summary"
          },
          {
            eyebrow: "UC-002",
            title: "Place Buy Order",
            description: "BUY order flow with validation, freeze, persist, and event.",
            href: "use-cases/portfolio-service/uc-002-place-buy-order.html",
            anchor: "UC-002",
            frameTitle: "UC-002 Place Buy Order"
          },
          {
            eyebrow: "UC-003",
            title: "Place Sell Order",
            description: "SELL order flow with holding checks and share locking.",
            href: "use-cases/portfolio-service/uc-003-place-sell-order.html",
            anchor: "UC-003",
            frameTitle: "UC-003 Place Sell Order"
          },
          {
            eyebrow: "UC-004",
            title: "Cancel Order",
            description: "Cancellation of a PENDING order with asset release.",
            href: "use-cases/portfolio-service/uc-004-cancel-order.html",
            anchor: "UC-004",
            frameTitle: "UC-004 Cancel Order"
          }
        ]
      },
      {
        id: "business-flows",
        title: "Business Flows",
        file: "groups/business-flows.html",
        eyebrow: "1 artifact",
        range: "BFLOW-001",
        description: "End-to-end order lifecycle across place, match, fill, and cancel.",
        artifacts: [
          {
            eyebrow: "BFLOW-001",
            title: "Order Lifecycle",
            description: "Place to PENDING to FILLED or CANCELLED flow with validation, asset freeze/release, and events across portfolio-service, market-service, and RabbitMQ.",
            href: "business-flows/portfolio-service/bflow-order-lifecycle.html",
            anchor: "BFLOW-001",
            frameTitle: "BFLOW-001 Order Lifecycle"
          }
        ]
      },
      {
        id: "business-rules",
        title: "Business Rules",
        file: "groups/business-rules.html",
        eyebrow: "1 artifact",
        range: "BR-001, BR-002, BR-009, BR-100..105",
        description: "Order/portfolio rules and data constraints with status.",
        artifacts: [
          {
            eyebrow: "Business rules",
            title: "Portfolio Business Rules",
            description: "Order validation (price band, funds, holdings, market hours, ownership) and data constraints.",
            href: "business-rules/portfolio-service/br-order-validation.html",
            anchor: "BR-100",
            frameTitle: "Business Rules Portfolio"
          }
        ]
      },
      {
        id: "data-models",
        title: "Data Models",
        file: "groups/data-models.html",
        eyebrow: "4 artifacts",
        range: "ENTITY-001 to ENTITY-004",
        description: "Portfolio, Holding, Transaction entities and the Order lifecycle.",
        artifacts: [
          {
            eyebrow: "ENTITY-001",
            title: "Portfolio",
            description: "JPA portfolio entity with user ownership and virtual cash.",
            href: "data-models/portfolio-service/entity-portfolio.html",
            anchor: "ENTITY-001",
            frameTitle: "Entity Portfolio"
          },
          {
            eyebrow: "ENTITY-002",
            title: "Holding",
            description: "JPA holding entity with portfolio, symbol, quantity, and average price.",
            href: "data-models/portfolio-service/entity-holding.html",
            anchor: "ENTITY-002",
            frameTitle: "Entity Holding"
          },
          {
            eyebrow: "ENTITY-003",
            title: "Order",
            description: "Order entity with a PENDING/FILLED/CANCELLED lifecycle.",
            href: "data-models/portfolio-service/entity-order.html",
            anchor: "ENTITY-003",
            frameTitle: "Entity Order"
          },
          {
            eyebrow: "ENTITY-004",
            title: "Transaction",
            description: "Append-only JPA transaction entity for executed orders.",
            href: "data-models/portfolio-service/entity-transaction.html",
            anchor: "ENTITY-004",
            frameTitle: "Entity Transaction"
          }
        ]
      },
      {
        id: "api-contracts",
        title: "API Contracts",
        file: "groups/api-contracts.html",
        eyebrow: "4 artifacts",
        range: "API-001 to API-004",
        description: "Portfolio, order, PnL, and cancel endpoints.",
        artifacts: [
          {
            eyebrow: "API-001",
            title: "GET /portfolio",
            description: "Returns portfolio, holdings, and transactions for a supplied user UUID.",
            href: "api-contracts/portfolio-service/api-get-portfolio.html",
            anchor: "API-001",
            frameTitle: "API-001 GET Portfolio"
          },
          {
            eyebrow: "API-002",
            title: "POST /portfolio/order",
            description: "Place a BUY/SELL order.",
            href: "api-contracts/portfolio-service/api-post-portfolio-order.html",
            anchor: "API-002",
            frameTitle: "API-002 POST Portfolio Order"
          },
          {
            eyebrow: "API-003",
            title: "DELETE /portfolio/order/{orderId}",
            description: "Order-cancellation endpoint.",
            href: "api-contracts/portfolio-service/api-delete-portfolio-order.html",
            anchor: "API-003",
            frameTitle: "API-003 DELETE Portfolio Order"
          },
          {
            eyebrow: "API-004",
            title: "GET /portfolio/pnl",
            description: "Returns the total PnL for a supplied user UUID.",
            href: "api-contracts/portfolio-service/api-get-portfolio-pnl.html",
            anchor: "API-004",
            frameTitle: "API-004 GET Portfolio PnL"
          }
        ]
      },
      {
        id: "messaging-contracts",
        title: "Messaging Contracts",
        file: "groups/messaging-contracts.html",
        eyebrow: "2 artifacts",
        range: "MSG-001 to MSG-002",
        description: "RabbitMQ price-update consumer and the portfolio transaction event.",
        artifacts: [
          {
            eyebrow: "MSG-001",
            title: "Market Price Updated",
            description: "Topic event on market.exchange / price.updated consumed by portfolio_service_price_q.",
            href: "messaging/portfolio-service/event-price-updated.html",
            anchor: "MSG-001",
            frameTitle: "MSG-001 Market Price Updated"
          },
          {
            eyebrow: "MSG-002",
            title: "Portfolio Transaction Event",
            description: "Outbound event published after each transaction (FR-PORTFOLIO-10).",
            href: "messaging/portfolio-service/event-reply-status.html",
            anchor: "MSG-002",
            frameTitle: "MSG-002 Portfolio Transaction Event"
          }
        ]
      },
      {
        id: "glossary",
        title: "Glossary",
        file: "groups/glossary.html",
        eyebrow: "1 artifact",
        range: "Domain terms",
        description: "Portfolio and paper-trading terms from the StockWise SRS glossary.",
        artifacts: [
          {
            eyebrow: "Glossary",
            title: "Portfolio Glossary",
            description: "Definitions for paper trading, PnL, portfolio, holding, order, transaction, and related terms.",
            href: "glossary/portfolio-service/glossary.html",
            frameTitle: "Portfolio Glossary"
          }
        ]
      },
      {
        id: "deployment",
        title: "Deployment",
        file: "groups/deployment.html",
        eyebrow: "1 artifact",
        range: "Runtime",
        description: "Build, runtime, ports, environment variables, dependencies, and service wiring.",
        artifacts: [
          {
            eyebrow: "Runtime",
            title: "Portfolio Service Runtime",
            description: "Spring Boot, Java, Maven, Docker, PostgreSQL, RabbitMQ, actuator, and local Docker Compose details.",
            href: "deployment/portfolio-service/deployment-runtime.html",
            frameTitle: "Deployment Portfolio Service Runtime"
          }
        ]
      },
      {
        id: "traceability",
        title: "Traceability",
        file: "groups/traceability.html",
        eyebrow: "1 artifact",
        range: "Coverage matrix",
        description: "Requirement-to-artifact coverage with implementation status.",
        artifacts: [
          {
            eyebrow: "Coverage matrix",
            title: "Traceability Matrix",
            description: "FR/UC/API/BR/Entity/NFR coverage with Implemented / Partial / Not-implemented status across the portfolio module.",
            href: "traceability/portfolio-service/traceability-matrix.html",
            frameTitle: "Traceability Matrix"
          }
        ]
      }
    ]
  };
})(window);
