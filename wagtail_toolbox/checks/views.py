import subprocess

from django.http import StreamingHttpResponse
from django.shortcuts import render


def models_list(request):
    def stream_response():
        process = subprocess.Popen(
            ["python", "manage.py", "model_response"], stdout=subprocess.PIPE
        )
        for line in iter(process.stdout.readline, b""):
            yield line.decode("utf-8")

        process.stdout.close()
        process.wait()

    return StreamingHttpResponse(stream_response())


def models_view(request):
    return render(
        request,
        "checks/models.html",
        {
            "title": "Models",
            "description": "A list of all models in the project.",
        },
    )
