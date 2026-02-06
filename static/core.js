let currentUser=null;
let currentGame=null;
let keyboardVisible=true;
let timerInterval=null;
let elapsedSeconds=0;
let currentRow=0;
let currentCol=0;
let currentWord="";
function isValidKey(key,mode){
    if(!key||key.length!==1)
        return false;
    let upper=key.toUpperCase();

    if(mode==="math")
        return /^[0-9+\-*/=]$/.test(key);
    return /^[A-Z]$/.test(upper);
}
function isPrintableKey(event){
    if(event.ctrlKey||event.altKey||event.metaKey)
        return false;
    let bad=["Shift","Control","Alt","CapsLock","F1","F2","F3","F4",
        "F5","F6","F7","F8","F9","F10","F11","F12"];
    return!bad.includes(event.key);
}
function calcCellSize(len){
    let size=Math.floor((440-(len-1)*5)/len);
    if(size>50)size=50;

    if(size<28)size=28;
    return size;
}
function showScreen(id){
    document.querySelectorAll(".screen").forEach(s=>s.classList.remove("active"));
    let screen=document.getElementById(id);

    if(screen)screen.classList.add("active");

    if(id==="gameScreen"){
        setTimeout(()=>document.getElementById("gameScreen").focus(),100);
    }
}
function showMessage(text,type="info",duration=3000){
    let msg=document.getElementById("message");
    if(!msg)return;
    msg.textContent=text;
    msg.className="message "+type;

    msg.style.display="block";
    setTimeout(()=>msg.style.display="none",duration);
}
function showModal(id){
    let modal=document.getElementById(id);

    if(modal)modal.style.display="flex";
}
function closeModal(id){
    let modal=document.getElementById(id);

    if(modal)modal.style.display="none";
}
function updateTimeDisplay(){
    let el=document.getElementById("timeDisplay");
    if(el)el.textContent=elapsedSeconds+"s";
}
function startTimer(){
    stopTimer();
    timerInterval=setInterval(()=>{
        elapsedSeconds++;

        updateTimeDisplay();
    },1000);
}
function stopTimer(){
    if(timerInterval){
        clearInterval(timerInterval);
        timerInterval=null;
    }
}
function switchKeyboard(mode){
    let alpha=document.getElementById("keyboard");
    let math=document.getElementById("mathKeyboard");
    if(mode==="math"){
        if(alpha)alpha.style.display="none";
        if(math)math.style.display="block";
    }else{
        if(alpha)alpha.style.display="block";
        if(math)math.style.display="none";
    }
}
async function login(){
    let username=document.getElementById("loginUsername").value.trim();
    let password=document.getElementById("loginPassword").value;
    let res=await fetch("/api/login",{method:"POST",

        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username,password})
    });
    let data=await res.json();
    if(data.success){
        currentUser=data.username;
        document.getElementById("playerName").textContent=currentUser;
        let resumeBtn=document.getElementById("resumeBtn");

        if(resumeBtn)resumeBtn.style.display=data.has_saved_game?"block":"none";

        showScreen("menuScreen");

        showMessage("Đăng nhập thành công!","success");
    }else{
        showMessage(data.message,"error");
    }
}
async function register(){
    let username=document.getElementById("regUsername").value.trim();
    let password=document.getElementById("regPassword").value;
    let confirm=document.getElementById("regPasswordConfirm").value;

    if(!username||!password||!confirm){
        showMessage("Vui lòng điền đủ thông tin!","error");
        return;
    }
    if(password!==confirm){
        showMessage("Mật khẩu không khớp!","error");
        return;
    }
    let res=await fetch("/api/register",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username,password})
    });
    let data=await res.json();
    if(data.success){
        currentUser=data.username;
        document.getElementById("playerName").textContent=currentUser;
        document.getElementById("resumeBtn").style.display="none";
        showScreen("menuScreen");
        showMessage(data.message,"success");
    }else{
        showMessage(data.message,"error");
    }
}
async function logout(){
    await fetch("/api/logout",{method:"POST"});
    currentUser=null;
    currentGame=null;
    currentRow=0;
    currentCol=0;
    currentWord="";
    showScreen("loginScreen");
    showMessage("Đã đăng xuất!","info");
}