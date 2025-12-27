from quart import Blueprint, Response, request, render_template, redirect
from math import ceil
from re import match as re_match
from .error import abort
from bot import TelegramBot
from bot.config import Telegram, Server
from bot.modules.telegram import get_message, get_file_properties

bp = Blueprint('main', __name__)

@bp.route('/')
async def home():
    return redirect(f'https://t.me/{Telegram.BOT_USERNAME}')

@bp.route("/dl/<file_id>")
async def dl(file_id):
    filepath = f"/path/to/files/{file_id}.mp4"
    start = 0
    end = None

    range_header = request.headers.get('Range', None)
    if range_header:
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            start = int(match.group(1))
            if match.group(2):
                end = int(match.group(2))

    file_size = os.path.getsize(filepath)
    end = end if end is not None else file_size - 1
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
    return Response(chunk, 206, headers)

    async def file_stream():
        bytes_streamed = 0
        chunk_index = 0
        try:
            async for chunk in TelegramBot.stream_media(
                file,
                offset=offset_chunks,
                limit=chunks_to_stream,
            ):
                if chunk_index == 0:
                    trim_start = start % chunk_size
                    if trim_start > 0:
                        chunk = chunk[trim_start:]

                remaining_bytes = content_length - bytes_streamed
                if remaining_bytes <= 0:
                    break

                if len(chunk) > remaining_bytes:
                    chunk = chunk[:remaining_bytes]

                yield chunk
                bytes_streamed += len(chunk)
                chunk_index += 1
        except Exception as e:
            print("Stream stopped:", e)
            return

    return Response(file_stream(), headers=headers, status=status_code)

@bp.route('/stream/<int:file_id>')
async def stream_file(file_id):
    code = request.args.get('code') or abort(401)
    return await render_template(
        'player.html',
        mediaLink=f'{Server.BASE_URL}/dl/{file_id}?code={code}'
    )

