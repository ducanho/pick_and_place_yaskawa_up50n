'use strict';
const $=id=>document.getElementById(id);
const flagNames=['servo','remote','play','teach','alarm','error','running','hold'];
const axes=['x','y','z','rx','ry','rz'];
let state=null,pending=false,initialized=false,uiError='',claimAttempted=false;
const tri=v=>v===true?'ON':v===false?'OFF':'UNKNOWN';
const text=(id,value)=>{$(id).textContent=value;};
let stackCountDirty=false;
async function claimControl(){
const send=token=>fetch('/api/control/claim',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})});
let response=await send('');
if(response.status===403){
const token=window.prompt('Nhập mã điều khiển HMI');
if(token!==null)response=await send(token);
}
if(!response.ok){const result=await response.json();throw Error(result.detail||'Không nhận được quyền điều khiển');}
}
function renderLaser(robot){
text('laser',tri(robot.laser));$('laser').className=robot.laser===true?'on':robot.laser===false?'off':'unknown';
for(let i=0;i<2;i++){
const value=robot.vacuum_inputs?.[i]??(Number.isInteger(robot.laser_raw_byte)?Boolean(robot.laser_raw_byte&(1<<(i+1))):null);
const el=$(`pressure${i+1}`);
el.textContent=tri(value);el.className=value===true?'on':value===false?'off':'unknown';
}
}
function renderDrop(s){
const d=s.drop_height;
if(!d)return;
text('firstDropZ',d.first_drop_z_mm);text('dropThickness',d.board_thickness_mm);
if(!stackCountDirty)$('stackedCount').value=d.stacked_count;
const labels={IDLE:'Đang chờ',COMPLETE:'Hoàn tất',FAULT:'Có lỗi',HOLD:'Tạm dừng',SYSTEM_CHECK:'Đang kiểm tra',WAIT_TARGET:'Đang tìm ván',MOVE_XY:'Đang đến vị trí gắp',START_MOVEUNTI:'Đang tìm Z',Z_DESCENDING:'Đang tìm Z',VACUUM_ACTIVATING:'Đang bật hút',WRITING_DROP_P010:'Đang ghi vị trí thả',DROP_P010_WRITTEN:'Đã ghi vị trí thả',WAIT_DROP_POSITION:'Đang đến vị trí thả',WAIT_DROP_SAFE:'Đang đến điểm an toàn',DROP_SAFE_REACHED:'Đã đến điểm an toàn',CALCULATE_DROP_Z:'Đang tính Z thả',MOVING_TO_DROP_Z:'Đang hạ ván',DROP_Z_REACHED:'Đã đến Z thả',EXECUTING_H2OFF:'Đang nhả ván',H2OFF_COMPLETE:'Đã nhả ván',AWAIT_DROP_CONFIRMATION:'Đã nhả ván',STACK_COUNT_UPDATED:'Đã cập nhật số tấm',POST_H2OFF_MOVE:'Đang nâng đầu hút'};
text('dropStatus',labels[s.state]||(s.busy?'Đang chạy':'Đang chờ'));
const editable=!pending&&s.control&&!s.busy&&['IDLE','COMPLETE'].includes(s.state);
$('resetStack').disabled=!editable;
$('stackedCount').disabled=!editable;$('saveStackCount').disabled=!editable;
}
for(const key of flagNames){const box=document.createElement('div');box.className='flag';box.innerHTML=`<span>${key.toUpperCase()}</span><b id="flag-${key}">UNKNOWN</b>`;$('flags').append(box);}
for(const key of axes){const box=document.createElement('div');box.className='axis';box.innerHTML=`<span>${key.toUpperCase()}</span><b id="pos-${key}">—</b>`;$('position').append(box);}
async function refresh(){try{const r=await fetch('/api/state');if(!r.ok)throw Error('Mất kết nối server');state=await r.json();if(!state.control&&!claimAttempted){claimAttempted=true;await claimControl();const latest=await fetch('/api/state');if(!latest.ok)throw Error('HMI state unavailable');state=await latest.json();}render();}catch(e){uiError=e.message;text('notice',uiError);text('ready','UNKNOWN');for(const k of flagNames)text(`flag-${k}`,'UNKNOWN');document.querySelectorAll('button').forEach(b=>b.disabled=true);text('laser','UNKNOWN');renderLaser({});$('preview').style.display='none';}}
function render(){const s=state;const connected=s.robot.connected&&s.camera.connected;const gate=s.capabilities.full_cycle;const ready=gate.allowed&&connected&&s.state==='IDLE'&&['servo','remote','play'].every(k=>s.robot.flags[k]===true)&&['teach','alarm','error','running','hold'].every(k=>s.robot.flags[k]===false);text('mode',s.mode);text('robotLink',`ROBOT ${s.robot.connected?'ONLINE':'OFFLINE'}`);text('cameraLink',`CAMERA ${s.camera.connected?'ONLINE':'OFFLINE'}`);text('ready',s.state==='FAULT'?'FAULT':s.busy?'BUSY':ready?'READY':'NOT READY');text('state',s.state);text('lease',s.control?'Đang giữ quyền điều khiển':'Chỉ xem');text('fps',`${s.camera.fps} FPS`);
for(const k of flagNames){const el=$(`flag-${k}`),v=s.robot.flags[k];el.textContent=tri(v);el.className=v===true?'on':v===false?'off':'unknown';}
for(const k of axes)text(`pos-${k}`,s.robot.position?Number(s.robot.position[k]).toFixed(2):'—');
text('target',s.target?['x','y','z'].map(a=>s.target.pose[a].toFixed(1)).join(' / '):'— / — / —');text('laser',tri(s.robot.laser));renderLaser(s.robot);
text('notice',uiError||s.error||s.robot.error||gate.reason||s.real_limit||(s.state==='JOB_DISPATCHED'?`Đã gửi START ${s.job_dispatch?.name||'MOVEUNTI'}. Robot có thể vẫn đang chạy JOB.`:s.state==='COMPLETE'?(s.drop_release?.counted||s.drop_release?.board_release_confirmed?'Cycle hoàn tất · H2OFF đã xong, bộ đếm đã cập nhật':'Cycle hoàn tất'):s.mode==='MOCK'?'MOCK · Camera và robot được mô phỏng.':'REAL · Xác minh khu vực trước khi điều khiển.'));
if(!uiError&&!s.error&&!s.robot.error&&s.state==='COMPLETE'&&s.stop_reason==='no_boards')text('notice',`Đã dừng: không còn phát hiện ván · Đã xếp ${s.drop_height.stacked_count} tấm`);
const detections=s.camera.detections||[];text('detected',detections.length?detections.map(d=>`ID ${d.id} · ${(100*d.confidence).toFixed(0)}%`).join('   /   '):'Chưa có vật hợp lệ');text('calib',s.mode==='MOCK'?'MOCK · tọa độ mô phỏng':`Calibration: ${s.camera.calibration}`);
if(s.camera.connected){$('preview').src=`/api/preview.jpg?t=${Date.now()}`;$('preview').style.display='block';$('cameraNote').style.display='none';}else{$('preview').style.display='none';$('cameraNote').style.display='block';}
if(!initialized){for(const [key,value]of Object.entries(s.settings)){const input=$('settings').elements[key];if(input)input.value=value;};initialized=true;}
document.querySelectorAll('button').forEach(b=>b.disabled=pending||!s.control);$('start').disabled=pending||!s.control||!ready||stackCountDirty;$('connect').disabled=pending||!s.control||s.busy;$('ack').disabled=pending||!s.control||s.busy||s.robot.flags.running!==false||!['COMPLETE','JOB_DISPATCHED','HOLD','FAULT'].includes(s.state);
const releasing=s.robot.flags.hold_command===true;
text('hold',releasing?'UNHOLD':'HOLD');
$('hold').className=releasing?'releaseHold':'holdButton';
$('hold').setAttribute('aria-pressed',String(releasing));
$('hold').disabled=pending||!s.control||(releasing&&!s.capabilities.release_hold.allowed);
$('hold').title=releasing?(s.capabilities.release_hold.reason||'Nhả command HOLD'):'';
document.querySelectorAll('[data-channel]').forEach(b=>b.disabled=pending||!s.control||s.busy||!(s.capabilities.manual_vacuum||s.capabilities.vacuum_only).allowed||!['IDLE','COMPLETE'].includes(s.state));
for(const el of $('settings').elements)el.disabled=pending||!s.control||s.state!=='IDLE';
renderDrop(s);

}
async function command(path,extra={}){if(pending||!state)return;pending=true;uiError='';render();try{const body={request_id:crypto.randomUUID(),revision:state.revision,...extra};const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const result=await r.json();if(!r.ok)throw Error(result.detail||'Yêu cầu thất bại');}catch(e){uiError=e.message;}finally{pending=false;await refresh();}}

$('connect').onclick=()=>command('/api/system/connect');$('start').onclick=()=>command('/api/cycle/start',{stage:'full_cycle'});$('ack').onclick=()=>command('/api/cycle/acknowledge',{inspected:true});
document.querySelectorAll('[data-channel]').forEach(b=>b.onclick=()=>command(`/api/vacuum/${b.dataset.channel}`,{on:b.dataset.on==='true'}));
$('hold').onclick=()=>{
if(state.robot.flags.hold_command!==true){command('/api/cycle/hold');return;}
if(!state.capabilities.release_hold.allowed)return;
if(window.confirm('Nhả HOLD có thể cho phép chuyển động đang treo tiếp tục. Xác nhận khu vực đã sẵn sàng và gửi NHẢ HOLD?'))command('/api/cycle/release-hold',{confirmed:true});
};
$('settings').onsubmit=e=>{e.preventDefault();const settings={};for(const [k,v]of new FormData(e.target))settings[k]=Number(v);command('/api/config',{settings});};
$('resetStack').onclick=()=>{if(window.confirm('Đặt STACKED COUNT về 0 và Z thả tiếp theo về 330 mm?')){stackCountDirty=false;command('/api/drop/reset',{confirmed:true});};};
$('stackedCount').oninput=()=>{stackCountDirty=true;if(state)render();};
$('stackedCount').onkeydown=e=>{if(e.key==='Escape'){stackCountDirty=false;if(state)render();}};
$('stackCountForm').onsubmit=async e=>{
e.preventDefault();if(!$('stackCountForm').reportValidity())return;
const count=Number($('stackedCount').value);
if(!Number.isSafeInteger(count)||count<0)return;
await command('/api/drop/count',{stacked_count:count});
if(!uiError){stackCountDirty=false;render();}
};
setInterval(()=>{if(!pending)refresh();},500);refresh();


