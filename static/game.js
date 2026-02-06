function showNewGameOptions(){
    showScreen("newGameScreen");
}
async function startNewGame(){
    let mode=document.getElementById("gameMode").value;

    let maxAttempts=parseInt(document.getElementById("maxAttempts").value);
    let res=await fetch("/api/new_game",{method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({mode,max_attempts:maxAttempts})
    });

    let data=await res.json();

    if(!data.success){
        showMessage(data.message,"error");
        if(data.blocked)
            showScreen("menuScreen");
        return;
    }
    currentGame={mode:data.mode,
        max_attempts:data.max_attempts,
        word_length:data.word_length,
        attempts:0,
        guesses:[],
        used_letters:{correct:[],present:[],absent:[]}
    };
    currentRow=0;
    currentCol=0;
    currentWord="";
    elapsedSeconds=0;
    initGameBoard();
    updateGameHeader();
    switchKeyboard(currentGame.mode);
    updateKeyboardColors(currentGame.used_letters);
    showScreen("gameScreen");
    updateTimeDisplay();
    startTimer();
    updateHintsDisplay(3);
    document.getElementById("hintBtn").disabled=false;
    document.getElementById("hintBtn").textContent="💡 Gợi ý";
    document.getElementById("undoBtn").disabled=true;
    document.getElementById("redoBtn").disabled=true;
    if(data.remaining_plays>=0){
        setTimeout(()=>{
            showMessage("Còn "+data.remaining_plays+" lượt","info");
        },500);
    }
}
async function loadSettings(){
    let res=await fetch("/api/get_settings");
    let settings=await res.json();
    document.getElementById("unlimitedPlay").checked=settings.unlimited;
    document.getElementById("maxPlays").value=settings.max_plays;
    document.getElementById("resetMode").value=settings.reset_mode;
    document.getElementById("resetInterval").value=settings.reset_interval;
    toggleUnlimited();
    toggleResetOptions();
}
function toggleUnlimited(){
    let unlimited=document.getElementById("unlimitedPlay").checked;
    document.getElementById("limitSettings").style.display=unlimited?"none":"block";
}
function toggleResetOptions(){
    let mode=document.getElementById("resetMode").value;
    document.getElementById("intervalSetting").style.display=mode==="interval"?"block":"none";
}
async function saveSettings(){
    let settings={
        unlimited:document.getElementById("unlimitedPlay").checked,
        max_plays:parseInt(document.getElementById("maxPlays").value),
        reset_mode:document.getElementById("resetMode").value,
        reset_interval:parseInt(document.getElementById("resetInterval").value)
    };
    let res=await fetch("/api/update_settings",{method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(settings)
    });
    let data=await res.json();
    if(data.success){
        showMessage("Đã lưu!","success");
        showScreen("menuScreen");
    }
}
async function resumeGame(){
    let res=await fetch("/api/resume_game",{
        method:"POST",
        headers:{"Content-Type":"application/json"}
    });
    let data=await res.json();
    if(data.success){
        let state=data.state;
        currentGame={mode:state.mode,max_attempts:state.max_attempts, word_length:state.word_length,
            attempts:state.attempts,
            guesses:state.guesses,
            hints_remaining:state.hints_remaining,
            used_letters:state.used_letters
        };
        currentRow=state.attempts;
        currentCol=0;
        currentWord="";
        elapsedSeconds=state.elapsed_seconds;

        initGameBoard();
        state.guesses.forEach((g,i)=>displayGuess(i,g.word,g.result));
        updateTimeDisplay();
        startTimer();

        updateGameHeader();
        switchKeyboard(currentGame.mode);

        updateKeyboardColors(currentGame.used_letters);
        updateActiveCells();

        updateHintsDisplay(currentGame.hints_remaining);
        if(currentGame.hints_remaining<=0){
            document.getElementById("hintBtn").disabled=true;
            document.getElementById("hintBtn").textContent="Hết";
        }
        showScreen("gameScreen");
        document.getElementById("undoBtn").disabled=!data.can_undo;
        document.getElementById("redoBtn").disabled=!data.can_redo;
        showMessage("Đã tiếp tục!","success");
    }else{
        showMessage(data.message,"error");
    }
}
async function backToMenu(){
    stopTimer();
    let resumeBtn=document.getElementById("resumeBtn");
    if(currentGame&&currentRow<currentGame.max_attempts){
        let wantSave=confirm("Lưu game?");
        if(wantSave){
            await fetch("/api/quit_game",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({elapsed_seconds:elapsedSeconds})
            });
            if(resumeBtn)resumeBtn.style.display="block";
        }else{
            await fetch("/api/discard_game",{method:"POST"});
            if(resumeBtn)resumeBtn.style.display="none";
        }
    }
    showScreen("menuScreen");
}
function initGameBoard(){
    let board=document.getElementById("gameBoard");
    if(!board||!currentGame)
        return;
    board.innerHTML="";
    let len=currentGame.word_length;
    let cellSize=calcCellSize(len);

    board.style.setProperty("--cell-size",cellSize+"px");
    board.style.gridTemplateColumns="repeat("+len+","+cellSize+"px)";

    board.style.justifyItems="center";
    board.style.width="fit-content";

    board.style.margin="15px auto";
    for(let i=0;i<currentGame.max_attempts;i++){
        let row=document.createElement("div");
        row.className="game-row";
        row.id="row-"+i;
        row.style.gridTemplateColumns="repeat("+len+","+cellSize+"px)";
        row.style.setProperty("--cell-size",cellSize+"px");
        for(let j=0;j<len;j++){
            let cell=document.createElement("div");
            cell.className="game-cell";
            cell.id="cell-"+i+"-"+j;
            cell.style.width=cellSize+"px";
            cell.style.height=cellSize+"px";
            row.appendChild(cell);
        }
        board.appendChild(row);
    }
    updateActiveCells();
}
function updateActiveCells(){
    document.querySelectorAll(".game-cell").forEach(c=>c.classList.remove("active"));
    if(!currentGame)
        return;
    if(currentRow<currentGame.max_attempts){
        let cell=document.getElementById("cell-"+currentRow+"-"+currentCol);
        if(cell)cell.classList.add("active");
    }
}
function updateCurrentRow(){
    if(!currentGame)
        return;
    for(let i=0;i<currentGame.word_length;i++){
        let cell=document.getElementById("cell-"+currentRow+"-"+i);
        if(!cell)continue;
        if(currentWord[i]){
            cell.textContent=currentWord[i];
            cell.classList.add("filled");
        }else{
            cell.textContent="";
            cell.classList.remove("filled");
        }
    }
    updateActiveCells();
}
function displayGuess(rowIndex,word,result){
    if(!word||!result)
        return;
    let len=currentGame.word_length;
    for(let i=0;i<len;i++){
        let cell=document.getElementById("cell-"+rowIndex+"-"+i);
        if(!cell)
            continue;
        cell.textContent=word[i];
        cell.classList.add("filled");
        cell.classList.remove("active","cell-correct","cell-present","cell-absent");
        if(result[i]===2){
            cell.classList.add("cell-correct");
        }else if(result[i]===1){
            cell.classList.add("cell-present");
        }else{
            cell.classList.add("cell-absent");
        }
    }
}
function updateGameHeader(){
    if(!currentGame)return;
    let player=document.getElementById("currentPlayer");
    let attempts=document.getElementById("attemptsDisplay");
    let mode=document.getElementById("modeDisplay");
    if(player)player.textContent=currentUser;
    if(attempts)attempts.textContent=currentGame.attempts+"/"+currentGame.max_attempts;
    let icon="🇬🇧";
    if(currentGame.mode==="vietnamese")icon="🇻🇳";
    if(currentGame.mode==="math")icon="🔢";
    if(mode)mode.textContent=icon;
}
async function getHint(){
    if(!currentGame){
        showMessage("Không có game!","error");
        return;
    }
    if(!confirm("Dùng gợi ý?"))
        return;
    let res=await fetch("/api/get_hint",{
        method:"POST",
        headers:{"Content-Type":"application/json"}
    });
    let data=await res.json();
    if(data.success){
        showMessage(data.hint_text,"info",5000);
        updateHintsDisplay(data.hints_remaining);
        if(data.hints_remaining<=0){
            document.getElementById("hintBtn").disabled=true;
            document.getElementById("hintBtn").textContent="Hết";
        }
    }else{
        showMessage(data.message,"error");
    }
}
function updateHintsDisplay(remaining){
    let display=document.getElementById("hintsDisplay");
    if(display){
        display.textContent=remaining;
        display.style.color="#dc3545";
    }
}

async function submitGuess(){
    if(!currentGame)
        return;
    if(currentWord.length!==currentGame.word_length){
        showMessage("Cần "+currentGame.word_length+" ký tự!","error");
        return;
    }
    let res=await fetch("/api/guess",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({word:currentWord,elapsed_seconds:elapsedSeconds})
    });
    let data=await res.json();
    if(data.success){
        displayGuess(currentRow,data.word,data.result);
        currentGame.attempts=data.attempts;
        currentGame.guesses.push({word:data.word,result:data.result});
        if(data.used_letters)currentGame.used_letters=data.used_letters;
        currentWord="";
        currentCol=0;
        currentRow++;

        updateGameHeader();
        updateKeyboardColors(currentGame.used_letters);
        updateActiveCells();
        document.getElementById("undoBtn").disabled=!data.can_undo;
        document.getElementById("redoBtn").disabled=!data.can_redo;
        if(data.game_over){
            stopTimer();
            if(data.won){
                showMessage("Thắng trong "+data.time_elapsed.toFixed(2)+"s","success");
            }else{
                showMessage(" Thua! Đáp án: "+data.target_word,"error");
            }
            setTimeout(()=>{
                showScreen("menuScreen");
            },3000);
        }
    }else{
        showMessage(data.message,"error");
    }
}
async function undoGuess(){
    let res=await fetch("/api/undo",{
        method:"POST",
        headers:{"Content-Type":"application/json"}
    });
    let data=await res.json();
    if(data.success){
        if(!currentGame)currentGame={};
        currentGame.attempts=data.attempts;
        currentGame.guesses=data.guesses;
        if(data.used_letters)currentGame.used_letters=data.used_letters;
        currentRow=data.attempts;
        currentCol=0;
        currentWord="";
        initGameBoard();
        data.guesses.forEach((g,i)=>displayGuess(i,g.word,g.result));
        updateGameHeader();
        updateKeyboardColors(currentGame.used_letters);
        updateActiveCells();
        document.getElementById("undoBtn").disabled=!data.can_undo;
        document.getElementById("redoBtn").disabled=!data.can_redo;
        showMessage("Hoàn tác","info");
    }else{
        showMessage(data.message,"error");
    }
}
async function redoGuess(){
    let res=await fetch("/api/redo",{
        method:"POST",
        headers:{"Content-Type":"application/json"}
    });
    let data=await res.json();
    if(data.success){
        if(!currentGame)currentGame={};
        currentGame.attempts=data.attempts;
        currentGame.guesses=data.guesses;
        if(data.used_letters)currentGame.used_letters=data.used_letters;
        currentRow=data.attempts;
        currentCol=0;
        currentWord="";
        initGameBoard();
        data.guesses.forEach((g,i)=>displayGuess(i,g.word,g.result));
        updateGameHeader();
        updateKeyboardColors(currentGame.used_letters);
        updateActiveCells();
        document.getElementById("undoBtn").disabled=!data.can_undo;
        document.getElementById("redoBtn").disabled=!data.can_redo;
        showMessage("Làm lại","info");
    }else{
        showMessage(data.message,"error");
    }
}
async function loadLeaderboard(){
    let res=await fetch("/api/leaderboard");
    let data=await res.json();
    if(data.success){
        let list=document.getElementById("leaderboardList");
        if(!list)return;
        if(!data.leaderboard||data.leaderboard.length===0){
            list.innerHTML='<p style="text-align:center;padding:20px;">Chưa có ai</p>';
        }else{
            let html='<table><tr><th>Hạng</th><th>Tên</th><th>TB</th><th>Best</th><th>Thắng</th></tr>';
            data.leaderboard.forEach((p,i)=>{
                html+="<tr>";
                html+="<td>"+p.rank+"</td>";
                html+="<td>"+p.name+"</td>";
                html+="<td>"+p.avg_time.toFixed(2)+"</td>";
                html+="<td>"+(p.best_time?p.best_time.toFixed(2):"-")+"</td>";
                html+="<td>"+p.total_wins+"</td>";
                html+="</tr>";
            });
            html+="</table>";
            list.innerHTML=html;
        }
        showModal("leaderboardModal");
    }else{
        showMessage(data.message,"error");
    }
}
async function loadHistory(){
    let res=await fetch("/api/history");
    let data=await res.json();
    if(data.success){
        let list=document.getElementById("historyList");
        if(!list)return;
        if(!data.history||data.history.length===0){
            list.innerHTML='<p style="text-align:center;padding:20px;">Chưa có lịch sử</p>';
        }else{
            let html='<table><tr><th>STT</th><th>Thời gian</th><th>Lượt</th><th>KQ</th><th>Mode</th><th>Lúc</th></tr>';
            data.history.forEach((g,i)=>{
                html+="<tr>";
                html+="<td>"+(i+1)+"</td>";
                html+="<td>"+g.time.toFixed(2)+"s</td>";
                html+="<td>"+g.attempts+"</td>";
                html+="<td>"+(g.won?"✅":"❌")+"</td>";
                let icon="🇬🇧";
                if(g.mode==="vietnamese")icon="🇻🇳";
                if(g.mode==="math")icon="🔢";
                html+="<td>"+icon+"</td>";
                html+="<td>"+g.date+"</td>";
                html+="</tr>";
            });
            html+="</table>";
            list.innerHTML=html;
        }
        showModal("historyModal");
    }else{
        showMessage(data.message,"error");
    }
}
 
