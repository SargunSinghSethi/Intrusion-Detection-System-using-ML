import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any


def load_model(model_path: str):
    """Load joblib model with error handling."""
    try:
        print(f"📦 Loading model from {model_path} ...")
        model = joblib.load(model_path)
        print("✅ Model loaded successfully.")
        return model
    except Exception as e:
        print(f"⚠️ Error loading model: {e}")
        return None


def predict_from_csv(csv_path: str, model_path: str, scaler_path: str, is_multiclass: bool = False) -> Dict[str, Any]:
    """
    Runs model inference on the given CSV with support for both binary and multi-class classification.
    
    Args:
        csv_path: Path to input CSV file (must have all 78 features)
        model_path: Path to trained model (.joblib)
        scaler_path: Path to fitted scaler (.joblib)
        is_multiclass: If True, performs multi-class classification (15 classes)
                      If False, performs binary classification (BENIGN vs ATTACK)
    
    Returns:
        Dictionary containing predictions, confidence scores, and analysis results
    """
    
    # Multi-class label mapping (matching your training data)
    MULTICLASS_LABELS = {
        0: "BENIGN",
        1: "Bot",
        2: "DDoS",
        3: "DoS GoldenEye",
        4: "DoS Hulk",
        5: "DoS Slowhttptest",
        6: "DoS slowloris",
        7: "FTP-Patator",
        8: "Heartbleed",
        9: "Infiltration",
        10: "PortScan",
        11: "SSH-Patator",
        12: "Web Attack – Brute Force",
        13: "Web Attack – Sql Injection",
        14: "Web Attack – XSS"
    }
    
    # ALL 78 features in EXACT order expected by the model
    ALL_78_FEATURES = [
        "Destination Port", "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
        "Total Length of Fwd Packets", "Total Length of Bwd Packets", "Fwd Packet Length Max",
        "Fwd Packet Length Min", "Fwd Packet Length Mean", "Fwd Packet Length Std",
        "Bwd Packet Length Max", "Bwd Packet Length Min", "Bwd Packet Length Mean",
        "Bwd Packet Length Std", "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean",
        "Flow IAT Std", "Flow IAT Max", "Flow IAT Min", "Fwd IAT Total", "Fwd IAT Mean",
        "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min", "Bwd IAT Total", "Bwd IAT Mean",
        "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min", "Fwd PSH Flags", "Bwd PSH Flags",
        "Fwd URG Flags", "Bwd URG Flags", "Fwd Header Length", "Bwd Header Length",
        "Fwd Packets/s", "Bwd Packets/s", "Min Packet Length", "Max Packet Length",
        "Packet Length Mean", "Packet Length Std", "Packet Length Variance",
        "FIN Flag Count", "SYN Flag Count", "RST Flag Count", "PSH Flag Count",
        "ACK Flag Count", "URG Flag Count", "CWE Flag Count", "ECE Flag Count",
        "Down/Up Ratio", "Average Packet Size", "Avg Fwd Segment Size",
        "Avg Bwd Segment Size", "Fwd Header Length.1", "Fwd Avg Bytes/Bulk",
        "Fwd Avg Packets/Bulk", "Fwd Avg Bulk Rate", "Bwd Avg Bytes/Bulk",
        "Bwd Avg Packets/Bulk", "Bwd Avg Bulk Rate", "Subflow Fwd Packets",
        "Subflow Fwd Bytes", "Subflow Bwd Packets", "Subflow Bwd Bytes",
        "Init_Win_bytes_forward", "Init_Win_bytes_backward", "act_data_pkt_fwd",
        "min_seg_size_forward", "Active Mean", "Active Std", "Active Max",
        "Active Min", "Idle Mean", "Idle Std", "Idle Max", "Idle Min"
    ]

    try:
        # Load model and scaler
        model = load_model(model_path)
        if model is None:
            raise ValueError("Model could not be loaded.")
        
        scaler = joblib.load(scaler_path)
        print(f"✓ Loaded scaler from {os.path.basename(scaler_path)}")

        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} samples from {os.path.basename(csv_path)}")

        # Ensure only numeric features
        df_numeric = df.select_dtypes(include=['number']).fillna(0)
        if df_numeric.empty:
            raise ValueError("No numeric columns found in CSV for prediction.")

        # Check for missing features
        csv_features = df_numeric.columns.tolist()
        missing_features = [f for f in ALL_78_FEATURES if f not in csv_features]
        
        # if missing_features:
        #     raise ValueError(f"CSV is missing required features: {missing_features}... (showing first 10)")
        
        # Select ALL 78 features in EXACT order
        df_aligned = df_numeric[ALL_78_FEATURES]
        
        print("🔧 Preprocessing data with all 78 features...")
        df_scaled = scaler.transform(df_aligned)

        # Predict
        classification_type = "Multi-class" if is_multiclass else "Binary"
        print(f"🔍 Evaluating {classification_type} classification...")
        predictions = model.predict(df_scaled)

        # Calculate confidence
        if hasattr(model, "predict_proba"):
            confidences = model.predict_proba(df_scaled)
            avg_confidence = float(np.mean(np.max(confidences, axis=1)))
        else:
            avg_confidence = 0.8  # fallback

        # Analyze results
        if is_multiclass:
            # Multi-class analysis
            unique_preds, counts = np.unique(predictions, return_counts=True)
            pred_distribution = {
                MULTICLASS_LABELS.get(int(pred), f"Unknown-{pred}"): int(count)
                for pred, count in zip(unique_preds, counts)
            }
            
            benign_count = pred_distribution.get("BENIGN", 0)
            attack_count = len(df) - benign_count
            
            benign_ratio = benign_count / len(df)
            anomaly_ratio = attack_count / len(df)
            
            overall_pred = "benign" if benign_ratio > 0.8 else "malicious"
            threat_level = "low" if overall_pred == "benign" else "high"
            
            result = {
                "classification_type": "multi-class",
                "total_samples": len(df),
                "avg_confidence": round(avg_confidence, 3),
                "benign_ratio": float(round(benign_ratio, 3)),
                "anomaly_ratio": float(round(anomaly_ratio, 3)),
                "prediction_distribution": pred_distribution,
                "prediction": overall_pred,
                "threat_level": threat_level,
                "top_attack_types": sorted(
                    [(k, v) for k, v in pred_distribution.items() if k != "BENIGN"],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            }
            
        else:
            # Binary analysis
            benign_ratio = (predictions == 0).mean()  # 0 = BENIGN
            anomaly_ratio = (predictions == 1).mean()  # 1 = ATTACK
            
            overall_pred = "benign" if benign_ratio > 0.8 else "malicious"
            threat_level = "low" if overall_pred == "benign" else "high"
            
            result = {
                "classification_type": "binary",
                "total_samples": len(df),
                "avg_confidence": round(avg_confidence, 3),
                "benign_ratio": float(round(benign_ratio, 3)),
                "anomaly_ratio": float(round(anomaly_ratio, 3)),
                "prediction": overall_pred,
                "threat_level": threat_level,
            }

        print("✅ Final Result Summary")
        print(result)
        return result

    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        return {"error": str(e)}
