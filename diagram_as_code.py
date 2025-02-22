#######################################
# THIS CODE IS ONLY FOR EXPERIMENT
#######################################
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.compute import EKS
from diagrams.aws.database import Aurora, ElastiCache
from diagrams.aws.network import APIGateway
from diagrams.aws.analytics import Kinesis
from diagrams.aws.storage import S3
from diagrams.aws.analytics import Athena
from diagrams.aws.management import Cloudwatch
from diagrams.aws.devtools import XRay
from diagrams.aws.analytics import ManagedStreamingForKafka as MSK
from diagrams.aws.general import Client

with Diagram("Trading System Architecture", show=False, graph_attr={"nodesep":"1.2", "ranksep":"1.2"}) as diag: # Increased node and rank separation
    # Single, General Client
    client = Client("Clients (Web/Mobile)")  # Combined client

    with Cluster("Network", graph_attr={"margin":"2.0"}): # Increased margin for network components
        apigateway = APIGateway("API Gateway")

    with Cluster("Order Ingestion", graph_attr={"margin":"2.0"}): # Increased margin for order ingestion
        order_ingestion = Lambda("Lambda (Order Ingestion)")

    with Cluster("Message Queue (MSK)", graph_attr={"margin":"2.0"}): # Increased margin for MSK
        order_stream = MSK("MSK (order-requests)")
        validated_orders = MSK("validated-orders")
        matching_events = MSK("matched-events")
        trade_execution = MSK("trade-execution")

    with Cluster("EKS Cluster", graph_attr={"margin":"2.0"}): # Increased margin for EKS cluster
        with Cluster("Order Processing"):
            order_processor = EKS("Order Processor (Pod)")
        with Cluster("Matching Engine"):
            matcher = EKS("Matcher (Pod)")
        with Cluster("Market Data Service"):
            market_data = EKS("MarketData (Pod)")

    with Cluster("Data Storage", graph_attr={"margin":"2.0"}): # Increased margin for data storage
        orders_db = Aurora("Aurora (Orders)")
        users_db = Aurora("Aurora (Users) Account")
        elasticache = ElastiCache("ElastiCache")
        kinesis = Kinesis("Kinesis Data Stream")
        s3 = S3("S3 Bucket")
        glue = Athena("Glue")

    with Cluster("Monitoring & Tracing", graph_attr={"margin":"2.0"}): # Increased margin for monitoring
        cloudwatch = Cloudwatch("Cloudwatch")
        xray = XRay("X-Ray")

    # Connections (Simplified with annotations and explicit directions)
    client >> apigateway << Edge(label="1. HTTPS/Websocket", style="->")  # Explicit direction
    apigateway >> order_ingestion << Edge(label="2. X-Ray request tracing initialization", style="->")
    order_ingestion >> order_stream << Edge(label="3. Order Ingestion", style="->")

    order_stream >> order_processor << Edge(label="4. Order Received", style="->")

    order_processor >> orders_db << Edge(label="5a. 1st DUAL WRITE", style="->")
    order_processor >> users_db << Edge(label="5b. Verify user's balance", style="->")
    order_processor >> elasticache << Edge(label="5c. 2nd DUAL WRITE", style="->")
    order_processor >> validated_orders << Edge(label="6. Publish validated order", style="->")

    validated_orders >> matcher << Edge(label="7. Order Matching", style="->")

    matcher >> matching_events << Edge(label="8a. Matching Events", style="->")
    matcher >> trade_execution << Edge(label="8b. Trade Execution", style="->")

    matching_events >> market_data << Edge(label="9a. Market Data Updates (Matched Events)", style="->")
    trade_execution >> market_data << Edge(label="9b. Market Data Updates (Trade Execution)", style="->")
    market_data >> apigateway << Edge(label="9c. WebSocket connection", style="->")

    trade_execution >> kinesis << Edge(label="10a. Trade Execution Stream", style="->")
    kinesis >> s3 << Edge(label="10b. Data Storage", style="->")
    s3 >> glue << Edge(label="10c. Data Processing", style="->")

    apigateway >> cloudwatch << Edge(label="11a. Logs & Metrics", style="->")
    order_ingestion >> cloudwatch << Edge(style="->")  # Added direction
    order_processor >> cloudwatch << Edge(style="->")  # Added direction
    matcher >> cloudwatch << Edge(style="->")  # Added direction
    market_data >> cloudwatch << Edge(style="->")  # Added direction
    kinesis >> cloudwatch << Edge(style="->")  # Added direction
    s3 >> cloudwatch << Edge(style="->")  # Added direction

    apigateway >> xray << Edge(label="11b. X-Ray requests tracing", style="->")
    order_ingestion >> xray << Edge(style="->")  # Added direction
    order_processor >> xray << Edge(style="->")  # Added direction
    matcher >> xray << Edge(style="->")  # Added direction
    market_data >> xray << Edge(style="->")  # Added direction
    kinesis >> xray << Edge(style="->")  # Added direction

    # Workflow Steps (using Subgraphs/Clusters with Labels - Simplified and Numbered)
    with Cluster("Workflow Steps", direction="LR", graph_attr={"nodesep":"1.0", "ranksep":"1.0"}): # Increased node and rank separation for workflow steps
        with Cluster("1. User Submits Order"):
            client >> apigateway

        with Cluster("2. Order Ingestion & Validation"):
            apigateway >> order_ingestion
            order_ingestion >> order_stream

        with Cluster("3. Order Processing"):
            order_stream >> order_processor

        with Cluster("4. Matching & Trade Execution"):
            validated_orders >> matcher
            matcher >> matching_events
            matcher >> trade_execution

        with Cluster("5. Market Data Updates"):
            matching_events >> market_data
            trade_execution >> market_data
            market_data >> apigateway

        with Cluster("6. Data Streaming & Storage"):
            trade_execution >> kinesis
            kinesis >> s3
            s3 >> glue

        with Cluster("7. Monitoring & Tracing"):
            apigateway >> cloudwatch
            order_ingestion >> cloudwatch
            order_processor >> cloudwatch
            matcher >> cloudwatch
            market_data >> cloudwatch
            kinesis >> cloudwatch
            s3 >> cloudwatch

            apigateway >> xray
            order_ingestion >> xray
            order_processor >> xray
            matcher >> xray
            market_data >> xray
            kinesis >> xray