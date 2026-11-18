/* Shared model for the schematic, truth tables, and clock controls. */
(() => {
  'use strict';

  const terms = { MGA: [1, 8, 9], MGR: [2, 4, 5], MDA: [2, 8, 10], MDR: [1, 4, 6] };
  const lessons = [
    { id: 'boolean', title: 'Boolean algebra', topic: 'Boolean algebra', inputs: ['A', 'M', 'C'], outputs: ['X'],
      expression: 'X = (M + M·C) + (A·M + A·C + A·M·C)',
      note: 'AND requires every input to be 1. OR requires at least one. Absorption reduces this network to X = M + A·C.' },
    { id: 'decoder', title: 'Decoder matrix', topic: 'Combinational logic', inputs: ['BA', 'BR', 'BG', 'BD'], outputs: Object.keys(terms),
      expression: 'sₙ = 1 when BA BR BG BD encodes n',
      note: 'BA is the most significant bit. Exactly one of the 16 decoder lines is selected. Each output ORs the three lines marked by its junction dots.' },
    { id: 'sequential', title: 'JK flip-flops', topic: 'Sequential logic', inputs: [], outputs: ['C', 'B', 'A'],
      expression: 'Q⁺ = J·Q̄ + K̄·Q',
      note: 'Each falling clock edge samples all three J and K pairs from the old state. The three outputs then change together.' },
    { id: 'clock', title: 'Clock frequency', topic: 'Clock timing', inputs: [], outputs: ['CLK'],
      expression: 'T = 1 / f',
      note: 'Frequency counts complete cycles per second. One step moves to the next edge, half a period later.' },
  ];

  function initial(id) {
    switch (id) {
      case 'boolean': return { A: 1, M: 0, C: 1 };
      case 'decoder': return { BA: 0, BR: 0, BG: 0, BD: 1 };
      case 'sequential': return { C: 0, B: 0, A: 0, ticks: 0 };
      case 'clock': return { hz: 1, phase: 0, ticks: 0 };
    }
  }
  const index = s => 8 * s.BA + 4 * s.BR + 2 * s.BG + s.BD;
  function jk({A, B, C}) {
    return { JA: B & (1-C), KA: 1, JB: +(A === C), KB: 1, JC: B & (1-A), KC: B | (1-A) };
  }
  function evaluate(id, s) {
    switch (id) {
      case 'boolean': return { X: s.M | (s.A & s.C) };
      case 'decoder': return Object.fromEntries(Object.entries(terms).map(([key, rows]) => [key, +rows.includes(index(s))]));
      case 'sequential': return { C: s.C, B: s.B, A: s.A };
      case 'clock': return { CLK: s.phase };
    }
  }
  function step(id, s) {
    if (id === 'clock') return {...s, ticks: s.ticks + 1, phase: 1 - s.phase};
    if (id !== 'sequential') return {...s};
    const pins = jk(s);
    const next = q => (pins['J'+q] & (1-s[q])) | ((1-pins['K'+q]) & s[q]);
    return {...s, C: next('C'), B: next('B'), A: next('A'), ticks: s.ticks + 1};
  }

  const ink = '#25343a', low = '#768187', high = '#13867c', chip = '#e5f5f1';
  const amber = '#fff1b9', yellow = '#fff7d9';
  const mono = "'IBM Plex Mono','Cascadia Mono',Consolas,monospace";
  const sans = "Inter,'Segoe UI',Arial,sans-serif";
  const sub = n => String(n).replace(/\d/g, d => '₀₁₂₃₄₅₆₇₈₉'[d]);
  const tone = v => v ? high : low;
  function label(x,y,text,opts={}) {
    const {size=14,align='middle',color=ink,weight=500,font=mono} = opts;
    return `<text x="${x}" y="${y}" text-anchor="${align}" dominant-baseline="middle" fill="${color}" font-family="${font}" font-size="${size}" font-weight="${weight}">${text}</text>`;
  }
  function path(d, stroke=low, width=2, fill='none') {
    return `<path d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`;
  }
  const wire = (d,v) => path(d,tone(v),v?2.7:2.15);
  const dot = (x,y,v,r=3.6) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${tone(v)}"/>`;
  function rect(x,y,w,h,fill,stroke=ink,r=4,width=1.8) {
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${width}"/>`;
  }
  function pin(x,y,name,value,editable=false,w=65) {
    const fill = value ? chip : '#f4f6f6', c = value ? high : low;
    const attrs = editable ? ` data-input="${name}" role="button" tabindex="0" aria-label="Toggle ${name}, currently ${value}" style="cursor:pointer"` : '';
    return `<g${attrs}><title>${editable?'Toggle input':'Output'} ${name}: ${value}</title>`+
      rect(x,y-14,w,28,fill,c,5,1.4)+label(x+10,y+.5,name,{size:13,align:'start',weight:650})+
      rect(x+w-23,y-9,16,18,value?high:'#e1e6e7', 'none',3)+
      label(x+w-15,y+.5,value,{size:12,color:value?'#fff':'#48565c',weight:700})+'</g>';
  }
  function gate(type,x,y,value,word='',scale=1) {
    const d = type === 'AND' ? 'M0 -20 H31 A20 20 0 0 1 31 20 H0 Z' :
      'M0 -20 Q30 -23 57 0 Q30 23 0 20 Q12 0 0 -20 Z';
    return `<g transform="translate(${x} ${y}) scale(${scale})"><title>${type} gate, output ${value}</title>`+
      path(d,value?high:ink,2,value?'#e7f7f3':'#fbfcfc')+
      (word?label(type==='AND'?23:27,1,word,{size:11,color:value?high:ink,weight:650}):'')+'</g>';
  }
  const levelDetail = level => level === 'signals';
  function booleanDiagram(s, level) {
    const {A,M,C}=s, am=A&M, mc=M&C, ac=A&C, amc=am&C;
    const upper=M|mc, lower=am|ac|amc, X=upper|lower;
    let g='';
    // Each input has its own bus. A crossing is a junction only where a dot appears.
    g+=wire('M88 43 H260',A)+wire('M117 43 V310 H260',A)+wire('M117 216 H260',A);
    g+=wire('M88 128 H260',M)+wire('M148 128 V65 H260',M)+wire('M148 128 V325 H260',M)+wire('M148 100 H468',M);
    g+=wire('M88 238 H260',C)+wire('M181 238 V150 H260',C)+wire('M181 238 V340 H260',C);
    g+=wire('M311 54 H360 V212 H468',am)+wire('M311 139 H407 V120 H468',mc);
    g+=wire('M311 227 H468',ac)+wire('M311 325 H407 V242 H468',amc);
    g+=wire('M520 110 H561 V154 H612',upper)+wire('M520 227 H561 V174 H612',lower)+wire('M665 164 H699',X);
    for (const [x,y,v] of [[117,43,A],[117,216,A],[148,128,M],[148,100,M],[181,238,C]]) g+=dot(x,y,v);
    for (const [y,v] of [[54,am],[139,mc],[227,ac],[325,amc]]) g+=gate('AND',260,y,v);
    // 3-input AND has a slightly taller body so all three terminals meet its flat face.
    g+=gate('OR',463,110,upper)+gate('OR',463,227,lower)+gate('OR',608,164,X);
    g+=pin(22,43,'A',A,true,66)+pin(22,128,'M',M,true,66)+pin(22,238,'C',C,true,66)+pin(699,164,'X',X,false,65);
    for(const [y,name,val] of [[54,'A·M',am],[139,'M·C',mc],[227,'A·C',ac],[325,'A·M·C',amc]]) {
      g+=label(286,y+34,name+(levelDetail(level)?' = '+val:''),{size:14,color:val?high:ink});
    }
    g+=label(496,76,levelDetail(level)?'M + M·C = '+upper:'M + M·C',{size:13});
    g+=label(493,264,levelDetail(level)?'A·M + A·C + A·M·C = '+lower:'A·M + A·C + A·M·C',{size:13});
    if(levelDetail(level)) g+=label(636,200,'X = '+X,{size:16,weight:650,color:X?high:ink});
    return g;
  }
  function decoderDiagram(s,level) {
    const n=index(s), outs=evaluate('decoder',s);
    const yrow=r=>40+r*13.9;
    let g=rect(135,22,142,245,amber,'#997f35',4);
    g+=label(204,146,'Decoder',{font:sans,size:18,weight:600})+label(204,167,'4 → 16',{size:12,color:'#70643e'});
    lessons[1].inputs.forEach((v,i)=>{
      const y=84+i*40;
      g+=pin(28,y,v,s[v],true,67)+wire(`M95 ${y} H135`,s[v])+label(146,y,'e'+sub(3-i),{align:'start',size:14});
    });
    const used = new Set(Object.values(terms).flat());
    for(let r=0;r<16;r++) {
      const y=yrow(r);
      g+=label(268,y,'s'+sub(r),{align:'end',size:12,color:r===n?high:ink,weight:r===n?750:450});
      g+=wire(`M277 ${y} H${used.has(r)?755:302}`,r===n);
    }
    Object.entries(terms).forEach(([name,rows],i)=>{
      const cx=360+i*102;
      rows.forEach((r,k)=>{
        const x=cx+(k-1)*16;
        g+=wire(`M${x} ${yrow(r)} V281`,r===n)+dot(x,yrow(r),r===n);
      });
      g+=`<g transform="translate(${cx} 276) rotate(90)">${path('M0 -24 Q30 -23 44 0 Q30 23 0 24 Q10 0 0 -24 Z',outs[name]?high:ink,1.8,outs[name]?chip:yellow)}</g>`;
      g+=wire(`M${cx} 320 V342`,outs[name])+pin(cx-36,355,name,outs[name],false,72);
      if(levelDetail(level)) g+=label(cx,379,'Σ('+rows.join(',')+')',{size:11,color:low});
    });
    return g;
  }
  function sequentialDiagram(s,level) {
    const {A,B,C}=s, p=jk(s), d=levelDetail(level);
    // Coordinates follow the reference: Q outputs are on the left, J/K on the right.
    let g=wire('M104 32 H503 V122 H463',0)+wire('M326 32 V122 H310',0)+wire('M173 32 V122 H156',0);
    g+=dot(173,32,0,2.5)+dot(326,32,0,2.5)+label(102,32,'Clock',{align:'end',size:13});
    const paths=[
      ['M73 79 H42 V297 H226',C], ['M73 165 H59 V328 H226',1-C],['M59 234 H226',1-C],
      ['M226 79 H206 V218 H226',B],['M206 218 H183 V406 H163',B],['M183 365 H166',B],
      ['M379 79 H367 V258 H206 V281 H226',A],['M379 165 H352 V396 H211 V344 H226',1-A],
      ['M211 380 H166',1-A],['M197 380 V420 H163',1-A],
      ['M262 226 H469 V79 H456',p.JA],['M262 290 H273 V303 H287',A&C],
      ['M262 336 H273 V322 H287',(1-A)&(1-C)],['M324 313 H336 V79 H304',p.JB],
      ['M130 373 H97 V197 H183 V79 H151',p.JC],['M125 414 H78 V218 H173 V165 H151',p.KC],
      ['M304 165 H317',1],['M456 165 H478',1]
    ];
    for(const [coords,v] of paths)g+=wire(coords,v);
    for(const [x,y,v] of [[59,234,1-C],[206,218,B],[183,365,B],[211,380,1-A],[197,380,1-A]]) g+=dot(x,y,v,2.8);
    // These mirrored gates face left towards the J and K pins of FF-C.
    g+=`<g transform="translate(166 373) scale(-.71 .78)">${gate('AND',0,0,p.JC)}</g>`;
    g+=`<g transform="translate(166 414) scale(-.72 .78)">${gate('OR',0,0,p.KC)}</g>`;
    for(const [y,v] of [[226,p.JA],[290,A&C],[336,(1-A)&(1-C)]]) g+=`<g transform="translate(226 ${y}) scale(.71 .79)">${gate('AND',0,0,v)}</g>`;
    g+=`<g transform="translate(283 313) scale(.72 .78)">${gate('OR',0,0,p.JB)}</g>`;
    for (const [x,q] of [[73,'C'],[226,'B'],[379,'A']]) {
      const v=s[q], end=x+78;
      g+=rect(x,68,78,108,'#f9fbfa',ink,2,1.7);
      g+=label(x+5,80,q+(d?'='+v:''),{size:12,align:'start',color:tone(v)})+
        label(x+5,165,q+'̄'+(d?'='+(1-v):''),{size:12,align:'start',color:tone(1-v)})+
        label(end-5,80,'J'+q+(d?'='+p['J'+q]:''),{size:11,align:'end'})+
        label(end-5,165,'K'+q+(d?'='+p['K'+q]:''),{size:11,align:'end'})+
        label(x+39,108,'FF-'+q,{size:15,weight:650})+label(end-16,123,'CLK',{size:10,align:'end'})+
        path(`M${end} 116 l-10 6 10 6`,ink,1.6)+`<circle cx="${end+3}" cy="122" r="2.8" fill="white" stroke="${ink}" stroke-width="1.5"/>`;
    }
    g+=label(321,165,'1',{size:12})+label(482,165,'1',{size:12});
    // Keep symbols and letters in proportion; the feedback network fills the bottom half.
    return `<g transform="translate(131 -9) scale(1.03 .90)">${g}</g>`;
  }
  function clockDiagram(s,level) {
    const hz=Math.max(.01,Number(s.hz)||1), t=1/hz, width=139;
    const time=n=>Number(n.toPrecision(3))+' s';
    const endTick=Math.max(6,s.ticks+1), startTick=endTick-6;
    const left=144, top=116, bottom=224, span=width*.68;
    let g=label(78,top,'HIGH · 1',{size:14,color:high})+label(78,bottom,'LOW · 0',{size:14,color:low});
    for(let k=0;k<=6;k++){
      const x=left+k*span, tick=k+startTick;
      g+=path(`M${x} 87 V259`,'#ced6d5',1);
      if(detailedTick(level,k))g+=label(x,277,time(tick*t/2),{size:13,color:low});
      if(k===6)break;
      const y=tick%2?top:bottom;
      g+=wire(`M${x} ${y} H${x+span} V${y===top?bottom:top}`,tick%2);
    }
    const marker=left+(s.ticks-startTick)*span;
    g+=dot(marker,s.phase?top:bottom,s.phase,6)+label(marker,64,'CLK = '+s.phase,{size:16,weight:650});
    const p0=left+(startTick%2?0:1)*span;
    g+=path(`M${p0} 308 V320 M${p0} 314 h${2*span} M${p0+2*span} 308 V320`,ink,1.4);
    g+=label(p0+span,343,'T = '+time(t),{size:16});
    return g;
  }
  const detailedTick=(level,k)=>level==='signals'||k%2===0;

  function overview(id,s) {
    if(id==='clock'){
      const hz=Math.max(.01,Number(s.hz)||1);
      return rect(223,125,354,138,yellow,'#9e905c',10)+label(400,163,hz+' Hz',{size:34,weight:650})+
        label(400,219,'1 cycle = '+Number((1/hz).toPrecision(3))+' s',{size:19});
    }
    const l=lessons.find(item=>item.id===id), out=evaluate(id,s);
    let g=rect(272,94,248,203,id==='decoder'?amber:'#edf6f3',ink,7,2);
    g+=label(396,175,l.title,{size:24,font:sans,weight:650});
    const summary={boolean:'X = M + A·C',decoder:'4 inputs → 16 lines',sequential:'3 state bits'};
    g+=label(396,214,summary[id],{size:17});
    if(id==='sequential')g+=wire('M125 195 H272',0)+label(90,195,'CLK ↓',{size:17});
    l.inputs.forEach((name,i)=>{
      const y=115+(i+0.5)*150/l.inputs.length;
      g+=pin(77,y,name,s[name],true,74)+wire(`M151 ${y} H272`,s[name]);
    });
    l.outputs.forEach((name,i)=>{
      const y=115+(i+.5)*150/l.outputs.length;
      g+=wire(`M520 ${y} H646`,out[name])+pin(646,y,name,out[name],false,79);
    });
    return g;
  }
  function draw(id,s,level='gates') {
    if(level==='overview')return overview(id,s);
    return {boolean:booleanDiagram,decoder:decoderDiagram,sequential:sequentialDiagram,clock:clockDiagram}[id](s,level);
  }
  window.CircuitLab={lessons,initial,evaluate,step,draw,terms,jk};
})();
