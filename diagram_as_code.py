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

# Define some styling constants
DIAGRAM_ATTRS = {
    "pad": "2.0",
    "splines": "ortho",  
    "nodesep": "1.5",    
    "ranksep": "1.8",    
    "fontsize": "45",    
    "fontname": "Arial"
}

CLUSTER_ATTRS = {
    "margin": "30",
    "fontsize": "13",
    "fontname": "Arial",
    "style": "rounded",  # Rounded corners for clusters
    "penwidth": "2.0"    
}

EDGE_ATTRS = {
    "fontsize": "11",
    "fontname": "Arial",
    "penwidth": "2.0"    
}

with Diagram(
    "Trading System Architecture",
    show=False,
    direction="LR",      # Left to right layout
    graph_attr=DIAGRAM_ATTRS,
    edge_attr=EDGE_ATTRS
) as diag:
    
    # Client Layer
    with Cluster("Client Layer", graph_attr=CLUSTER_ATTRS):
        client = Client("Trading Clients\n(Web/Mobile)")

    # API Layer
    with Cluster("API Layer", graph_attr=CLUSTER_ATTRS):
        apigateway = APIGateway("API Gateway")

    # Order Processing Layer
    with Cluster("Order Processing", graph_attr=CLUSTER_ATTRS):
        order_ingestion = Lambda("Order Ingestion")
        
        with Cluster("Message Queue"):
            order_queues = [
                MSK("order-requests"),
                MSK("validated-orders"),
                MSK("matched-events"),
                MSK("trade-execution")
            ]

    # Core Trading Layer
    with Cluster("Trading Engine (EKS)", graph_attr=CLUSTER_ATTRS):
        with Cluster("Trading Services"):
            trading_services = [
                EKS("Order Processor"),
                EKS("Matching Engine"),
                EKS("Market Data")
            ]

    # Data Layer
    with Cluster("Data Storage & Processing", graph_attr=CLUSTER_ATTRS):
        databases = [
            Aurora("Orders DB"),
            Aurora("Users DB"),
            ElastiCache("Order Cache")
        ]
        
        data_pipeline = [
            Kinesis("Data Stream"),
            S3("Data Lake"),
            Athena("Analytics")
        ]

    # Monitoring Layer
    with Cluster("Observability", graph_attr=CLUSTER_ATTRS):
        monitoring = [
            Cloudwatch("Metrics & Logs"),
            XRay("Tracing")
        ]

    # Draw main flow connections
    client >> Edge(label="1. Submit Order", color="blue") >> apigateway
    apigateway >> Edge(label="2. Process", color="blue") >> order_ingestion
    order_ingestion >> Edge(label="3. Queue", color="blue") >> order_queues[0]
    
    # Order processing flow
    order_queues[0] >> Edge(label="4. Validate", color="green") >> trading_services[0]
    trading_services[0] >> Edge(label="5. Store", color="green") >> databases[0]
    trading_services[0] >> Edge(label="6. Cache", color="green") >> databases[2]
    
    # Trading flow
    trading_services[0] >> Edge(label="7. Match", color="orange") >> trading_services[1]
    trading_services[1] >> Edge(label="8. Execute", color="orange") >> order_queues[2]
    
    # Market data flow
    order_queues[2] >> Edge(label="9. Update", color="purple") >> trading_services[2]
    trading_services[2] >> Edge(label="10. Stream", color="purple") >> apigateway
    
    # Data pipeline
    order_queues[3] >> Edge(label="11. Archive", color="red") >> data_pipeline[0]
    data_pipeline[0] >> data_pipeline[1] >> data_pipeline[2]
    
    # Monitoring connections (simplified)
    [apigateway, order_ingestion, trading_services[0]] >> monitoring[0]
    [apigateway, order_ingestion, trading_services[0]] >> monitoring[1]