#!/bin/bash
# Подбор уровня музыки и скорости её возврата после фразы.
#
# Владелец слышит «шум после точки». Голос там уже чистый: ворота дают минус
# девяносто пять децибел. Значит звучит МУЗЫКА: она приглушается под голосом и
# выныривает в паузе. Чем быстрее возврат, тем заметнее этот всплеск, и на слух
# он читается как шум или задержка.
#
# Медленный возврат означает, что в коротких паузах музыка остаётся тихой и
# поднимается только там, где владелец действительно молчит долго.
cd /Volumes/T7/ibook-reels/tishina || exit 1
MUZ=/Volumes/T7/reels-saas/reel_music_chistaya.m4a
CH="highpass=f=70,afftdn=nf=-35:nr=20,agate=threshold=0.03:range=0.0002:ratio=9:attack=4:release=70:knee=3,loudnorm=I=-14:TP=-2.0:LRA=9"
LOUD="acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=2,loudnorm=I=-13:TP=-1.5:LRA=7,volume=5dB,alimiter=limit=0.95:level=disabled"

proba () {
  ffmpeg -y -v error -i syroy.wav -i "$MUZ" -filter_complex \
    "[0]${CH}[vc];[1]volume=$1[m];[vc]asplit=2[v1][v2];[m][v1]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=$2[md];[v2][md]amix=inputs=2:normalize=0:duration=first,${LOUD}[a]" \
    -map "[a]" -ar 16000 -ac 1 "m_$3.wav" && echo "готов $3" || echo "СБОЙ $3"
}

proba 0.34 250 seychas
proba 0.22 700 tishe
proba 0.15 900 ochen_tiho
proba 0.00 250 bez_muzyki
ls -la m_*.wav 2>/dev/null | awk '{print $9}'
