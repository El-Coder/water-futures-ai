"""
Script to train and deploy water futures model on Vertex AI
Run this once to set up the model
"""
import asyncio
from google.cloud import aiplatform
from google.cloud import storage
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set GCP project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/service-account-key.json"  # Update this
PROJECT_ID = "water-futures-ai"
REGION = "us-central1"
BUCKET_NAME = "water-futures-data"

def create_sample_training_data():
    """Create sample training data for the hackathon"""
    dates = pd.date_range(start='2023-01-01', end='2024-12-01', freq='D')
    
    data = []
    for date in dates:
        # Simulate seasonal patterns and drought impact
        base_price = 500
        seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * date.dayofyear / 365)
        drought_severity = 3 + np.random.random() * 2  # 3-5 severity
        drought_impact = 1 + (drought_severity - 3) * 0.02
        noise = np.random.normal(0, 5)
        
        price = base_price * seasonal_factor * drought_impact + noise
        
        data.append({
            'date': date,
            'contract_code': 'NQH25',
            'price': price,
            'volume': np.random.randint(800, 1500),
            'drought_severity': drought_severity,
            'precipitation': max(0, 50 - drought_severity * 10 + np.random.normal(0, 10)),
            'region': 'Central Valley'
        })
    
    df = pd.DataFrame(data)
    return df

def upload_to_gcs(df, filename):
    """Upload DataFrame to Google Cloud Storage"""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    
    # Save to CSV
    csv_data = df.to_csv(index=False)
    blob = bucket.blob(filename)
    blob.upload_from_string(csv_data)
    
    print(f"Uploaded {filename} to gs://{BUCKET_NAME}/{filename}")
    return f"gs://{BUCKET_NAME}/{filename}"

async def train_custom_model():
    """Train a custom TensorFlow model on Vertex AI"""
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Create training data
    print("Creating sample training data...")
    df = create_sample_training_data()
    
    # Upload to GCS
    print("Uploading data to Google Cloud Storage...")
    try:
        # Create bucket if it doesn't exist
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        if not bucket.exists():
            bucket = storage_client.create_bucket(BUCKET_NAME, location=REGION)
            print(f"Created bucket {BUCKET_NAME}")
    except Exception as e:
        print(f"Bucket creation error (may already exist): {e}")
    
    gcs_path = upload_to_gcs(df, "training_data.csv")
    
    # For hackathon, we'll use a pre-built container with a simple model
    # In production, you'd have a custom training script
    
    print("Creating Vertex AI dataset...")
    dataset = aiplatform.TabularDataset.create(
        display_name="water-futures-dataset",
        gcs_source=gcs_path,
    )
    
    print("Training AutoML model...")
    # Use AutoML for simplicity in hackathon
    job = aiplatform.AutoMLTabularTrainingJob(
        display_name="water-futures-forecast",
        optimization_prediction_type="regression",
        optimization_objective="minimize-rmse",
    )
    
    model = job.run(
        dataset=dataset,
        target_column="price",
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        predefined_split_column_name=None,
        timestamp_split_column_name=None,
        weight_column=None,
        budget_milli_node_hours=1000,  # Minimum budget for AutoML
        model_display_name="water-futures-model",
        disable_early_stopping=False,
    )
    
    print("Deploying model to endpoint...")
    endpoint = model.deploy(
        deployed_model_display_name="water-futures-endpoint",
        machine_type="n1-standard-4",
        min_replica_count=1,
        max_replica_count=1,
        traffic_percentage=100,
        sync=True,
    )
    
    print(f"Model deployed to endpoint: {endpoint.resource_name}")
    print(f"Endpoint ID: {endpoint.name}")
    
    # Test prediction
    test_instance = {
        "drought_severity": 4.0,
        "precipitation": 30.0,
        "volume": 1200,
        "region": "Central Valley"
    }
    
    prediction = endpoint.predict([test_instance])
    print(f"Test prediction: {prediction}")
    
    return endpoint

def create_simple_sklearn_model():
    """Alternative: Create a simple scikit-learn model for quick deployment"""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    import joblib
    
    # Create training data
    df = create_sample_training_data()
    
    # Prepare features
    X = df[['drought_severity', 'precipitation', 'volume']].values
    y = df['price'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save model
    joblib.dump(model, 'water_futures_model.pkl')
    print("Saved sklearn model to water_futures_model.pkl")
    
    # Test prediction
    test_score = model.score(X_test, y_test)
    print(f"Model R2 score: {test_score}")
    
    return model

if __name__ == "__main__":
    print("Water Futures Model Training Script")
    print("====================================")
    
    # For hackathon, use simple sklearn model
    print("\nOption 1: Creating simple sklearn model (recommended for hackathon)...")
    create_simple_sklearn_model()
    
    print("\nOption 2: To train on Vertex AI (requires GCP setup):")
    print("Uncomment the line below and run:")
    # asyncio.run(train_custom_model())
    
    print("\nModel training complete!")
    print("\nTo use Vertex AI in production:")
    print("1. Set up service account credentials")
    print("2. Update GOOGLE_APPLICATION_CREDENTIALS path")
    print("3. Run: python train_model.py")
    print("4. Update VERTEX_ENDPOINT_NAME in your .env file with the endpoint ID")