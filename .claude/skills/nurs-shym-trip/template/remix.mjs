// НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ курс: Нұрсерік пен PROXIMA нарықты колоссал етті.
// Сводит звук готового ролика: голос + еле слышные клики/кранчи на каждое появление слова и карточки
// (звуки из папки пользователя МОНТАЖ\ЗВУКИ\SFX, «чуть-чуть подсолить»). Видео копируется как есть.
// node remix.mjs video-perehod.html out/perehod.mp4 "out/итог.mp4"
import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';
const [html, vin, vout] = process.argv.slice(2);
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const browser = await puppeteer.launch({ headless: true, executablePath: CHROME, args: ['--allow-file-access-from-files', '--disable-web-security'] });
const p = await browser.newPage();
await p.setViewport({ width: 1080, height: 1920 });
await p.goto('file:///' + path.resolve(html).replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
await p.evaluate(() => window.READY);
const { DUR, EV } = await p.evaluate(() => {
  const ev = [];
  document.querySelectorAll('section.scene').forEach(sc => {
    const s0 = parseFloat(sc.dataset.s);
    sc.querySelectorAll('[data-in]').forEach(el => {
      const d = el.dataset;
      if (d.fx === 'words') (d.w || d.in).split(/\s+/).filter(Boolean).forEach(w => ev.push([s0 + parseFloat(w), 'w']));
      else if (el.classList.contains('rcard')) ev.push([s0 + parseFloat(d.in), 'c']);
      else if (el.id === 'ctaw' || el.classList.contains('mgw')) ev.push([s0 + parseFloat(d.in), 'w']);
    });
  });
  // карточки «охват» (data-sin) и COMMERCIAL в блокноте
  const st = el => parseFloat(el.closest('section').dataset.s);
  document.querySelectorAll('.rcard[data-sin]').forEach(el => ev.push([st(el) + parseFloat(el.dataset.sin), 'c']));
  const nb = document.querySelector('img[data-seq="media/nb/"]'); if (nb) ev.push([st(nb) + 1.92, 'w']);
  return { DUR: window.DUR, EV: ev.sort((a, b) => a[0] - b[0]) };
});
await browser.close();
// чередуем: кранч 1/2/3 на слова, клик на карточки; очень тихо (~22–26 дБ ниже голоса)
const pick = (k, i) => k === 'c' ? ['click', 0.07] : [`crunch${(i % 3) + 1}`, 0.055];
// QUIET="a-b" — окно, где звуки тише (сцена «охват»), QK — во сколько раз
const [QA, QB] = (process.env.QUIET || '0-0').split('-').map(Number), QK = parseFloat(process.env.QK || 0.4);
const ev = EV.filter(([t]) => t >= 0 && t < DUR).map(([t, k], i) => { const [n, g] = pick(k, i); return [t, n, t >= QA && t < QB ? g * QK : g]; });
// CUTWHOOSH="2.567" — тихий кинематографичный вжух (Саунд Пак), пик ровно на склейке
if (process.env.CUTWHOOSH) { const PK = JSON.parse(fs.readFileSync('a/sfx_pro/peaks.json', 'utf8'));
  process.env.CUTWHOOSH.split(',').map(Number).forEach(c => ev.push([Math.max(0, c - PK.cin2), 'cin2', parseFloat(process.env.CWVOL || 0.13)])); }
const inA = ['-i', vin, '-i', 'media/voice.m4a'], flt = ['[1:a]asplit=2[vo][vsc]'], mix = ['[vo]'];
ev.forEach(([t, n, g], i) => { inA.push('-i', `a/sfx_pro/${n}.wav`); const k = i + 2;
  flt.push(`[${k}:a]adelay=${Math.round(t * 1000)}:all=1,volume=${g}[s${k}]`); mix.push(`[s${k}]`); });
// музыка (тайп-бит, как в креативе 3): с 5.9 с трека, тише голоса, приглушается под речь
// звук wipe-переходов из примера (только звук, без голоса) — под B-roll после хука
if (fs.existsSync('a/sfx_pro/wipeset.wav') && process.env.WIPESET) {
  const k = ev.length + 2; inA.push('-i', 'a/sfx_pro/wipeset.wav'); ev.push([0, 'wipeset', 0]);
  flt.push(`[${k}:a]adelay=${Math.round(parseFloat(process.env.WIPESET) * 1000)}:all=1,volume=${process.env.WVOL || 0.5}[wp]`); mix.push('[wp]');
}
const MUSIC = process.env.MUSIC, MUSIC2 = process.env.MUSIC2;
if (MUSIC && fs.existsSync(MUSIC)) {
  let k = ev.length + 2; const XF = parseFloat(process.env.XF || 0), XD = 1.2, MV = process.env.MVOL || 0.2;
  inA.push('-ss', process.env.MSS || '5.9', '-i', MUSIC);
  if (MUSIC2 && fs.existsSync(MUSIC2) && XF > 0) {
    // трек 1 до XF, плавно перетекает в трек 2 (XD сек), трек 2 до конца
    inA.push('-ss', process.env.MSS2 || '42', '-i', MUSIC2);
    flt.push(`[${k}:a]atrim=0:${(XF + XD).toFixed(2)},asetpts=PTS-STARTPTS,volume=${MV},afade=t=in:d=0.3,afade=t=out:st=${XF.toFixed(2)}:d=${XD}[ma]`,
      `[${k + 1}:a]atrim=0:${(DUR - XF).toFixed(2)},asetpts=PTS-STARTPTS,volume=${process.env.MVOL2 || MV},afade=t=in:d=${XD},afade=t=out:st=${(DUR - XF - 1.0).toFixed(2)}:d=1.0,adelay=${Math.round(XF * 1000)}:all=1[mb]`,
      `[ma][mb]amix=inputs=2:normalize=0:duration=longest[mx]`);
    // паузы в музыке: DROPS="a-b,c-d" — музыка мягко замолкает (ramp 60 мс) и возвращается
    const drops = (process.env.DROPS || '').split(',').filter(Boolean).map(x => x.split('-').map(Number));
    const expr = drops.map(([a, b]) => `(1-0.97*clip((t-${a})/0.06,0,1)*clip((${b}-t)/0.06,0,1))`).join('*') || '1';
    flt.push(`[mx]volume='${expr}':eval=frame[mu0]`);
  } else flt.push(`[${k}:a]atrim=0:${DUR},asetpts=PTS-STARTPTS,volume=${MV},afade=t=in:d=0.3,afade=t=out:st=${(DUR - 1.2).toFixed(2)}:d=1.2[mu0]`);
  flt.push(`[mu0][vsc]sidechaincompress=threshold=0.02:ratio=5:attack=15:release=350[mu]`);
  mix.push('[mu]');
} else flt[0] = '[1:a]anull[vo]';
flt.push(`${mix.join('')}amix=inputs=${mix.length}:normalize=0:duration=longest,atrim=0:${DUR},loudnorm=I=-14:TP=-1.5[aout]`);
execFileSync('ffmpeg', ['-v', 'error', '-y', ...inA, '-filter_complex', flt.join(';'), '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', String(DUR), '-movflags', '+faststart', vout], { stdio: ['ignore', 'ignore', 'inherit'] });
console.log('звуков:', ev.length);
console.log('Готово:', vout);
