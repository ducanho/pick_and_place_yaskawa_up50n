'use strict';
const el = id => document.getElementById(id);
const number = v => v == null ? '—' : Number(v).toFixed(2);
let initialized = false;
let lastEvent = 0;
const labels = {plane_z_mm:'Plane Z · mm',rx:'RX · °',ry:'RY · °',rz:'RZ · °',movl_speed:'MOVL · mm/s',confidence:'Confidence',position_tolerance_mm:'Stability tolerance · mm',minimum_move_distance_mm:'Minimum distance · mm',max_frame_age_ms:'Max frame age · ms',max_frame_gap_ms:'Max frame gap · ms',min_stable_frames:'Stable frames',stable_duration_seconds:'Additional stable · s'};
async function api(path, data) {
  const response = await fetch('/api/' + path, {method:data === undefined ? 'GET' : 'POST',headers:data === undefined ? {} : {'Content-Type':'application/json','X-NX100-Control':'operator'},body:data === undefined ? undefined : JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(typeof result.message === 'string' ? result.message : JSON.stringify(result.detail || result));
  return result;
}
function error(err) { el('error').hidden = false; el('error').textContent = err.message; }
function bind(id, path, data = () => ({})) {
  el(id).addEventListener('click', async () => {
    el(id).disabled = true;
    try { await api(path, data()); el('error').hidden = true; } catch (err) { error(err); }
    finally { el(id).disabled = false; }
  });
}
bind('start','auto/start'); bind('stop','auto/stop'); bind('hold','robot/hold');
bind('robot-disconnect','robot/disconnect'); bind('camera-disconnect','camera/disconnect');
bind('camera-connect','camera/connect', () => ({index:Number(el('cameras').value)}));
el('scan').addEventListener('click', async () => {
  try {
    const cameras = await api('camera/scan', {});
    el('cameras').replaceChildren(...cameras.map(camera => {
      const option = document.createElement('option'); option.value = camera.index; option.textContent = camera.name; return option;
    }));
  } catch (err) { error(err); }
});
el('robot-form').addEventListener('submit', async event => {
  event.preventDefault(); const form = new FormData(event.target);
  try { await api('robot/connect', {ip:form.get('ip'),port:Number(form.get('port'))}); el('error').hidden = true; } catch (err) { error(err); }
});
el('config-form').addEventListener('submit', async event => {
  event.preventDefault(); const values = Object.fromEntries([...new FormData(event.target)].map(([k,v])=>[k,Number(v)]));
  try { await api('config', values); el('error').hidden = true; } catch (err) { error(err); }
});
function flags(container, entries) {
  el(container).replaceChildren(...entries.map(([name, value, bad]) => {
    const span = document.createElement('span'); span.className = 'flag' + (bad ? ' bad' : value ? ' on' : ''); span.textContent = `${name}: ${value ? 'ON' : 'OFF'}`; return span;
  }));
}
function render(data) {
  const {robot:r, auto:a, vision:v, calibration:c} = data;
  el('network').textContent = '● Dashboard online'; el('mode').textContent = r.mode;
  el('state').textContent = a.state; el('message').textContent = a.message;
  el('selected').textContent = a.selected ? `ID ${a.selected.object_id}` : '—';
  el('minimum').textContent = `${a.tracking.minimum_move_distance_mm} mm`;
  el('eligible').textContent = a.eligible_count; el('completed').textContent = a.last_completed ? `ID ${a.last_completed.object_id}` : '—';
  el('robot-status').textContent = r.connected ? 'Connected' : 'Disconnected';
  const f = r.flags || {};
  flags('flags', ['servo','remote','play','teach','alarm','error','running','hold'].map(k=>[k.toUpperCase(),!!f[k],!!f[k] && ['alarm','error','hold'].includes(k)]).concat([['BUSY',r.busy,false]]));
  el('pose').replaceChildren(...['x','y','z','rx','ry','rz'].map(axis=>{
    const div = document.createElement('div'); const label = document.createElement('span'); label.textContent = axis.toUpperCase(); const value = document.createElement('strong'); value.textContent = number(r.cartesian?.[axis]); div.append(label,value); return div;
  }));
  el('joint').textContent = r.joint ? 'RPOSJ · pulse: ' + ['s','l','u','r','b','t'].map(k=>`${k.toUpperCase()} ${r.joint[k]}`).join(' / ') : 'RPOSJ · pulse: —';
  el('motion').textContent = r.motion ? `${r.motion.phase}: ${r.motion.message}` : 'Chưa có lệnh MOVE';
  el('camera-status').textContent = v.connected ? 'Connected' : 'Disconnected';
  el('vision-info').textContent = `${v.mode} · ${v.fps} FPS · YOLO ${v.model_loaded ? 'ready' : 'not loaded'} ${v.error}`;
  if (v.connected) { el('preview').hidden=false; el('preview-empty').hidden=true; el('preview').src='/api/preview.jpg?t='+Date.now(); }
  else { el('preview').hidden=true; el('preview-empty').hidden=false; }
  el('targets').replaceChildren(...a.targets.map(t=>{
    const row = document.createElement('tr'); const cells = [`${t.id} / ${t.instance}`, t.name, number(t.confidence),`${number(t.u)} / ${number(t.v)}`, (t.xyz || []).map(number).join(' / '),(t.orientation || []).map(number).join(' / '),t.stable_frames || 0, number(t.stable_seconds || 0),number(t.distance_last_mm),number(t.distance_same_id_mm),t.reason || 'stabilizing'];
    for (const value of cells) { const td=document.createElement('td'); td.textContent=value; row.append(td); } return row;
  }));
  el('selected-pose').textContent = a.selected ? `Snapshot ID ${a.selected.object_id} · XYZ ${a.selected.xyz.join(', ')} mm · RX RY RZ ${a.selected.orientation.join(', ')}° · config v${a.selected.config_version}` : 'Chưa có snapshot đang thực thi';
  el('calibration').textContent = `${c.mode} · ${c.accepted_by_operator ? 'Đang dùng calibration đã xác nhận' : 'Calibration chưa khả dụng'}\nẢnh gốc ${c.image_size?.join(' × ') || '—'} · Offset Base X +280 / Y +215 mm\n${c.message}`;
  el('stop-status').textContent = `Stop requested: ${a.stop_requested} · Config version ${a.config_version}`;
  if (!initialized) {
    for (const [key,value] of Object.entries(a.tracking)) {
      const label=document.createElement('label'); label.textContent=labels[key] || key; const input=document.createElement('input'); input.type='number'; input.step='any'; input.name=key; input.value=value; input.required=true; label.append(input); el('config-form').append(label);
    }
    const button=document.createElement('button'); button.textContent='ÁP DỤNG CẤU HÌNH'; el('config-form').append(button); initialized=true;
  }
  if (data.events.length && data.events.at(-1).id !== lastEvent) {
    el('events').textContent=data.events.map(e=>`${e.time}  ${e.level}  ${e.message}`).join('\n'); el('events').scrollTop=el('events').scrollHeight; lastEvent=data.events.at(-1).id;
  }
}
async function poll() {
  try { render(await api('state')); } catch (err) { el('network').textContent='Dashboard mất kết nối'; error(err); }
  setTimeout(poll, 400);
}
poll();
