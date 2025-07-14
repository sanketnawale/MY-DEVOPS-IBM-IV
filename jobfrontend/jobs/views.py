from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import requests
from django.shortcuts import render  # <-- Add this line

# ✅ Correct variable name
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def job_list(request):
    response = requests.get("http://127.0.0.1:8000/jobs")
    jobs_raw = response.json()["jobs"]
    
    jobs = []
    for job in jobs_raw:
        parts = job.split(maxsplit=4)  
        if len(parts) == 5:  
            job_data = {
                "jobid": parts[0],   
                "retcode": parts[1] + ' ' + parts[2],  
                "jobname": parts[3],  
                "status": parts[4]    
            }
            jobs.append(job_data)

    return render(request, "jobs/job_list.html", {"jobs": jobs})

def parse_spool_content(spool_content):
    spool_sections = []
    current_section = None
    
    for line in spool_content.splitlines():
        if line.startswith("Spool file:"):
            if current_section:
                spool_sections.append(current_section)
            current_section = {"title": line, "content": []}
        elif current_section:
            current_section["content"].append(line)
    
    if current_section:
        spool_sections.append(current_section)
    
    return spool_sections

def view_spool(request, jobid):
    response = requests.get(f"http://127.0.0.1:3000/jobs/{jobid}/spool")
    spool_content = response.json()["spool"]
    
    spool_sections = parse_spool_content(spool_content)

    return render(request, "jobs/job_spool.html", {
        "jobid": jobid,
        "spool_sections": spool_sections
    })

@csrf_exempt  # 🔴 CSRF exemption for testing
def send_spool_to_ollama(request):
    if request.method == "POST":
        try:
            # ✅ Read incoming JSON data
            data = json.loads(request.body)
            spool_content = data.get("content", "").strip()

            if not spool_content:
                print("❌ ERROR: No spool content received")  # Debug
                return JsonResponse({"error": "No spool content received"}, status=400)

            # ✅ Send spool content to Ollama API
            payload = {
                "model": "deepseek-r1:1.5b",  # Make sure the model exists
                "prompt": spool_content,
                "stream": False
            }
            print(f"📡 Sending to Ollama: {spool_content[:100]}...")  # Debug print

            response = requests.post(OLLAMA_URL, json=payload)
            print(f"📥 Ollama Response [{response.status_code}]: {response.text}")  # Debug print

            # ✅ Return Ollama's response
            return JsonResponse(response.json(), status=response.status_code)

        except json.JSONDecodeError:
            print("❌ ERROR: Invalid JSON received")  # Debug
            return JsonResponse({"error": "Invalid JSON received"}, status=400)

        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR: Request to Ollama failed: {e}")  # Debug
            return JsonResponse({"error": "Failed to reach Ollama API"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405),