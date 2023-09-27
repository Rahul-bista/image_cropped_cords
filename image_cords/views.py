import io
import json
import os.path
import uuid
from pathlib import Path

from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from labels.forms import LabelForm
from labels.models import ImageLabel

import numpy as np


def alpha_composite_to_rgb(image: Image.Image):
    if image.mode == 'RGB':
        return image

    if image.mode == 'RGBA':
        with Image.new('RGBA', image.size, (0, 0, 0, 255)) as layer:
            rgba_image = Image.alpha_composite(layer, image)

        return rgba_image.convert('RGB')

    return image.convert('RGB')


def alpha_composite_to_rgba(image):
    with Image.new('RGBA', image.size, (0, 0, 0, 0)) as layer:
        rgba_image = Image.alpha_composite(layer, image)

    return rgba_image


def remove_background(image: Image.Image, mask: Image.Image):
    image = alpha_composite_to_rgb(image)
    image_arr = np.asarray(image)
    mask_arr = np.asarray(mask)

    transparent_arr = np.zeros((image_arr.shape[0], image_arr.shape[1], 4), dtype=np.uint8)
    transparent_arr[:, :, 0:3] = image_arr
    transparent_arr[:, :, 3] = mask_arr

    transparent_image = Image.fromarray(transparent_arr)
    transparent_image = alpha_composite_to_rgba(transparent_image)
    return transparent_image


def index(request):
    if request.method == 'POST':
        form = LabelForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            original_image = Image.open(form.cleaned_data['original_image'])
            mask_image = Image.open(form.cleaned_data['mask_image'])

            has_errors = False
            if original_image.width != mask_image.width or original_image.height != mask_image.height:
                form.add_error('original_image', 'Invalid image pair')
                has_errors = True

            if mask_image.mode != 'L':
                form.add_error('mask_image', 'Invalid mask image')
                has_errors = True

            if not has_errors:
                model = form.save()
                transparent = remove_background(original_image, mask_image)
                buffer = io.BytesIO()
                transparent.save(buffer, format='PNG')
                filename = Path(model.mask_image.path).name
                model.transparent_image.save(filename, buffer)
                model.save()
                return redirect(f'{reverse("generate")}?key={model.key}')

            return render(request, 'index.html',
                          {'form': form})

    return render(request, 'index.html')


def generate(request):
    key = request.GET.get('key')

    if not key:
        return redirect(reverse('home'))

    model = get_object_or_404(ImageLabel, key=key)

    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        left = data['x']
        top = data['y']
        width = data['width']
        height = data['height']
        right = left + width
        bottom = top + height

        original = Image.open(model.original_image.path)
        original_cropped = original.crop((left, top, right, bottom))

        mask = Image.open(model.mask_image.path)
        mask_cropped = mask.crop((left, top, right, bottom))

        filename = str(uuid.uuid4())
        im_dir = Path('out/im/')
        if not im_dir.exists():
            im_dir.mkdir(parents=True)

        gt_dir = Path('out/gt/')
        if not gt_dir.exists():
            gt_dir.mkdir(parents=True)

        original_cropped.save(f'out/im/{filename}.jpg')
        mask_cropped.save(f'out/gt/{filename}.png')

        return redirect(f'{request.path}?key={key}')

    return render(request, 'generate.html', {
        'model': model
    })
