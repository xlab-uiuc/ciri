from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from collections import Counter
import random
from typing import List


def get_dominant_reason(reasons: List[str]) -> str:
    """
    Get a representative reason from the most dominant cluster of similar reasons.
    
    Args:
        reasons: List of reason strings to analyze
        
    Returns:
        A representative reason string from the largest cluster of similar reasons
    """
    if not reasons:
        raise ValueError("Input reasons list cannot be empty")
        
    if len(reasons) == 1:
        return reasons[0]

    # Calculate the TF-IDF scores
    vectorizer = TfidfVectorizer(strip_accents='unicode', lowercase=True)
    tfidf_matrix = vectorizer.fit_transform(reasons)
    
    # Cluster the reasons using DBSCAN
    dbscan = DBSCAN(eps=0.3, min_samples=2, metric='cosine').fit(tfidf_matrix)
    labels = dbscan.labels_
    
    # If all reasons are considered noise, return most common reason
    unique_labels = set(labels)
    if len(unique_labels) == 1 and -1 in unique_labels:
        return Counter(reasons).most_common(1)[0][0]
    
    # Find the dominant cluster, excluding noise points (-1)
    label_counts = Counter(labels)
    if -1 in label_counts:
        del label_counts[-1]
        
    if not label_counts:  # If no valid clusters remain
        return Counter(reasons).most_common(1)[0][0]
        
    dominant_cluster_label = label_counts.most_common(1)[0][0]
    
    # Get reasons from dominant cluster and return most frequent
    dominant_cluster_reasons = [reason for idx, reason in enumerate(reasons) 
                              if labels[idx] == dominant_cluster_label]
    return Counter(dominant_cluster_reasons).most_common(1)[0][0]