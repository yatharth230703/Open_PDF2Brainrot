import uuid, os
from pathlib import Path
from django.shortcuts import render, redirect
from django.conf import settings
from .processing import process_pdf

def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf = request.FILES['pdf']
        job_id = uuid.uuid4()
        media_root = Path(settings.MEDIA_ROOT)

        input_dir = media_root / 'input'
        input_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = input_dir / f'{job_id}.pdf'
        with open(pdf_path, 'wb') as f:
            for chunk in pdf.chunks():
                f.write(chunk)
        out_root = media_root / 'processed' / str(job_id)
        out_root.mkdir(parents=True, exist_ok=True)
        process_pdf(pdf_path, out_root)

        return redirect('viewer:view_results', job_id=job_id)

    return render(request, 'upload.html')



def view_results(request, job_id):
    base = Path(settings.MEDIA_ROOT) / 'processed' / str(job_id)
    mapping = {}
    for jsonf in (base / 'flashcards').glob('*.json'):
        name = jsonf.stem 
        mapping.setdefault(name, {})['json_url'] = (
            settings.MEDIA_URL + f'processed/{job_id}/flashcards/{jsonf.name}'
        )
    videos_root = base / 'videos'
    for sub in videos_root.iterdir():
        if not sub.is_dir(): continue
        name = sub.name  
        urls = []
        for vid in sorted(sub.iterdir()):
            if vid.suffix.lower() in ('.mp4','.mov','.avi'):
                urls.append(settings.MEDIA_URL + f'processed/{job_id}/videos/{name}/{vid.name}')
        if urls:
            mapping.setdefault(name, {})['video_urls'] = urls
    flashcards = sorted(mapping.keys(),
        key=lambda n: int(n.split('_')[1])
    )

    return render(request, 'results.html', {
        'mapping': mapping,
        'flashcards': flashcards,
    })
