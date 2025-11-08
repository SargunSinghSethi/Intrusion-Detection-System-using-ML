import os
import json
import google.generativeai as genai
from typing import Dict, Any

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD7sQe85tFm2cU9KR2sDedG5sEi0JSDEg4")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a cybersecurity expert analyzing network traffic data. Based on the model prediction results, generate a detailed threat analysis report.

Return a JSON object with the following structure:
{
  "threats": [
    {
      "id": 1,
      "type": "Threat Type Name",
      "severity": "High/Medium/Low",
      "description": "Detailed description",
      "confidence": 0.95,
      "sourceIP": "192.168.1.100",
      "destinationIP": "10.0.0.50",
      "port": 443
    }
  ],
  "summary": {
    "totalThreats": 3,
    "riskScore": 85,
    "recommendation": "Detailed recommendation text"
  }
}

Provide realistic and specific threat analysis based on the model output.
"""

def format_with_gemini(model_output: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """
    Send model output to Gemini and get formatted threat analysis
    """
    try:
        if not GEMINI_API_KEY:
            # Return dummy formatted response if no API key
            return generate_dummy_response(model_output, filename)
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Prepare prompt
        prompt = f"""
{SYSTEM_PROMPT}

File analyzed: {filename}
Model prediction: {json.dumps(model_output, indent=2)}

Generate the threat analysis report in JSON format.
"""
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Extract and clean response text
        response_text = response.text.strip()
        
        # Extract JSON if wrapped in Markdown code block
        if "```json" in response_text:
            json_start = response_text.find("```json") + len("```json")
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + len("```")
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        # Parse JSON
        result = json.loads(response_text)
        return result

    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return generate_dummy_response(model_output, filename)


def generate_dummy_response(model_output: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """Generate a dummy response based on model output"""
    threat_level = model_output.get("threat_level", "low")
    confidence = model_output.get("confidence", 0.5)
    prediction = model_output.get("prediction", "").lower()

    if threat_level == "high" or prediction == "malicious":
        severity = "High"
        threat_count = 3
        risk_score = 85
    elif threat_level == "medium" or prediction == "suspicious":
        severity = "Medium"
        threat_count = 2
        risk_score = 55
    else:
        severity = "Low"
        threat_count = 0
        risk_score = 15

    threats_list = []
    if threat_count > 0:
        threats_list.append({
            "id": 1,
            "type": "Suspicious Network Activity",
            "severity": severity,
            "description": f"Unusual network pattern detected in packet flow with {confidence:.0%} confidence.",
            "confidence": confidence,
            "sourceIP": "192.168.1.100",
            "destinationIP": "10.0.0.50",
            "port": 443
        })

        if threat_count >= 2:
            threats_list.append({
                "id": 2,
                "type": "Potential Malware Signature",
                "severity": severity,
                "description": "Detected patterns matching known malware behavior.",
                "confidence": round(confidence * 0.9, 2),
                "sourceIP": "192.168.1.105",
                "destinationIP": "203.0.113.42",
                "port": 8080
            })

        if threat_count >= 3:
            threats_list.append({
                "id": 3,
                "type": "Data Exfiltration Attempt",
                "severity": severity,
                "description": "Large data transfer to suspicious external IP.",
                "confidence": round(confidence * 0.85, 2),
                "sourceIP": "192.168.1.100",
                "destinationIP": "198.51.100.23",
                "port": 22
            })

    # Recommendation message
    if severity == "High":
        recommendation = (
            f"The analyzed file '{filename}' shows a HIGH risk level. "
            "Immediate action recommended — isolate affected systems and conduct a thorough investigation."
        )
    elif severity == "Medium":
        recommendation = (
            f"The analyzed file '{filename}' shows a MEDIUM risk level. "
            "Monitor for suspicious activity and review security logs."
        )
    else:
        recommendation = (
            f"The analyzed file '{filename}' shows a LOW risk level. "
            "No immediate action required — continue routine monitoring."
        )

    return {
        "threats": threats_list,
        "summary": {
            "totalThreats": threat_count,
            "riskScore": risk_score,
            "recommendation": recommendation
        }
    }
