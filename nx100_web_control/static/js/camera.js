'use strict';
const el = id => document.getElementById(id);
const canvas = el('cameraCanvas'), ctx = canvas.getContext('2d');
let frame=null, image=null, selected=null, connected=false, frozen=false, frameRequest=false;
let conversionVersion=0, streamVersion=0, commandBusy=false;

async function call(path, body) {
  const response=await fetch(path,{method:body===undefined?'GET':'POST',
    headers:body===undefined?{}:{'Content-Type':'application/json','X-NX100-Control':'local'},
    body:body===undefined?undefined:JSON.stringify(body)});
  const result=await response.json();
  if(!response.ok)throw new Error(result.message||'Camera request failed');
  return result;
}
function fail(error){el('cameraError').textContent=error.message||String(error);}
function clearPoint(message='Chọn pixel để tính tọa độ.') {
  conversionVersion++;el('baseX').textContent=el('baseY').textContent=el('baseZ').textContent='—';
  el('pointPhase').textContent='NOT CALCULATED';el('pointMessage').textContent=message;
}
function buttons(){
  el('findCamera').disabled=commandBusy||connected;
  el('openCamera').disabled=commandBusy||connected||el('cameraDevice').value==='';
  el('closeCamera').disabled=commandBusy||!connected;
  el('live').disabled=!connected;el('live').textContent=frozen?'RESUME LIVE':'LIVE';
  el('convertPoint').disabled=!selected||!frame||el('planeZ').value==='';
}
function showStatus(status){
  connected=status.camera.connected;el('visionMode').textContent=status.mode;
  el('cameraStatus').textContent=status.camera.message;
  const calibration=status.calibration;
  if(!calibration){el('quality').textContent='Không đọc được calib: '+status.calibration_error;el('quality').classList.add('quality-bad');}
  else{
    const summary=calibration.residual_summary;
    const rms=summary.translation_error_mm?.rms, outliers=summary.outlier_count;
    el('quality').textContent=`${calibration.quality_status} · ${calibration.samples_used||'?'} mẫu`+
      (rms!==undefined?` · residual tịnh tiến RMS ${rms.toFixed(2)} mm`:'')+
      (outliers!==undefined?` · ${outliers} outlier`:'')+' · Tọa độ tính được chưa được đo kiểm độc lập.';
    el('quality').classList.toggle('quality-bad',calibration.quality_status!=='residual_checks_passed');
    el('calibrationSource').textContent=`${calibration.path} · ${calibration.image_width} × ${calibration.image_height} · Camera → BASE · mm`;
    el('calibrationDetails').textContent=JSON.stringify(calibration,null,2);
  }
  buttons();
}
function draw(){
  if(!image||!frame)return;
  ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(image,0,0,canvas.width,canvas.height);
  if(selected){
    const x=(selected.u+.5)*canvas.width/frame.width,y=(selected.v+.5)*canvas.height/frame.height;
    ctx.strokeStyle='#ffd166';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x-18,y);ctx.lineTo(x+18,y);ctx.moveTo(x,y-18);ctx.lineTo(x,y+18);ctx.stroke();
    ctx.beginPath();ctx.arc(x,y,9,0,Math.PI*2);ctx.stroke();
  }
}
async function fetchFrame(){
  if(!connected||frozen||frameRequest)return;
  frameRequest=true;const version=streamVersion;
  try{
    const next=await call('/api/vision/frame');
    const img=new Image();img.src=next.image_data;await img.decode();
    if(version!==streamVersion||frozen||!connected)return;
    frame=next;image=img;canvas.width=img.width;canvas.height=img.height;
    el('emptyCamera').hidden=true;draw();
    el('frameInfo').textContent=`${next.width} × ${next.height} raw · preview ${next.preview_width} × ${next.preview_height}`+
      (next.resolution_matches_calibration?'':' · KHÁC KÍCH THƯỚC CALIB — không tính XYZ');
    el('cameraError').textContent='';
  }catch(error){fail(error);}finally{frameRequest=false;}
}
async function stream(){await fetchFrame();setTimeout(stream,250);}
async function convert(){
  clearPoint();const version=conversionVersion;
  if(!selected||!frame)return;
  if(el('planeZ').value===''||!Number.isFinite(el('planeZ').valueAsNumber)){
    el('pointMessage').textContent='Đã chọn pixel. Nhập Z mặt vật trong hệ BASE để tính XYZ.';return;
  }
  el('pointPhase').textContent='CALCULATING…';
  try{
    const result=await call('/api/vision/pixel-to-base',{frame_id:frame.frame_id,...selected,plane_z_mm:el('planeZ').valueAsNumber});
    if(version!==conversionVersion)return;
    for(const axis of ['x','y','z'])el('base'+axis.toUpperCase()).textContent=result.base_mm[axis].toFixed(3);
    el('pointPhase').textContent=result.mode==='MOCK'?'MOCK ESTIMATE':result.quality_status==='needs_review'?'ESTIMATE · NEEDS REVIEW':'BASE POINT · CHECK ACCURACY';
    el('pointMessage').textContent=`Giao điểm tại Z BASE = ${result.plane_z_mm} mm. Pixel (${result.pixel.u}, ${result.pixel.v}). Không gửi lệnh robot; RX/RY/RZ không xác định từ pixel.`;
    el('cameraError').textContent='';
  }catch(error){if(version===conversionVersion){el('pointPhase').textContent='CANNOT CONVERT';fail(error);}}
}
canvas.addEventListener('click',event=>{
  if(!frame||!image||!connected)return;
  const rect=canvas.getBoundingClientRect();
  const u=Math.min(frame.width-1,Math.max(0,Math.floor((event.clientX-rect.left)*frame.width/rect.width)));
  const v=Math.min(frame.height-1,Math.max(0,Math.floor((event.clientY-rect.top)*frame.height/rect.height)));
  frozen=true;streamVersion++;selected={u,v};el('pixelValue').textContent=`u ${u} / v ${v}`;
  draw();buttons();convert();
});
el('planeZ').addEventListener('input',()=>{clearPoint('Độ cao đã đổi. Nhấn Enter hoặc CALCULATE XYZ để tính lại.');buttons();});
el('planeZ').addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.repeat){event.preventDefault();convert();}});
el('convertPoint').onclick=convert;
el('live').onclick=()=>{frozen=false;streamVersion++;selected=null;el('pixelValue').textContent='u — / v —';clearPoint();buttons();fetchFrame();};
async function cameraAction(task){
  if(commandBusy)return;commandBusy=true;buttons();
  try{await task();el('cameraError').textContent='';}catch(error){fail(error);}finally{commandBusy=false;buttons();}
}
el('findCamera').onclick=()=>cameraAction(async()=>{
  const result=await call('/api/vision/enumerate',{});el('cameraDevice').replaceChildren();
  for(const device of result.devices){const option=document.createElement('option');option.value=device.index;option.textContent=device.name;el('cameraDevice').append(option);}
  if(!result.devices.length){const option=document.createElement('option');option.value='';option.textContent='Không tìm thấy camera';el('cameraDevice').append(option);}
});
el('cameraDevice').onchange=buttons;
el('openCamera').onclick=()=>cameraAction(async()=>{
  const status=await call('/api/vision/connect',{index:Number(el('cameraDevice').value)});showStatus(status);
  frozen=false;streamVersion++;selected=null;clearPoint();await fetchFrame();
});
el('closeCamera').onclick=()=>cameraAction(async()=>{
  streamVersion++;frozen=true;frame=null;image=null;selected=null;clearPoint();
  showStatus(await call('/api/vision/disconnect',{}));ctx.clearRect(0,0,canvas.width,canvas.height);el('emptyCamera').hidden=false;el('pixelValue').textContent='u — / v —';
});
el('reloadCalibration').onclick=()=>cameraAction(async()=>{
  streamVersion++;selected=null;frame=null;image=null;clearPoint();el('pixelValue').textContent='u — / v —';
  showStatus(await call('/api/vision/reload',{}));frozen=false;await fetchFrame();
});
async function init(){
  try{const status=await call('/api/vision/status');showStatus(status);if(status.plane_z_mm!==null&&status.plane_z_mm!==undefined)el('planeZ').value=status.plane_z_mm;}
  catch(error){fail(error);}stream();
}
init();
