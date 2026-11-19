# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Режет примеры wipe transition и блокнот из «рилс ержан.MP4» под наш таймлайн (30 fps, кадры jpg). Звук не берём.
$f = "media\src_ex.mp4"
function seq($dir, $vf, $ss, $t) {
  New-Item -ItemType Directory -Force "media\$dir" | Out-Null
  Get-ChildItem "media\$dir" -Filter *.jpg | Remove-Item -Force -Confirm:$false
  ffmpeg -v error -y -ss $ss -t $t -i $f -an -vf "$vf,fps=30,format=yuvj420p" -q:v 2 "media\$dir\%05d.jpg"
  "{0}: {1} frames" -f $dir, (Get-ChildItem "media\$dir").Count
}
# 1) нарезка wipe-переходов (вертикально, весь кадр): 1.60–2.95 → 0.79 с (×1.71)
seq 'ex_wipe' 'setpts=PTS/1.71,scale=1080:1920' 1.60 1.35
# 2) горизонтальные примеры (без белого фона): 6.45–9.33 → 3.18 с
seq 'ex_dyn' 'crop=1080:816:0:552,setpts=PTS*1.104' 6.45 2.88
# 3) примеры «машина / сумка»: 14.12–15.96 → 2.14 с
seq 'ex_bag' 'crop=1080:816:0:552,setpts=PTS*1.163' 14.12 1.84
# 4) съёмка руками: 18.53–20.67 → 2.14 с
seq 'ex_hand' 'scale=1080:1920' 18.53 2.14
# 5) блокнот по словам: особенно | travel | fashion | commercial
New-Item -ItemType Directory -Force "media\nb" | Out-Null
Get-ChildItem "media\nb" -Filter *.jpg | Remove-Item -Force -Confirm:$false
$fc = "[0:v]trim=9.36:9.80,setpts=(PTS-STARTPTS)*1.18[a];[0:v]trim=9.80:10.52,setpts=PTS-STARTPTS[b];[0:v]trim=10.52:11.20,setpts=PTS-STARTPTS[c];[0:v]trim=11.20:12.45,setpts=(PTS-STARTPTS)*0.592[d];[a][b][c][d]concat=n=4:v=1:a=0,scale=1080:1920,fps=30,format=yuvj420p[v]"
ffmpeg -v error -y -i $f -filter_complex $fc -map "[v]" -q:v 2 "media\nb\%05d.jpg"
"nb: {0} frames" -f (Get-ChildItem "media\nb").Count

