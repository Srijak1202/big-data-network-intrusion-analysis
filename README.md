# Network Intrusion Detection with Apache Spark

## 1. Project Overview

This project implements a Network Intrusion Detection application using the NSL-KDD benchmark dataset, Apache Spark, and PySpark MLlib. It combines distributed data analytics, machine learning, and a web interface to analyze network traffic and classify potential intrusions.

## 2. System Architecture

- Dataset: NSL-KDD benchmark dataset.
- Data Analytics: Apache Spark for distributed processing and analytics.
- Machine Learning: PySpark MLlib for binary and five-class classification.
- Backend: FastAPI provides prediction and analytics APIs.
- Frontend: React provides the dashboard, intrusion detection interface, visualizations, and model evaluation pages.
- Prediction History: Currently stored using local JSON fallback storage. MongoDB integration has not been completed or verified.

## 3. Machine Learning Models

The application supports two classification tasks:

1. Binary classification: Normal traffic versus attack traffic.
2. Five-class classification: Normal, DoS, Probe, R2L, and U2R.

The models were evaluated using the NSL-KDD benchmark test dataset.

| Model | Held-out test accuracy |
|---|---:|
| Binary detection | 79.56% |
| Five-class detection | 74.05% |

The application includes model evaluation metrics, confusion matrices, feature importance, and precomputed analytics visualizations.

## 4. Technology Stack

- Python
- Apache Spark and PySpark MLlib
- FastAPI
- React
- JavaScript
- NSL-KDD dataset

## 5. Running the Application

### Prerequisites

Ensure that Python, Node.js, and the Spark environment required by the project are configured.

Install the project's required dependencies before starting the application.

### Start the application

From the project root directory, run:

```bash
chmod +x run_app.sh
./run_app.sh
