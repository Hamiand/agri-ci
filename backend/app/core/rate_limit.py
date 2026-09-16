import time,threading
from collections import defaultdict,deque
from fastapi import HTTPException,Request
_lock=threading.Lock()
_hits=defaultdict(deque)

def rate_limit(request:Request,bucket:str,limit:int=30,window_seconds:int=60):
    """Pilot protection. Replace with Redis/distributed limiter before multi-instance scale."""
    host=request.client.host if request.client else "unknown"
    key=f"{bucket}:{host}"
    now=time.time()
    with _lock:
        q=_hits[key]
        while q and q[0] <= now-window_seconds:q.popleft()
        if len(q)>=limit:
            raise HTTPException(status_code=429,detail="RATE_LIMITED")
        q.append(now)
