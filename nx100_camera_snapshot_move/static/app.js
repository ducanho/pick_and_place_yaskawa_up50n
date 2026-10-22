'use strict';
const el=id=>document.getElementById(id);
const num=v=>v==null?'—':Number(v).toFixed(2);
let state=null,initialized=false,lastEvent=0;
const labels={plane_z_mm:'Plane Z · mm',rx:'RX · °',ry:'RY · °',rz:'RZ · °',movl_speed:'MOVL · mm/s (0.1–200)',confidence:'Confidence',minimum_move_distance_mm:'Minimum MOVE distance · mm'};
async function api(path,data){
 const response=await fetch('/api/'+path,{method:data===undefined?'GET':'POST',headers:data===undefined?{}:{'Content-Type':'application/json','X-NX100-Control':'operator'},body:data===undefined?undefined:JSON.stringify(data)});
 const result=await response.json();if(!response.ok)throw new Error(result.message||JSON.stringify(result.detail||result));return result;
}
function showError(error){el('error').hidden=false;el('error').textContent=error.message;}
function bind(id,path,data=()=>({})){
 el(id).addEventListener('click',async()=>{el(id).disabled=true;try{await api(path,data());el('error').hidden=true;}catch(error){showError(error);}finally{el(id).disabled=false;}});
}
bind('camera-connect','camera/connect',()=>({index:Number(el('cameras').value)}));
bind('camera-disconnect','camera/disconnect');bind('robot-disconnect','robot/disconnect');
bind('capture','snapshot/capture');bind('hold','robot/hold');bind('ack','fault/acknowledge');
bind('release-hold','robot/hold/release');
bind('send','snapshot/send',()=>({batch_id:state?.workflow.batch_id,record_id:state?.workflow.next_record_id}));
el('scan').addEventListener('click',async()=>{try{const cameras=await api('camera/scan',{});el('cameras').replaceChildren(...cameras.map(c=>{const option=document.createElement('option');option.value=c.index;option.textContent=c.name;return option;}));}catch(error){showError(error);}});
el('robot-form').addEventListener('submit',async event=>{event.preventDefault();const f=new FormData(event.target);try{await api('robot/connect',{ip:f.get('ip'),port:Number(f.get('port'))});el('error').hidden=true;}catch(error){showError(error);}});
el('config-form').addEventListener('submit',async event=>{event.preventDefault();const values=Object.fromEntries([...new FormData(event.target)].map(([key,value])=>[key,Number(value)]));try{await api('config',values);el('error').hidden=true;}catch(error){showError(error);}});
function table(id,rows){el(id).replaceChildren(...rows.map(values=>{const row=document.createElement('tr');for(const value of values){const cell=document.createElement('td');cell.textContent=value;row.append(cell);}return row;}));}
function moveNote(w,r){
 const reasons=[],flags=r.flags||{};
 if(!r.connected)reasons.push('Chưa kết nối robot.');
 if(w.active_id||r.motion?.phase==='MOVING'||flags.running)reasons.push('Robot đang MOVE/chạy; chờ xác minh hoàn thành.');
 if(w.phase==='FAULT')reasons.push('Có lỗi hoặc MOVE chưa xác minh. Kiểm tra robot dừng rồi bấm XÁC NHẬN LỖI. '+(w.message||''));
 if(r.connected){
  if(flags.hold||r.hold_pending)reasons.push('HOLD đang bật hoặc đang xử lý. Nhả HOLD trước khi gửi.');
  if(flags.alarm)reasons.push('Robot đang có ALARM.');
  if(flags.error)reasons.push('Robot đang báo ERROR.');
  if(!flags.servo)reasons.push('SERVO chưa bật.');
  if(!flags.remote)reasons.push('Robot chưa ở chế độ REMOTE.');
  if(!flags.play)reasons.push('Robot chưa ở chế độ PLAY.');
 }
 if(!w.next_record_id&&!w.active_id&&w.phase!=='FAULT'){
  const pending=w.saved.filter(s=>s.status==='SAVED');
  const translations={
   'distance from last MOVE <= minimum':`Cách tọa độ MOVE gần nhất không quá ${w.tracking.minimum_move_distance_mm} mm.`,
   'same track unchanged':`ID này chưa dịch chuyển quá ${w.tracking.minimum_move_distance_mm} mm.`,
   'outside workspace':'Tọa độ nằm ngoài vùng làm việc đã cấu hình.',
   'stale frame':'Dữ liệu ảnh đã cũ.'
  };
  if(pending.length)reasons.push(...pending.map(s=>`ID ${s.target.object_id}: ${translations[s.reason]||s.reason}`));
  else if(w.saved.some(s=>s.status==='UNCERTAIN'))reasons.push('Có lệnh chưa xác minh; cần kiểm tra robot và lưu bộ tọa độ mới.');
  else reasons.push(w.saved.length?'Đã gửi hết tọa độ. Cần lưu bộ mới.':'Chưa có tọa độ đã lưu. Cắm camera, nhận diện rồi bấm LƯU.');
 }
 return reasons.length?'Chưa gửi MOVE: '+reasons.join(' '):`Sẵn sàng gửi MOVE cho ID ${w.next_object_id}.`;
}
function render(data){
 state=data;const {workflow:w,robot:r,vision:v,calibration:c}=data;
 el('network').textContent='● Dashboard online';el('mode').textContent=r.mode;
 el('phase').textContent=w.phase;el('message').textContent=w.message;
 el('saved-count').textContent=w.saved.filter(t=>t.status==='SAVED').length;
 el('completed-count').textContent=w.completed_count;el('next-id').textContent=w.next_object_id==null?'—':'ID '+w.next_object_id;
 el('minimum').textContent=w.tracking.minimum_move_distance_mm+' mm';
 el('camera-status').textContent=v.connected?'Connected':'Disconnected';el('robot-status').textContent=r.connected?'Connected':'Disconnected';
 el('vision-info').textContent=`${v.mode} · ${v.fps} FPS · ${v.error}`;
 if(v.connected){el('preview').hidden=false;el('preview-empty').hidden=true;el('preview').src='/api/preview.jpg?t='+Date.now();}else{el('preview').hidden=true;el('preview-empty').hidden=false;}
 const flags=r.flags||{};
 el('flags').replaceChildren(...['servo','remote','play','teach','alarm','error','running','hold'].map(key=>{const s=document.createElement('span');s.className='flag'+(flags[key]?' on':'');s.textContent=key.toUpperCase()+': '+(flags[key]?'ON':'OFF');return s;}));
 el('pose').replaceChildren(...['x','y','z','rx','ry','rz'].map(key=>{const d=document.createElement('div'),label=document.createElement('span'),value=document.createElement('strong');label.textContent=key.toUpperCase();value.textContent=num(r.cartesian?.[key]);d.append(label,value);return d;}));
 el('motion').textContent=r.motion?`${r.motion.phase}: ${r.motion.message}`:'Chưa gửi MOVE';
 el('send').disabled=!r.connected||!w.next_record_id||!!w.active_id||w.phase==='FAULT';
 el('send-note').textContent=moveNote(w,r);
 el('capture').disabled=!w.can_capture;
 el('capture').title=w.capture_reason;
 el('vision-info').textContent+=` · ${w.capture_reason}`;
 table('saved',w.saved.map(s=>[s.target.object_id,s.target.name,s.target.xyz.map(num).join(' / '),s.target.orientation.map(num).join(' / '),num(s.speed),num(s.distance_last_mm),num(s.distance_same_id_mm),s.status+' · '+s.reason]));
 table('live',w.live.map(t=>[t.id,t.name,num(t.confidence),`${num(t.u)} / ${num(t.v)}`,(t.xyz||[]).map(num).join(' / '),t.reason]));
 el('saved-at').textContent=w.saved[0]?'Lưu lúc '+new Date(w.saved[0].saved_at).toLocaleString():'';
 el('storage').textContent=w.saved.length?'Tọa độ đã lưu trên đĩa; không mất khi rút dây camera.':'';
 el('calibration').textContent=`Calibration: ${w.calibration_valid?'đang dùng':'không hợp lệ'} · Ảnh gốc ${c.image_size?.join(' × ')||'—'} · Offset Base X +280 / Y +215 mm · ${c.message}`;
 if(!initialized){for(const [key,value]of Object.entries(w.tracking)){const l=document.createElement('label');l.textContent=labels[key]||key;const input=document.createElement('input');Object.assign(input,{name:key,type:'number',step:'any',value,required:true});l.append(input);el('config-form').append(l);}const button=document.createElement('button');button.textContent='ÁP DỤNG CẤU HÌNH';el('config-form').append(button);initialized=true;}
 if(data.events.length&&data.events.at(-1).id!==lastEvent){el('events').textContent=data.events.map(e=>`${e.time} ${e.level} ${e.message}`).join('\n');el('events').scrollTop=el('events').scrollHeight;lastEvent=data.events.at(-1).id;}
}
async function poll(){try{render(await api('state'));}catch(error){el('network').textContent='Mất kết nối dashboard';showError(error);}setTimeout(poll,400);}poll();
