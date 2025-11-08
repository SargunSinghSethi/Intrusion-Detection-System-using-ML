import os
import pandas as pd
import numpy as np
from scapy.all import *
from tqdm import tqdm
from collections import defaultdict

def convert_pcap_to_csv(pcap_path: str, output_dir: str) -> str:
    """
    Convert a PCAP file into a detailed flow-based CSV with all 78 CICIDS-style features.
    """

    if not os.path.exists(pcap_path):
        raise FileNotFoundError(f"PCAP file not found: {pcap_path}")

    print(f"📥 Reading packets from {pcap_path} ...")
    packets = rdpcap(pcap_path)

    flows = defaultdict(list)

    def get_flow_key(pkt):
        if IP in pkt:
            proto = pkt[IP].proto
            if TCP in pkt or UDP in pkt:
                sport = pkt.sport
                dport = pkt.dport
            else:
                sport = dport = 0
            return (pkt[IP].src, pkt[IP].dst, sport, dport, proto)
        return None

    for pkt in tqdm(packets, desc="Processing packets"):
        key = get_flow_key(pkt)
        if key:
            flows[key].append(pkt)

    def safe_mean(arr): return float(np.mean(arr)) if len(arr) > 0 else 0.0
    def safe_std(arr): return float(np.std(arr)) if len(arr) > 1 else 0.0
    def safe_var(arr): return float(np.var(arr)) if len(arr) > 1 else 0.0

    flow_features = []

    for key, pkts in tqdm(flows.items(), desc="Computing flow features"):
        src, dst, sport, dport, proto = key
        pkts = sorted(pkts, key=lambda x: x.time)
        times = np.array([float(p.time) for p in pkts])
        lengths = np.array([len(p) for p in pkts])
        fwd_pkts = [p for p in pkts if p[IP].src == src]
        bwd_pkts = [p for p in pkts if p[IP].src == dst]

        # Flow duration
        flow_duration = (times[-1] - times[0]) if len(times) > 1 else 0.0

        # IATs
        flow_iats = np.diff(times) if len(times) > 1 else [0]
        flow_iat_mean, flow_iat_std, flow_iat_max, flow_iat_min = safe_mean(flow_iats), safe_std(flow_iats), max(flow_iats), min(flow_iats)

        # Forward/Backward IATs
        def get_iats(pkts):
            t = [float(p.time) for p in pkts]
            return np.diff(sorted(t)) if len(t) > 1 else [0]

        fwd_iats = get_iats(fwd_pkts)
        bwd_iats = get_iats(bwd_pkts)

        fwd_iat_total, fwd_iat_mean, fwd_iat_std, fwd_iat_max, fwd_iat_min = sum(fwd_iats), safe_mean(fwd_iats), safe_std(fwd_iats), max(fwd_iats), min(fwd_iats)
        bwd_iat_total, bwd_iat_mean, bwd_iat_std, bwd_iat_max, bwd_iat_min = sum(bwd_iats), safe_mean(bwd_iats), safe_std(bwd_iats), max(bwd_iats), min(bwd_iats)

        # Flags
        fin=syn=rst=psh=ack=urg=cwe=ece=0
        fwd_psh=bwd_psh=fwd_urg=bwd_urg=0
        fwd_hdr_len=bwd_hdr_len=0

        for p in pkts:
            if TCP in p:
                flags = p[TCP].flags
                fin += bool(flags & 0x01)
                syn += bool(flags & 0x02)
                rst += bool(flags & 0x04)
                psh += bool(flags & 0x08)
                ack += bool(flags & 0x10)
                urg += bool(flags & 0x20)
                ece += bool(flags & 0x40)
                cwe += bool(flags & 0x80)

                if p[IP].src == src:
                    fwd_hdr_len += p[TCP].dataofs * 4
                    fwd_psh += bool(flags & 0x08)
                    fwd_urg += bool(flags & 0x20)
                else:
                    bwd_hdr_len += p[TCP].dataofs * 4
                    bwd_psh += bool(flags & 0x08)
                    bwd_urg += bool(flags & 0x20)

        # Lengths
        fwd_lens = [len(p) for p in fwd_pkts] or [0]
        bwd_lens = [len(p) for p in bwd_pkts] or [0]

        # Basic features
        total_fwd_pkts, total_bwd_pkts = len(fwd_pkts), len(bwd_pkts)
        total_len_fwd, total_len_bwd = sum(fwd_lens), sum(bwd_lens)
        total_pkts = total_fwd_pkts + total_bwd_pkts
        total_len = total_len_fwd + total_len_bwd

        min_pkt_len, max_pkt_len = min(lengths), max(lengths)
        pkt_len_mean, pkt_len_std, pkt_len_var = safe_mean(lengths), safe_std(lengths), safe_var(lengths)

        # Rates
        flow_bytes_per_s = total_len / flow_duration if flow_duration > 0 else 0
        flow_pkts_per_s = total_pkts / flow_duration if flow_duration > 0 else 0
        fwd_pkts_per_s = total_fwd_pkts / flow_duration if flow_duration > 0 else 0
        bwd_pkts_per_s = total_bwd_pkts / flow_duration if flow_duration > 0 else 0

        # Derived
        down_up_ratio = (total_bwd_pkts / total_fwd_pkts) if total_fwd_pkts > 0 else 0
        avg_pkt_size = total_len / total_pkts if total_pkts > 0 else 0
        avg_fwd_seg_size = safe_mean(fwd_lens)
        avg_bwd_seg_size = safe_mean(bwd_lens)

        # Active / Idle Times
        actives, idles = [], []
        if len(times) > 1:
            diffs = np.diff(times)
            threshold = np.mean(diffs) + np.std(diffs)
            active, idle = [], []
            for d in diffs:
                if d <= threshold:
                    active.append(d)
                else:
                    idle.append(d)
            actives = active
            idles = idle

        active_mean, active_std, active_max, active_min = safe_mean(actives), safe_std(actives), max(actives, default=0), min(actives, default=0)
        idle_mean, idle_std, idle_max, idle_min = safe_mean(idles), safe_std(idles), max(idles, default=0), min(idles, default=0)

        # Subflow (simple approximation)
        subflow_fwd_pkts = total_fwd_pkts
        subflow_bwd_pkts = total_bwd_pkts
        subflow_fwd_bytes = total_len_fwd
        subflow_bwd_bytes = total_len_bwd

        # TCP window & data pkt approximation
        init_win_fwd = fwd_pkts[0][TCP].window if (fwd_pkts and TCP in fwd_pkts[0]) else 0
        init_win_bwd = bwd_pkts[0][TCP].window if (bwd_pkts and TCP in bwd_pkts[0]) else 0
        act_data_pkt_fwd = sum(1 for p in fwd_pkts if len(p) > 0)
        min_seg_size_fwd = min((len(p) for p in fwd_pkts), default=0)

        # ALL 78 FEATURES
        flow_features.append({
            "Destination Port": dport,
            "Flow Duration": flow_duration,
            "Total Fwd Packets": total_fwd_pkts,
            "Total Backward Packets": total_bwd_pkts,
            "Total Length of Fwd Packets": total_len_fwd,
            "Total Length of Bwd Packets": total_len_bwd,
            "Fwd Packet Length Max": max(fwd_lens),
            "Fwd Packet Length Min": min(fwd_lens),
            "Fwd Packet Length Mean": safe_mean(fwd_lens),
            "Fwd Packet Length Std": safe_std(fwd_lens),
            "Bwd Packet Length Max": max(bwd_lens),
            "Bwd Packet Length Min": min(bwd_lens),
            "Bwd Packet Length Mean": safe_mean(bwd_lens),
            "Bwd Packet Length Std": safe_std(bwd_lens),
            "Flow Bytes/s": flow_bytes_per_s,
            "Flow Packets/s": flow_pkts_per_s,
            "Flow IAT Mean": flow_iat_mean,
            "Flow IAT Std": flow_iat_std,
            "Flow IAT Max": flow_iat_max,
            "Flow IAT Min": flow_iat_min,
            "Fwd IAT Total": fwd_iat_total,
            "Fwd IAT Mean": fwd_iat_mean,
            "Fwd IAT Std": fwd_iat_std,
            "Fwd IAT Max": fwd_iat_max,
            "Fwd IAT Min": fwd_iat_min,
            "Bwd IAT Total": bwd_iat_total,
            "Bwd IAT Mean": bwd_iat_mean,
            "Bwd IAT Std": bwd_iat_std,
            "Bwd IAT Max": bwd_iat_max,
            "Bwd IAT Min": bwd_iat_min,
            "Fwd PSH Flags": fwd_psh,
            "Bwd PSH Flags": bwd_psh,
            "Fwd URG Flags": fwd_urg,
            "Bwd URG Flags": bwd_urg,
            "Fwd Header Length": fwd_hdr_len,
            "Bwd Header Length": bwd_hdr_len,
            "Fwd Packets/s": fwd_pkts_per_s,
            "Bwd Packets/s": bwd_pkts_per_s,
            "Min Packet Length": min_pkt_len,
            "Max Packet Length": max_pkt_len,
            "Packet Length Mean": pkt_len_mean,
            "Packet Length Std": pkt_len_std,
            "Packet Length Variance": pkt_len_var,
            "FIN Flag Count": fin,
            "SYN Flag Count": syn,
            "RST Flag Count": rst,
            "PSH Flag Count": psh,
            "ACK Flag Count": ack,
            "URG Flag Count": urg,
            "CWE Flag Count": cwe,
            "ECE Flag Count": ece,
            "Down/Up Ratio": down_up_ratio,
            "Average Packet Size": avg_pkt_size,
            "Avg Fwd Segment Size": avg_fwd_seg_size,
            "Avg Bwd Segment Size": avg_bwd_seg_size,
            "Fwd Header Length.1": fwd_hdr_len,
            "Fwd Avg Bytes/Bulk": 0,
            "Fwd Avg Packets/Bulk": 0,
            "Fwd Avg Bulk Rate": 0,
            "Bwd Avg Bytes/Bulk": 0,
            "Bwd Avg Packets/Bulk": 0,
            "Bwd Avg Bulk Rate": 0,
            "Subflow Fwd Packets": subflow_fwd_pkts,
            "Subflow Fwd Bytes": subflow_fwd_bytes,
            "Subflow Bwd Packets": subflow_bwd_pkts,
            "Subflow Bwd Bytes": subflow_bwd_bytes,
            "Init_Win_bytes_forward": init_win_fwd,
            "Init_Win_bytes_backward": init_win_bwd,
            "act_data_pkt_fwd": act_data_pkt_fwd,
            "min_seg_size_forward": min_seg_size_fwd,
            "Active Mean": active_mean,
            "Active Std": active_std,
            "Active Max": active_max,
            "Active Min": active_min,
            "Idle Mean": idle_mean,
            "Idle Std": idle_std,
            "Idle Max": idle_max,
            "Idle Min": idle_min,
            "Subflow Bwd Bytes": total_len_bwd
        })
        '''
        flow_features.append({
            "Destination Port": dport,
            "Average Packet Size": avg_pkt_size,
            "Init_Win_bytes_forward": init_win_fwd,
            "Packet Length Std": pkt_len_std,
            "Min Packet Length": min_pkt_len,
            "Max Packet Length": max_pkt_len,
            "Bwd Packet Length Std": safe_std(bwd_lens),
            "Init_Win_bytes_backward": init_win_bwd,
            "Packet Length Variance": pkt_len_var,
            "Bwd Packet Length Max": max(bwd_lens),
            "Bwd Packet Length Min": min(bwd_lens),
            "Subflow Fwd Bytes": subflow_fwd_bytes,
            "Fwd Packet Length Max": max(fwd_lens),
            "Fwd Packet Length Min": min(fwd_lens),
            "Avg Bwd Segment Size": avg_bwd_seg_size,
            "Packet Length Mean": pkt_len_mean,
            "Bwd Packet Length Mean": safe_mean(bwd_lens),
            "Fwd Packet Length Mean": safe_mean(fwd_lens),
            "Bwd Header Length": bwd_hdr_len,
            "Subflow Bwd Bytes": subflow_bwd_bytes,
        })
        '''
        
    # Save CSV
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pcap_path))[0]
    csv_path = os.path.join(output_dir, f"{base_name}_flows.csv")
    pd.DataFrame(flow_features).to_csv(csv_path, index=False)
    print(f"✅ Saved complete flow feature CSV with all 78 features: {csv_path}")
    return csv_path
