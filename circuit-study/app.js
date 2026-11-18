(() => {
  'use strict';
  const { lessons, initial, evaluate, step, draw } = window.CircuitLab;
  const byId = id => document.getElementById(id);
  const meta = {
    boolean: ['Boolean network','Boolean gate network','Trace three inputs through an AND–OR network to find the output.'],
    decoder: ['Decoder matrix','4-to-16 decoder','Follow one selected decoder line through the matrix to its outputs.'],
    sequential: ['JK flip-flops','JK flip-flop network','Step the clock to see how feedback determines the next three-bit state.'],
    clock: ['Clock waveform','Clock frequency','Explore how frequency in hertz changes the time between clock edges.']
  };
  const shapes = {
    network:'<path d="M2 5h5v5h5m-10 9h5v-5h5m0-7h4a5 5 0 0 1 0 10h-4zM21 12h2"/>',
    decoder:'<rect x="4" y="4" width="10" height="16" rx="1"/><path d="M1 9h3m-3 6h3m10-9h7m-7 4h7m-7 4h7m-7 4h7"/>',
    sequential:'<path d="M1 9h3m7 4h3m7-4h2M4 5h7v13H4zM14 5h7v13h-7zM7 18v3h10v-3"/>',
    clock:'<path d="M1 16h4V6h6v10h6V6h6"/>',
    library:'<rect x="3" y="4" width="4" height="16" rx="1"/><path d="M10 4v16m3-15 4-1 4 15-4 1z"/>',
    layers:'<path d="m3 8 9-5 9 5-9 5zm0 4 9 5 9-5m-18 5 9 5 9-5"/>',
    sliders:'<path d="M4 6h4m4 0h8M4 12h10m4 0h2M4 18h3m4 0h9"/><circle cx="10" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="9" cy="18" r="2"/>',
    reset:'<path d="M4 10a8 8 0 1 1 2 8M4 4v6h6"/>',
    cards:'<rect x="6" y="7" width="14" height="13" rx="2"/><path d="M3 15V4h13M10 11h6m-6 4h3"/>',
    keyboard:'<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M6 10h.1m4 0h.1m4 0h.1m4 0h.1M7 15h10"/>',
    left:'<path d="m14 6-6 6 6 6"/>',right:'<path d="m9 6 6 6-6 6"/>',
    plus:'<path d="M5 12h14M12 5v14"/>',minus:'<path d="M5 12h14"/>',
    fit:'<path d="M3 9V3h6m6 0h6v6m0 6v6h-6m-6 0H3v-6"/>',
    guide:'<path d="M3 4q5-1 9 2 4-3 9-2v14q-5-1-9 2-4-3-9-2zM12 6v14"/>',
    table:'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M3 15h18M10 4v16"/>'
  };
  function icon(name) {
    return '<svg aria-hidden="true" viewBox="0 0 24 24">'+shapes[name]+'</svg>';
  }
  document.querySelectorAll('i[data-icon]').forEach(el=>el.innerHTML=icon(el.dataset.icon));
  const stateById=Object.fromEntries(lessons.map(l=>[l.id,initial(l.id)]));
  const levels=[['overview','Block overview',65],['gates','Gate view',100],['signals','Signal detail',150]];
  let lesson, tab='Guide', hz=1, timer=null, zoom=1, cx=400, cy=195;
  const canvas=byId('canvas'), svg=byId('diagram');
  const state=()=>stateById[lesson.id];
  const currentLevel=()=>zoom<0.81?'overview':zoom<1.3?'gates':'signals';
  const tabNames=()=>lesson.id==='clock'?['Guide','Timing','Practice']:lesson.id==='sequential'?['Guide','State table','Timing','Practice']:['Guide','Truth table','Practice'];
  const libraryIcons=['network','decoder','sequential','clock'];
  byId('library').innerHTML=lessons.map((l,i)=>'<button class="lesson-link" data-id="'+l.id+'"><span class="mini-icon">'+icon(libraryIcons[i])+'</span><span><strong>'+meta[l.id][0]+'</strong><small>'+l.topic+'</small></span></button>').join('');
  byId('levels').innerHTML=levels.map(([key,name,pct])=>'<button class="level-btn" data-level="'+key+'"><span></span>'+name+'<em>'+pct+'%</em></button>').join('');
  function pause(){clearInterval(timer);timer=null;}
  function selectLesson(id){
    pause();lesson=lessons.find(l=>l.id===id)||lessons[0];
    zoom=1;cx=400;cy=195;tab='Guide';
    document.querySelectorAll('.lesson-link').forEach(btn=>btn.setAttribute('aria-current',String(btn.dataset.id===lesson.id)));
    const i=lessons.indexOf(lesson);
    byId('title').textContent=meta[lesson.id][1];byId('subtitle').textContent=meta[lesson.id][2];
    byId('topic').textContent=lesson.topic;byId('position').textContent=(i+1)+' / '+lessons.length;
    byId('figure').textContent='FIG. '+String(i+1).padStart(2,'0');
    svg.setAttribute('aria-label',meta[lesson.id][1]+', interactive schematic');
    document.title=meta[lesson.id][1]+' · Logic Atlas';
    renderTabs();render();
  }
  function navigate(id){if(location.hash.slice(1)!==id)location.hash=id;else selectLesson(id);}
  window.addEventListener('hashchange',()=>selectLesson(location.hash.slice(1)));
  byId('library').onclick=e=>{const b=e.target.closest('[data-id]');if(b) navigate(b.dataset.id);};
  byId('previous').onclick=()=>navigate(lessons[(lessons.indexOf(lesson)+3)%4].id);
  byId('next').onclick=()=>navigate(lessons[(lessons.indexOf(lesson)+1)%4].id);
  function view(){
    const w=800/zoom,h=390/zoom;
    cx=Math.max(0,Math.min(800,cx));cy=Math.max(0,Math.min(390,cy));
    svg.setAttribute('viewBox',[cx-w/2,cy-h/2,w,h].join(' '));
    byId('zoom-num').textContent=Math.round(zoom*100)+'%';
    byId('minus').disabled=zoom<=.55;byId('plus').disabled=zoom>=3;
    const level=currentLevel();byId('level-name').textContent=levels.find(l=>l[0]===level)[1];
    document.querySelectorAll('[data-level]').forEach(b=>{b.classList.toggle('active',b.dataset.level===level);b.setAttribute('aria-pressed',b.dataset.level===level);});
  }
  function diagram(){svg.innerHTML=draw(lesson.id,state(),currentLevel());view();}
  function setZoom(z,anchor){
    const before=currentLevel(),old=zoom;zoom=Math.max(.55,Math.min(3,z));
    if(anchor){cx=anchor.x+(cx-anchor.x)*old/zoom;cy=anchor.y+(cy-anchor.y)*old/zoom;}
    if(currentLevel()!==before)diagram();else view();
  }
  function fit(){cx=400;cy=195;setZoom(1);}
  byId('minus').onclick=()=>setZoom(zoom-.2);byId('plus').onclick=()=>setZoom(zoom+.2);byId('fit').onclick=fit;
  byId('levels').onclick=e=>{const b=e.target.closest('[data-level]');if(b){cx=400;cy=195;setZoom(levels.find(l=>l[0]===b.dataset.level)[2]/100);}};
  function svgPoint(x,y){return new DOMPoint(x,y).matrixTransform(svg.getScreenCTM().inverse());}
  canvas.addEventListener('wheel',e=>{
    if(e.target.closest('.canvas-tools'))return;
    e.preventDefault();const delta=e.deltaY*(e.deltaMode===1?16:1);
    setZoom(zoom*Math.exp(-Math.max(-220,Math.min(220,delta))*.002),svgPoint(e.clientX,e.clientY));
  },{passive:false});
  const pointers=new Map();let gesture;
  function baseline(){
    const p=[...pointers.values()];
    if(!p.length){gesture=null;canvas.classList.remove('dragging');return;}
    const a=p[0],b=p[1]||a,mid={x:(a.x+b.x)/2,y:(a.y+b.y)/2};
    gesture={...mid,scale:svg.getScreenCTM().a,dist:Math.hypot(a.x-b.x,a.y-b.y),cx,cy,zoom,anchor:svgPoint(mid.x,mid.y)};
  }
  canvas.onpointerdown=e=>{
    if(e.button!==0||e.target.closest('.canvas-tools'))return;
    pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,initialX:e.clientX,initialY:e.clientY,input:e.target.closest('[data-input]')?.dataset.input});
    if(pointers.size>1)for(const p of pointers.values())p.input=null;
    canvas.setPointerCapture(e.pointerId);baseline();
  };
  canvas.onpointermove=e=>{
    const p=pointers.get(e.pointerId);if(!p||!gesture)return;
    p.x=e.clientX;p.y=e.clientY;if(Math.hypot(p.x-p.initialX,p.y-p.initialY)>4){p.input=null;canvas.classList.add('dragging');}
    const [a,b]=[...pointers.values()];
    if(b&&gesture.dist>0){
      const midX=(a.x+b.x)/2,midY=(a.y+b.y)/2;
      setZoom(gesture.zoom*Math.hypot(a.x-b.x,a.y-b.y)/gesture.dist);
      cx=gesture.anchor.x+(gesture.cx-gesture.anchor.x-(midX-gesture.x)/gesture.scale)*gesture.zoom/zoom;
      cy=gesture.anchor.y+(gesture.cy-gesture.anchor.y-(midY-gesture.y)/gesture.scale)*gesture.zoom/zoom;
    }else{cx=gesture.cx-(p.x-gesture.x)/gesture.scale;cy=gesture.cy-(p.y-gesture.y)/gesture.scale;}
    view();
  };
  canvas.onpointerup=e=>{const p=pointers.get(e.pointerId);pointers.delete(e.pointerId);baseline();if(p?.input)setInput(p.input,1-state()[p.input]);};
  canvas.onpointercancel=e=>{pointers.delete(e.pointerId);baseline();};
  svg.addEventListener('keydown',e=>{const b=e.target.closest('[data-input]');if(b&&[' ','Enter'].includes(e.key)){e.preventDefault();setInput(b.dataset.input,1-state()[b.dataset.input]);svg.querySelector('[data-input="'+b.dataset.input+'"]')?.focus();}});
  function renderTabs(){
    const icons={'Guide':'guide','Truth table':'table','State table':'table','Practice':'cards','Timing':'clock'};
    byId('tabs').innerHTML=tabNames().map(name=>'<button role="tab" id="tab-'+name.split(' ')[0]+'" aria-controls="notes" aria-selected="'+(name===tab)+'" data-tab="'+name+'"><i data-icon>'+icon(icons[name])+'</i>'+(name==='Guide'?'Study guide':name)+'</button>').join('');
    byId('notes').setAttribute('aria-labelledby','tab-'+tab.split(' ')[0]);
  }
  function notes(){Notebook.renderTab(byId('notes'),tab,lesson,state(),setInput,hz,values=>{Object.assign(state(),values);render();});}
  function setTab(name){tab=name;renderTabs();notes();}
  byId('tabs').onclick=e=>{const b=e.target.closest('[data-tab]');if(b){setTab(b.dataset.tab);byId('tabs').querySelector('[aria-selected=true]').focus({preventScroll:true});}};
  byId('tabs').onkeydown=e=>{
    if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;
    e.preventDefault();const names=tabNames();setTab(names[(names.indexOf(tab)+(e.key==='ArrowRight'?1:names.length-1))%names.length]);
    byId('tabs').querySelector('[aria-selected=true]').focus();
  };
  byId('jump-practice').onclick=()=>{setTab('Practice');byId('notes').scrollIntoView({block:'center'});byId('notes').focus({preventScroll:true});};
  function setInput(key,val){if(lesson.inputs.includes(key)){state()[key]=val?1:0;render();}}
  function tick(){stateById[lesson.id]=step(lesson.id,state());render();}
  function play(){if(timer)pause();else timer=setInterval(tick,1000/hz/(lesson.id==='clock'?2:1));render();}
  function inspector(){
    const root=byId('signals'),focusKey=root.contains(document.activeElement)?document.activeElement.dataset.focus:null;
    const s=state(),outs=evaluate(lesson.id,s);
    const section=(label,inner)=>'<div class="signal-section"><div class="small-label">'+label+'</div>'+inner+'</div>';
    let html='';
    if(lesson.inputs.length){
      html+=section('Inputs',lesson.inputs.map(k=>'<div class="in-row"><strong class="in-name">'+k+'</strong><div class="bits" role="group" aria-label="Input '+k+'">'+[0,1].map(n=>'<button data-key="'+k+'" data-val="'+n+'" data-focus="'+k+n+'" aria-label="Set '+k+' to '+n+'" aria-pressed="'+(s[k]===n)+'" class="'+(s[k]===n?n?'is-on':'is-off':'')+'">'+n+'</button>').join('')+'</div></div>').join(''));
    }else{
      html+=section('Clock controls','<label class="clk-select">Frequency<select aria-label="Clock frequency" data-focus="hz" id="hz">'+[.5,1,2,4].map(n=>'<option value="'+n+'" '+(hz===n?'selected':'')+'>'+n+' Hz</option>').join('')+'</select></label><div class="step-buttons"><button data-action="step" data-focus="step">'+(lesson.id==='clock'?'Step edge':'Clock ↓')+'</button><button data-action="play" data-focus="play">'+(timer?'Pause':'Run')+'</button></div><span class="tick-count">'+s.ticks+(lesson.id==='clock'?' edges':' falling edges')+'</span>');
    }
    const outputRows=Object.entries(outs).map(([name,val])=>'<div class="out-row '+(val?'high':'')+'"><strong>'+name+'</strong><span>'+(val?'High':'Low')+'</span><b>'+val+'</b></div>').join('');
    html+=section(lesson.outputs.length>1?'Outputs':'Output','<div class="'+(lesson.outputs.length>2?'many-outputs':'')+'">'+outputRows+'</div>');
    let formula={boolean:'X = M + A·C',decoder:'s'+(8*s.BA+4*s.BR+2*s.BG+s.BD)+' is active',sequential:'Q⁺ = J·Q̄ + K̄·Q',clock:'T = '+(1/hz)+' s'}[lesson.id];
    html+='<div class="formula"><div class="small-label">'+({boolean:'Simplified expression',decoder:'Selected line',sequential:'Next-state rule',clock:'Period'}[lesson.id])+'</div><p>'+formula+'</p></div>';
    root.innerHTML=html;if(focusKey)root.querySelector('[data-focus="'+focusKey+'"]')?.focus({preventScroll:true});
  }
  byId('signals').onclick=e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.key)setInput(b.dataset.key,Number(b.dataset.val));else if(b.dataset.action==='play')play();else if(b.dataset.action==='step'){pause();tick();}};
  byId('signals').onchange=e=>{if(e.target.id==='hz'){const wasPlaying=!!timer;pause();hz=Number(e.target.value);if(lesson.id==='clock')stateById.clock={...initial('clock'),hz};if(wasPlaying)play();else render();}};
  byId('reset').onclick=()=>{pause();stateById[lesson.id]=initial(lesson.id);if(lesson.id==='clock')state().hz=hz;render();};
  function render(){if(lesson.id==='clock')state().hz=hz;diagram();inspector();notes();}
  const dialog=byId('shortcuts');
  byId('help-open').onclick=()=>dialog.showModal();byId('help-close').onclick=()=>dialog.close();
  dialog.onclick=e=>{if(e.target===dialog&&!e.target.closest('.dialog-head')){const r=dialog.getBoundingClientRect();if(e.clientY<r.top||e.clientY>r.bottom||e.clientX<r.left||e.clientX>r.right)dialog.close();}};
  document.addEventListener('keydown',e=>{
    if(e.ctrlKey||e.altKey||e.metaKey||dialog.open||e.target.closest('input,select,textarea,[contenteditable=true]'))return;
    if(e.key==='+'||e.key==='='){e.preventDefault();setZoom(zoom+.2);}
    else if(e.key==='-'){e.preventDefault();setZoom(zoom-.2);}
    else if(e.key==='0'){e.preventDefault();fit();}
    else if(canvas.contains(e.target)&&e.key.startsWith('Arrow')){e.preventDefault();cx+=({'ArrowRight':45,'ArrowLeft':-45}[e.key]||0)/zoom;cy+=({'ArrowDown':45,'ArrowUp':-45}[e.key]||0)/zoom;view();}
  });
  selectLesson(location.hash.slice(1));
})();
