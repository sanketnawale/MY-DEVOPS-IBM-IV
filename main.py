from fastapi import FastAPI
import subprocess
import requests
from pydantic import BaseModel
from fastapi import FastAPI
app = FastAPI()

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama's API

class SpoolData(BaseModel):
    content: str  # Spool message to be sent

def get_zos_jobs():
    cmd = [
        'zowe.cmd', 'zos-jobs', 'list', 'jobs',
        '--user', 'Z00805',
        '--password', 'VHM05VPF',
        '--host', '204.90.115.200',
        '--port', '10443',
        '--ru', 'false'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def get_job_spool(jobid):
    cmd = [
        'zowe.cmd', 'zos-jobs', 'view', 'all-spool-content', jobid,
        '--user', 'Z00805',
        '--password', 'VHM05VPF',
        '--host', '204.90.115.200',
        '--port', '10443',
        '--ru', 'false'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

@app.get("/jobs")
def list_jobs():
    jobs_data = get_zos_jobs()
    return {"jobs": jobs_data.splitlines()}

@app.get("/jobs/{jobid}/spool")
def view_spool(jobid: str):
    spool_content = get_job_spool(jobid)
    return {"spool": spool_content}

@app.post("/send_spool")
async def send_spool(spool: SpoolData):
    """ Sends spool data to Ollama AI and returns the response """
    payload = {
        "model": "deepseek-r1:1.5b",  # Use DeepSeek-R1 1.5B model
        "prompt": spool.content,
        "stream": False
    }

    print(f"📤 Sending spool data: {spool.content[:100]}...")  # Only show first 100 chars

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json()  # Return AI-generated response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
