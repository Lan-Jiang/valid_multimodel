import os
import uuid
import math
import subprocess
import json
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from typing import List, Dict
from videohash import VideoHash

app = FastAPI()

# In-memory storage as per requirements
video_db = {} 

CANONICAL_RATIOS = {
    "9:16": 9/16,
    "1:1": 1/1,
    "4:5": 4/5,
    "16:9": 16/9
}

def get_aspect_ratio_bucket(width: int, height: int):
    actual_ratio = width / height
    for label, value in CANONICAL_RATIOS.items():
        # Check within 1% tolerance
        if abs(actual_ratio - value) <= 0.01 * value:
            return label
    return f"{width}:{height}"

@app.post("/upload")
async def upload_videos(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        file_id = str(uuid.uuid4())
        temp_path = f"temp_{file_id}.mp4"
        
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # 1. Extract Metadata using ffprobe
        cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json {temp_path}"
        meta = json.loads(subprocess.check_output(cmd, shell=True))
        w, h = meta['streams'][0]['width'], meta['streams'][0]['height']
        
        # 2. Generate Perceptual Hash for matching
        v_hash = VideoHash(path=temp_path).hash_hex
        
        ratio_label = get_aspect_ratio_bucket(w, h)
        
        video_data = {
            "id": file_id,
            "filename": file.filename,
            "width": w,
            "height": h,
            "aspect_ratio": ratio_label,
            "hash": v_hash
        }
        
        video_db[file_id] = video_data
        results.append(video_data)
        os.remove(temp_path) # Clean up
        
    return results

@app.get("/videos")
async def list_videos(ratio: str = Query(None)):
    if ratio:
        return [v for v in video_db.values() if v['aspect_ratio'] == ratio]
    return list(video_db.values())

@app.get("/match")
async def match_video(video_id: str):
    target = video_db.get(video_id)
    if not target:
        raise HTTPException(status_code=404, detail="Video not found")
    
    matches = []
    for vid in video_db.values():
        if vid['id'] == video_id: continue
        
        # Simple Hamming distance check for similarity
        # In a production app, use bitwise comparison for 'confidence'
        if vid['hash'] == target['hash']:
            matches.append({"video_id": vid['id'], "confidence": 1.0})
            
    return matches