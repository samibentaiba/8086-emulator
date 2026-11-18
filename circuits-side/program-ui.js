(() => {
  const $ = id => document.getElementById(id);
  const escape = value => String(value).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
  const samples = {
    sum: "; Add 1 + 2 + 3 + 4 + 5\nMOV AX, 0\nMOV BX, 1\nMOV CX, 5\nagain:\n    ADD AX, BX\n    INC BX\n    LOOP again\nHLT",
    memory: "; Store a word, then read it through ES:[BP+SI+6]\nMOV AX, 3000h\nMOV ES, AX\nMOV BP, 100h\nMOV SI, 4\nMOV WORD PTR ES:[BP+SI+6], 1234h\nMOV AX, 1\nADD AX, ES:[BP+SI+6]\nHLT",
    call: "; CALL pushes the byte address of the return instruction\nMOV SP, 0FFFEh\nMOV AX, 5\nCALL double_value\nHLT\ndouble_value:\n    PUSH BX\n    MOV BX, AX\n    ADD AX, BX\n    POP BX\n    RET",
    sort: "ASSUME CS:CODE,DS:DATA\nDATA SEGMENT\n    VAL DB 0FEh,27h,10h,0A2h,6Ch,110b\n    COUNT DW 6\nDATA ENDS\nCODE SEGMENT\nSTART:\n    MOV AX,DATA\n    MOV DS,AX\n    MOV CX,COUNT\n    DEC CX\nNEXTSCAN:\n    MOV BX,CX\n    MOV SI,0\nNEXTCOMP:\n    MOV AL,VAL[SI]\n    MOV DL,VAL[SI+1]\n    CMP AL,DL\n    JC NOSWAP\n    MOV VAL[SI],DL\n    MOV VAL[SI+1],AL\nNOSWAP:\n    INC SI\n    DEC BX\n    JNZ NEXTCOMP\n    LOOP NEXTSCAN\n    HLT\nCODE ENDS\nEND START"
  };
  let mode = "registers";
  let memoryAddress = 0x20000;
  let requestVersion = 0;
  let previousListing = null;
  let compiling = false;
  $("assemblySource").value = samples.sum;
  const programOption = document.createElement("option");
  programOption.value = "PROGRAM";
  programOption.textContent = "My assembly program";
  if (!$("traceProgram").querySelector('[value="PROGRAM"]')) $("traceProgram").append(programOption);

  function open() {
    $("programDock").hidden = false;
    document.body.classList.add("code-open");
    $("programToggle").setAttribute("aria-expanded","true");
    $("assemblySource").focus({preventScroll:true});
    atlasUI.refresh();
  }
  $("programToggle").onclick = () => {
    if ($("programDock").hidden) open();
    else {
      $("programDock").hidden = true;
      document.body.classList.remove("code-open");
      $("programToggle").setAttribute("aria-expanded","false");
    }
  };
  async function assemble() {
    atlasUI.pause();
    compiling = true;
    $("assemblyError").textContent = "";
    $("programState").textContent = "Loading code engine…";
    $("assembleProgram").disabled = true;
    try {
      await program.assemble($("assemblySource").value);
      $("programState").textContent = "Program loaded";
      previousListing = null;
    } catch(failure) {
      $("assemblyError").textContent = failure.message.replace(/^PythonError:\s*/,"");
      $("programState").textContent = "Assembly failed";
    } finally {
      compiling = false;
      $("assembleProgram").disabled = false;
      update();
      atlasUI.refresh();
    }
  }
  $("assembleProgram").onclick = assemble;
  $("instructionStep").onclick = async () => {
    atlasUI.pause();
    await program.stepInstruction();
    atlasUI.refresh();
    update();
  };
  $("backProgram").onclick = async () => {
    atlasUI.pause();
    await program.back();
    atlasUI.refresh();
    update();
  };
  $("sampleProgram").onchange = e => {
    atlasUI.pause();
    $("assemblySource").value = samples[e.target.value];
    $("programState").textContent = "Example selected · assemble to load";
  };
  $("openAssembly").onchange = async e => {
    const file = e.target.files[0];
    if (!file) return;
    atlasUI.pause();
    $("assemblySource").value = await file.text();
    $("programState").textContent = file.name+" · assemble to load";
    e.target.value = "";
  };
  $("saveAssembly").onclick = () => {
    const url = URL.createObjectURL(new Blob([$("assemblySource").value],{type:"text/plain"}));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "circuit-atlas.asm";
    anchor.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  $("assemblySource").oninput = () => {
    atlasUI.pause();
    $("programState").textContent = "Source edited · assemble to apply";
  };
  $("assemblySource").onkeydown = e => {
    if(e.key==="Tab"){
      e.preventDefault();
      const t=e.target,start=t.selectionStart,end=t.selectionEnd;
      t.setRangeText("    ",start,end,"end");
    }
    if((e.ctrlKey||e.metaKey)&&e.key==="Enter"){e.preventDefault();assemble();}
  };
  function setMode(next) {
    mode=next;
    for(const item of ["Registers","Memory","Console"])$("show"+item).setAttribute("aria-pressed",item.toLowerCase()===mode);
    renderMachine();
  }
  $("showRegisters").onclick=()=>setMode("registers");
  $("showMemory").onclick=()=>setMode("memory");
  $("showConsole").onclick=()=>setMode("console");
  async function renderMachine() {
    if(!program.active){
      $("machineContents").innerHTML='<p class="ins-copy">Assemble a program to inspect its registers, memory, and output.</p>';
      return;
    }
    const s=cpu.s;
    if(mode==="console"){
      $("machineContents").innerHTML='<pre class="program-console">'+escape(program.log||"Program output appears here.")+'</pre>';
      return;
    }
    if(mode==="registers"){
      const regs=["AX","BX","CX","DX","SP","BP","SI","DI","CS","DS","SS","ES"];
      $("machineContents").innerHTML='<div class="register-grid">'+regs.map(r=>'<div><span>'+r+'</span><b>'+cpu.hex(s[r.toLowerCase()])+'</b></div>').join("")+
        '<div><span>IP</span><b>'+cpu.hex(s.execIP)+'</b></div><div><span>Fetch</span><b>'+cpu.hex(s.ip)+'</b></div></div><div class="program-flags">'+Object.entries(s.flags).map(([name,value])=>'<span class="'+(value?"on":"")+'">'+name+' <b>'+((s.undefinedFlags||[]).includes(name)?"?":value)+'</b></span>').join("")+'</div><small class="mini">? means the instruction leaves that flag undefined.</small>';
      return;
    }
    if(!$("memoryAddress")){
      $("machineContents").innerHTML='<label class="memory-address">Physical address <input id="memoryAddress" maxlength="5" value="'+cpu.hex(memoryAddress,5)+'" aria-label="Physical memory address in hexadecimal"><button id="readMemory">Read</button></label><div id="memoryBytes"></div>';
      $("readMemory").onclick=()=>{
        const input=$("memoryAddress").value;
        if(!/^[0-9a-f]{1,5}$/i.test(input)){$("memoryBytes").textContent="Enter 1–5 hexadecimal digits.";return;}
        memoryAddress=parseInt(input,16);renderMachine();
      };
      $("memoryAddress").onkeydown=e=>{if(e.key==="Enter")$("readMemory").click()};
    }
    const version=++requestVersion;
    try {
      const memory=await program.memory(memoryAddress);
      if(version!==requestVersion||mode!=="memory")return;
      $("memoryBytes").innerHTML=Array.from({length:8},(_,row)=>'<div class="memory-row"><b>'+cpu.hex((memory.address+row*8)&0xfffff,5)+'</b>'+memory.bytes.slice(row*8,row*8+8).map(v=>'<span>'+cpu.hex(v,2)+'</span>').join("")+'</div>').join("");
    }catch(failure){if($("memoryBytes"))$("memoryBytes").textContent=failure.message;}
  }
  function update() {
    $("instructionStep").hidden=!program.active;
    $("instructionStep").disabled=program.busy||program.done||!!program.error;
    $("backProgram").disabled=!program.canBack||program.busy;
    $("step").disabled=program.active&&(program.busy||program.done||!!program.error);
    $("run").disabled=program.active&&(program.done||!!program.error);
    if(program.error)$("assemblyError").textContent=program.error;
    if(program.active){
      if(!compiling)$("programState").textContent=program.error?"Execution stopped":program.done?"Program halted":program.busy?"Executing…":cpu.s.last;
      if(previousListing!==program.listing){
        previousListing=program.listing;
        $("programListing").innerHTML=program.listing.map(row=>'<button class="listing-row" role="listitem" data-line="'+row.line+'" data-address="'+row.address+'"><span>'+cpu.hex(row.address)+'</span><code>'+row.bytes.map(v=>cpu.hex(v,2)).join(" ")+'</code><span>'+escape(row.text.trim())+'</span></button>').join("");
      }
      const address=program.event?cpu.s.instructionAddress:cpu.s.execIP;
      $("programListing").querySelectorAll("[data-address]").forEach(row=>row.classList.toggle("current",+row.dataset.address===address));
      $("programCounter").textContent="IP "+cpu.hex(cpu.s.execIP)+" · fetched "+cpu.hex(cpu.s.ip);
    }
    renderMachine();
  }
  $("programListing").onclick=e=>{
    const row=e.target.closest("[data-line]");
    if(!row)return;
    const lines=$("assemblySource").value.split("\n"),line=+row.dataset.line;
    const start=lines.slice(0,line-1).reduce((n,v)=>n+v.length+1,0);
    $("assemblySource").focus({preventScroll:true});
    $("assemblySource").setSelectionRange(start,start+(lines[line-1]?.length||0));
  };
  $("supportedInstructions").textContent="MOV · XCHG · LEA · LDS · LES · ADD/ADC/SUB/SBB/CMP · AND/OR/XOR/TEST · NOT/NEG · INC/DEC · MUL/IMUL/DIV/IDIV · shifts and rotates by 1 or CL · conditional jumps · LOOP · near/far CALL/JMP/RET · PUSH/POP · flag operations · strings and REP · IN/OUT · CBW/CWD/AAM · XLAT · NOP/HLT.";
  program.events.addEventListener("change",()=>{update();atlasUI.refresh()});
  window.programUI={open,assemble,update};
  update();
})();

