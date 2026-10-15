from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ConnectionFeatures(BaseModel):
    """
    Input schema for the 41 NSL-KDD network traffic attributes.
    Sensible defaults represent standard TCP web/HTTP traffic.
    """
    duration: float = Field(0.0, description="Length of connection in seconds")
    protocol_type: str = Field("tcp", description="Protocol type: tcp, udp, icmp")
    service: str = Field("http", description="Network service on destination (e.g. http, ftp, smtp)")
    flag: str = Field("SF", description="Normal or error status of the connection (e.g. SF, S0, REJ)")
    src_bytes: float = Field(215.0, description="Bytes sent from source to destination")
    dst_bytes: float = Field(450.0, description="Bytes sent from destination to source")
    land: float = Field(0.0, description="1 if connection is from/to same host/port; 0 otherwise")
    wrong_fragment: float = Field(0.0, description="Number of wrong fragments")
    urgent: float = Field(0.0, description="Number of urgent packets")
    hot: float = Field(0.0, description="Number of hot indicators")
    num_failed_logins: float = Field(0.0, description="Number of failed login attempts")
    logged_in: float = Field(1.0, description="1 if successfully logged in; 0 otherwise")
    num_compromised: float = Field(0.0, description="Number of compromised conditions")
    root_shell: float = Field(0.0, description="1 if root shell is obtained; 0 otherwise")
    su_attempted: float = Field(0.0, description="1 if su root command attempted; 0 otherwise")
    num_root: float = Field(0.0, description="Number of root accesses")
    num_file_creations: float = Field(0.0, description="Number of file creation operations")
    num_shells: float = Field(0.0, description="Number of shell prompts")
    num_access_files: float = Field(0.0, description="Number of operations on access control files")
    num_outbound_cmds: float = Field(0.0, description="Number of outbound commands in ftp session")
    is_host_login: float = Field(0.0, description="1 if login belongs to host admin; 0 otherwise")
    is_guest_login: float = Field(0.0, description="1 if login is a guest account; 0 otherwise")
    count: float = Field(1.0, description="Number of connections to same host in past 2 seconds")
    srv_count: float = Field(1.0, description="Number of connections to same service in past 2 seconds")
    serror_rate: float = Field(0.0, description="% of connections that have SYN errors")
    srv_serror_rate: float = Field(0.0, description="% of connections to same service that have SYN errors")
    rerror_rate: float = Field(0.0, description="% of connections that have REJ errors")
    srv_rerror_rate: float = Field(0.0, description="% of connections to same service that have REJ errors")
    same_srv_rate: float = Field(1.0, description="% of connections to same service")
    diff_srv_rate: float = Field(0.0, description="% of connections to different services")
    srv_diff_host_rate: float = Field(0.0, description="% of connections to different hosts")
    dst_host_count: float = Field(1.0, description="Destination host count")
    dst_host_srv_count: float = Field(1.0, description="Destination host service count")
    dst_host_same_srv_rate: float = Field(1.0, description="Destination host same service rate")
    dst_host_diff_srv_rate: float = Field(0.0, description="Destination host diff service rate")
    dst_host_same_src_port_rate: float = Field(1.0, description="Destination host same source port rate")
    dst_host_srv_diff_host_rate: float = Field(0.0, description="Destination host diff host rate")
    dst_host_serror_rate: float = Field(0.0, description="Destination host SYN error rate")
    dst_host_srv_serror_rate: float = Field(0.0, description="Destination host service SYN error rate")
    dst_host_rerror_rate: float = Field(0.0, description="Destination host REJ error rate")
    dst_host_srv_rerror_rate: float = Field(0.0, description="Destination host service REJ error rate")
    difficulty: Optional[float] = Field(20.0, description="NSL-KDD difficulty score (optional)")

class PredictionResult(BaseModel):
    id: str
    timestamp: str
    task: str  # "binary" or "five_class"
    predicted_class: str
    confidence: float
    probabilities: Dict[str, float]
    inference_time_ms: float
    storage_type: str  # "mongodb" or "local_fallback"
    features: Dict[str, Any]

class DatabaseStatus(BaseModel):
    status: str  # "connected" or "offline_fallback"
    message: str
    uri: str
    db_name: str
    total_records: int

class SystemHealth(BaseModel):
    status: str
    spark_version: str
    models_loaded: Dict[str, bool]
    database: DatabaseStatus

class PresetProfile(BaseModel):
    id: str
    name: str
    category: str
    description: str
    features: Dict[str, Any]
