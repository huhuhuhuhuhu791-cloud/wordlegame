//Các hàm sử lý liên quan tới phím và sự kiện như click.
//Xử lý người dùng nhập một kí tự
function handleKeyPress(key){
    if(!currentGame)
        return;
    if(currentRow>=currentGame.max_attempts)
        return;
    //Chế độ chơi
    if(!isValidKey(key,currentGame.mode)){
        if(currentGame.mode==="math"){
            showMessage("Chỉ nhập số và +-*/=","error");
        }else{
            showMessage("Chỉ nhập chữ A-Z","error");
        }
        return;
    }

    if(currentCol<currentGame.word_length){
        currentWord=currentWord+key.toUpperCase();
        currentCol++;
        updateCurrentRow();
    }
}
//Xử lý phím xóa
function handleBackspace(){
    if(!currentGame)
        return;
    if(currentCol<=0)
        return;
    //Giảm current rol đi 1, cắt bỏ kí tự cuối
    currentCol--;
    currentWord=currentWord.slice(0,-1);
    updateCurrentRow();
}
//Xử lý phím enter
function handleEnter(){
    if(!currentGame)
        return;
    if(currentCol===currentGame.word_length){
        submitGuess();
    }else{
        showMessage("Cần "+currentGame.word_length+" ký tự!","error");
    }
}
//Hàm xử lý bỏ trên bàn phím ảo
function toggleKeyboard(){
    //Đảo trạng thái keyboard và xử lý ẩn hiện
    let alpha=document.getElementById("keyboard");
    let math=document.getElementById("mathKeyboard");
    let btn=document.getElementById("keyboardToggle");
    if(!btn)return;
    keyboardVisible=!keyboardVisible;
    if(keyboardVisible){
        switchKeyboard(currentGame?currentGame.mode:"english");
        btn.textContent=" Ẩn";
    }else{
        if(alpha)
            alpha.style.display="none";
        if(math)

            math.style.display="none";
        btn.textContent="Hiện";
    }
}
//Xử lý nhập từ trên phím ảo
function typeKey(letter){
    handleKeyPress(letter);
}
//xử lý xóa từ phím ảo
function deleteKey(){
    handleBackspace();
}
//xửu lý cập nhật các màu cell trên phím ảo
function updateKeyboardColors(usedLetters){
    if(!usedLetters)return;
    
    // Xóa hết màu
    document.querySelectorAll(".key").forEach(k=>k.classList.remove("cell-correct","cell-present","cell-absent"));
    
    // CHỈ HIỆN MÀU KHI KHÔNG Ở BLIND MODE HOẶC GAME KẾT THÚC
    if(currentGame && currentGame.blind_mode && !currentGame.game_over){
        return; // <-- Không update màu keyboard trong blind mode
    }
    
    // Phần còn lại giữ nguyên
    usedLetters.correct.forEach(letter=>{
        document.querySelectorAll(".key").forEach(btn=>{
            if(btn.textContent===letter){
                btn.classList.add("cell-correct");
            }
        });
    });
    usedLetters.present.forEach(letter=>{
        document.querySelectorAll(".key").forEach(btn=>{
            if(btn.textContent===letter&&!btn.classList.contains("cell-correct")){
                btn.classList.add("cell-present");
            }
        });
    });
    usedLetters.absent.forEach(letter=>{
        document.querySelectorAll(".key").forEach(btn=>{
            if(btn.textContent===letter&&!btn.classList.contains("cell-correct")&&!btn.classList.contains("cell-present")){
                btn.classList.add("cell-absent");
            }
        });
    });
}

///Hàm xử lý sự kiện trong trang//

// xử lý các phím kích chuột và Login--register
document.addEventListener("DOMContentLoaded",()=>{
    //Xử lý login
    document.getElementById("loginUsername")?.addEventListener("keypress",e=>{
        if(e.key==="Enter")
            document.getElementById("loginPassword").focus();

    });
    document.getElementById("loginPassword")?.addEventListener("keypress",e=>{
        if(e.key==="Enter")
            login();

    });

    //xử lý regis
    document.getElementById("regUsername")?.addEventListener("keypress",e=>{
        if(e.key==="Enter")
            document.getElementById("regPassword").focus();
    });
    document.getElementById("regPassword")?.addEventListener("keypress",e=>{
        if(e.key==="Enter")
            document.getElementById("regPasswordConfirm").focus();
    });

    document.getElementById("regPasswordConfirm")?.addEventListener("keypress",e=>{
        if(e.key==="Enter")
            register();
    });
    //bắt sự kiện phím khi ở màn hình game(khi nhập bàn phím)
    document.addEventListener("keydown",e=>{
        let gameScreen=document.getElementById("gameScreen");
        if(!gameScreen)
            return;
        
        if(!gameScreen.classList.contains("active"))
            return;

        if(e.key==="Backspace"||e.key==="Enter"||e.key===" "){
            e.preventDefault();
        }

        if(!isPrintableKey(e))
            return;
        if(e.key==="Enter"){
            handleEnter();
        }else if(e.key==="Backspace"){
            handleBackspace();
        }else if(e.key.length===1){
            handleKeyPress(e.key);
        }
    });
    window.addEventListener("click",e=>{
        document.querySelectorAll(".modal").forEach(m=>{
            if(e.target===m){
                m.style.display="none";
            }
        });
    });
});