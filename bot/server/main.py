import os
import re
from quart import Blueprint, Response, request, render_template, redirect
from .error import abort
from bot.config import Telegram, Server

bp = Blueprint('main', __name__)

# Redirect home to bot
@bp.route('/')
async def home():
    return redirect(f'https://t.me/{Telegram.BOT_USERNAME}')

# Download/stream endpoint
@bp.route("/dl/<file_id>")
async def dl(file_id):
    # Update this path to where your files actually are
    filepath = f"/path/to/files/{file_id}.mp4"

    if not os.path.exists(filepath):
        return "File not found", 404

    file_size = os.path.getsize(filepath)
    start = 0
    end = file_size - 1

    range_header = request.headers.get('Range', None)
    if range_header:
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            start = int(match.group(1))
            if match.group(2):
                end = int(match.group(2))
    length = end - start + 1

    with open(filepath, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)

    headers = {
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Accept-Ranges': 'bytes',
        'Content-Length': str(length),
        'Content-Type': 'video/mp4'
    }
    return Response(chunk, status=206 if range_header else 200, headers=headers)

# Stream endpoint
@bp.route('/stream/<file_id>')
async def stream_file(file_id):
    code = request.args.get('code') or abort(401)
    return await render_template(
        'player.html',
        mediaLink=f'{Server.BASE_URL}/dl/{file_id}?code={code}'
    )
