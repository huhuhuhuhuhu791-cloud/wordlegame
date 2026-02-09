from datetime import datetime
from data_structures import LinkedList,Stack  # Bỏ HashMap
import random

#xử lý biểu thức toán học
def _precedence(op):
    if op in("+","-"):
        return 1
    if op in("*","/"):
        return 2
    return 0
    
def _is_operator(ch):
    return ch in("+","-","*","/")
    
def infix_to_postfix(tokens):
    output=[]
    op_stack=Stack()
    for token in tokens:
        if token.lstrip("-").isdigit():
            output.append(token)
        elif _is_operator(token):
            while not op_stack.is_empty():
                top=op_stack.peek()
                if _is_operator(top)and _precedence(top)>=_precedence(token):
                    output.append(op_stack.pop())
                else:
                    break
            op_stack.push(token)
        elif token=="(":
            op_stack.push(token)
        elif token==")":
            while not op_stack.is_empty() and op_stack.peek()!="(":
                output.append(op_stack.pop())
            if not op_stack.is_empty():
                op_stack.pop()
    while not op_stack.is_empty():
        output.append(op_stack.pop())
    return output
    
def eval_postfix(postfix_tokens):
    eval_stack=Stack()
    for token in postfix_tokens:
        if token.lstrip("-").isdigit():
            eval_stack.push(int(token))
        elif _is_operator(token):
            if eval_stack.size()<2:
                raise ValueError("Biểu thức không hợp lệ")
            b=eval_stack.pop()
            a=eval_stack.pop()
            if token=="+":
                eval_stack.push(a+b)
            elif token=="-":
                eval_stack.push(a-b)
            elif token=="*":
                eval_stack.push(a*b)
            elif token=="/":
                if b==0:
                    raise ValueError("Chia cho 0")
                if a%b!=0:
                    raise ValueError("Không chia hết")
                eval_stack.push(a//b)
        else:
            raise ValueError(f"Token không hợp lệ:{token}")
    if eval_stack.size()!=1:
        raise ValueError("Biểu thức không hợp lệ")
    return eval_stack.pop()
    
def tokenize_expr(expr_str):
    tokens=[]
    i=0
    while i<len(expr_str):
        ch=expr_str[i]
        if ch.isdigit():
            num=""
            while i<len(expr_str) and expr_str[i].isdigit():
                num+=expr_str[i]
                i+=1
            tokens.append(num)
        elif ch in"+-*/()":
            tokens.append(ch)
            i+=1
        elif ch==" ":
            i+=1
        else:
            raise ValueError(f"Ký tự không hợp lệ:{ch}")
    return tokens
    
def validate_and_eval_math(expression_str):
    if "=" not in expression_str:
        return False,None
    parts=expression_str.split("=")
    if len(parts)!=2:
        return False,None
    lhs,rhs=parts[0].strip(),parts[1].strip()
    if not rhs.lstrip("-").isdigit():
        return False,None
    try:
        tokens=tokenize_expr(lhs)
        postfix=infix_to_postfix(tokens)
        computed=eval_postfix(postfix)
        return computed==int(rhs),computed
    except Exception:
        return False,None
        
def _generate_math_pool():
    pool=[]
    ops=["+","-","*"]
    seen=set()
    for a in range(1,13):
        for b in range(1,10):
            for c in range(1,10):
                for op1 in ops:
                    for op2 in ops:
                        expr_lhs=f"{a}{op1}{b}{op2}{c}"
                        try:
                            tokens=tokenize_expr(expr_lhs)
                            postfix=infix_to_postfix(tokens)
                            result=eval_postfix(postfix)
                        except Exception:
                            continue
                        if result<0 or result>99:
                            continue
                        full=f"{expr_lhs}={result}"
                        if 7<=len(full)<=12 and full not in seen:
                            seen.add(full)
                            pool.append(full)
                            if len(pool)>=120:
                                return pool
    return pool
    
_MATH_POOL=_generate_math_pool()

#Các CoreGame
class WordleGame:
    def __init__(self,mode="english",max_attempts=6,blind_mode=False):
        self.mode=mode
        self.max_attempts=max_attempts
        self.attempts=0
        self.guesses=LinkedList()
        self.undo_stack=Stack()
        self.redo_stack=Stack()
        
        # ========== THAY HASHMAP BẰNG DICT ==========
        self.used_letters={
            "correct": LinkedList(),
            "present": LinkedList(),
            "absent": LinkedList()
        }
        # ============================================
        
        self.start_time=datetime.now()
        self.time_elapsed=0
        self.game_over=False
        self.won=False
        self.target_word=self._get_random_word()
        self.word_length=len(self.target_word)
        self.hints_remaining=3
        self.hints_used=[]
        self.max_undo_redo=3
        self.undo_count=0
        self.redo_count=0
        self.blind_mode=blind_mode
        
        # CHI PHÍ HINT
        self.hint_costs = {
            0: 2,  
            1: 2,   
            2: 2,   
        }
        
        # CHI PHÍ UNDO/REDO
        self.undo_cost = 3
        self.redo_cost = 3
        
    def _get_random_word(self):
        if self.mode=="english":
            with open("data/words/english.txt","r",encoding="utf-8") as f:
                arr=[line.strip() for line in f]
                n=random.randint(0,len(arr)-1)
                return arr[n]
        elif self.mode=="vietnamese":
           with open("data/words/vietnamese.txt","r",encoding="utf-8") as f:
                arr=[line.strip() for line in f]
                n=random.randint(0,len(arr)-1)
                return arr[n]
        else:
            arr=_MATH_POOL
            n=random.randint(0,len(arr))
            return arr[n]
            
    def get_hint(self):
        if self.hints_remaining<=0:
            return{"success":False,"message":"Bạn đã hết lượt gợi ý","hints_remaining":0}
        
        if self.game_over:
            return{"success":False,"message":"Game đã kết thúc","hints_remaining":self.hints_remaining}
        
        hint_type=len(self.hints_used)
        hint_text=""
        cost = self.hint_costs.get(hint_type, 0)
        
        # CÁC LOẠI HINT
        if self.mode=="math":
            if hint_type==0:
                hint_text=f"Chữ số đầu tiên: {self.target_word[0]}"
            elif hint_type==1:
                hint_text=f"Chữ số cuối cùng: {self.target_word[-1]}"
            elif hint_type==2:
                total=sum(int(d) for d in self.target_word if d.isdigit())
                hint_text=f"Kết quả phép tính là = {total}"
        else:
            if hint_type==0:
                hint_text=f"Chữ cái đầu: {self.target_word[0].upper()}"
            elif hint_type==1:
                hint_text=f"Chữ cái cuối: {self.target_word[-1].upper()}"
            elif hint_type==2:
                mid_index=len(self.target_word)//2
                hint_text=f"Chữ cái thứ {mid_index}: {self.target_word[mid_index].upper()}"
        
        self.hints_used.append(hint_text)
        self.hints_remaining-=1
        
        return {
            "success": True,
            "message": "Đây là gợi ý của bạn!",
            "hint_text": hint_text,
            "hints_remaining": self.hints_remaining,
            "hint_number": len(self.hints_used),
            "cost": cost
        }
        
    def is_valid_word(self,word):
        word=word.upper()
        if len(word)!=self.word_length:
            return False
        if self.mode=="math":
            ok,_=validate_and_eval_math(word)
            return ok
        if self.mode=="english":
            with open("data/words/english.txt","r",encoding="utf-8") as f:
                arr=[line.strip() for line in f]  
            if word in arr:
                return True    
            return False
        else:
            with open("data/words/vietnamese.txt","r",encoding="utf-8") as f:
                arr=[line.strip() for line in f]
            if word in arr:
                return True
            return False
            
    def make_guess(self,word):
        word=word.upper()
        if self.game_over:
            # ========== THAY HASHMAP BẰNG DICT ==========
            return {
                "success": False,
                "message": "Game đã kết thúc!",
                "game_over": True,
                "won": self.won
            }
            # ============================================
            
        if len(word)!=self.word_length:
            return {
                "success": False,
                "message": f"Cần {self.word_length} ký tự!",
                "game_over": False
            }
            
        result_array=self._check_word(word)
        
        # ========== THAY HASHMAP BẰNG DICT ==========
        state={
            "guesses_backup": self._clone_guesses(),
            "attempts": self.attempts,
            "used_letters_backup": self._clone_used_letters()
        }
        # ============================================
        
        self.undo_stack.push(state)
        if self.undo_stack.size()>self.max_undo_redo:
            temp_stack=Stack()
            for _ in range(self.undo_stack.size()-1):
                temp_stack.push(self.undo_stack.pop())
            self.undo_stack.clear()
            while not temp_stack.is_empty():
                self.undo_stack.push(temp_stack.pop())
                
        self.redo_stack.clear()
        self.redo_count=0
        
        # ========== THAY HASHMAP BẰNG DICT ==========
        guess_data={
            "word": word,
            "result": result_array,
            "timestamp": datetime.now().isoformat()
        }
        # ============================================
        
        self.guesses.append(guess_data)
        self.attempts+=1
        self._update_used_letters(word,result_array)
        
        if word==self.target_word:
            self.won=True
            self.game_over=True
            self.time_elapsed=(datetime.now()-self.start_time).total_seconds()
            
        if self.attempts>=self.max_attempts:
            self.game_over=True
            self.time_elapsed=(datetime.now()-self.start_time).total_seconds()
            
        # ========== THAY HASHMAP BẰNG DICT ==========
        return {
            "success": True,
            "word": word,
            "result": result_array,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "game_over": self.game_over,
            "won": self.won,
            "target_word": self.target_word if self.game_over else None,
            "time_elapsed": self.time_elapsed if self.game_over else None,
            "used_letters": self._used_letters_to_dict(),
            "can_undo": not self.undo_stack.is_empty(),
            "can_redo": not self.redo_stack.is_empty(),
            "blind_mode": self.blind_mode
        }
        # ============================================
        
    def _check_word(self,word):
        n=self.word_length
        result=[0]*n
        target_arr=list(self.target_word)
        word_arr=list(word)
        
        # Đánh dấu các vị trí đúng
        for i in range(n):
            if word_arr[i]==target_arr[i]:
                result[i]=2
                target_arr[i]=None
                word_arr[i]=None
        
        # Đánh dấu các chữ cái có nhưng sai vị trí
        for i in range(n):
            if word_arr[i] is not None:
                letter=word_arr[i]
                for j in range(n):
                    if target_arr[j]==letter:
                        result[i]=1
                        target_arr[j]=None
                        break
        return result
        
    def _update_used_letters(self,word,result):
        # ========== THAY HASHMAP BẰNG DICT ==========
        correct_list=self.used_letters["correct"]
        present_list=self.used_letters["present"]
        absent_list=self.used_letters["absent"]
        # ============================================
        
        for i in range(self.word_length):
            letter=word[i]
            if result[i]==2:
                if not correct_list.contains(letter):
                    correct_list.append(letter)
                if present_list.contains(letter):
                    present_list.delete(letter)
            elif result[i]==1:
                if not present_list.contains(letter) and not correct_list.contains(letter):
                    present_list.append(letter)
            else:
                if(not absent_list.contains(letter) and not correct_list.contains(letter) and not present_list.contains(letter)):
                    absent_list.append(letter)
                    
    def undo(self):
        if self.undo_stack.is_empty():
            return {"success": False, "message": "Không thể undo!"}
            
        if self.undo_count>=self.max_undo_redo:
            return {"success": False, "message": f"Đã hết lượt undo!(Tối đa {self.max_undo_redo} lần)"}
            
        # ========== THAY HASHMAP BẰNG DICT ==========
        cur={
            "guesses_backup": self._clone_guesses(),
            "attempts": self.attempts,
            "used_letters_backup": self._clone_used_letters()
        }
        # ============================================
        
        self.redo_stack.push(cur)
        prev=self.undo_stack.pop()
        
        # ========== THAY HASHMAP BẰNG DICT ==========
        self.guesses=prev["guesses_backup"]
        self.attempts=prev["attempts"]
        self.used_letters=prev["used_letters_backup"]
        # ============================================
        
        self.game_over=False
        self.won=False
        self.undo_count+=1
        
        return {
            "success": True,
            "message": f"Đã hoàn tác({self.max_undo_redo-self.undo_count} lượt undo còn lại)",
            "attempts": self.attempts,
            "guesses": self._guesses_to_list(),
            "used_letters": self._used_letters_to_dict(),
            "can_undo": not self.undo_stack.is_empty() and self.undo_count<self.max_undo_redo,
            "can_redo": not self.redo_stack.is_empty() and self.redo_count<self.max_undo_redo,
            "undo_remaining": self.max_undo_redo-self.undo_count,
            "redo_remaining": self.max_undo_redo-self.redo_count,
            "cost": self.undo_cost
        }
        
    def redo(self):
        if self.redo_stack.is_empty():
            return {"success": False, "message": "Không thể redo!"}
            
        if self.redo_count>=self.max_undo_redo:
            return {"success": False, "message": f"Đã hết lượt redo!(Tối đa {self.max_undo_redo} lần)"}
            
        # ========== THAY HASHMAP BẰNG DICT ==========
        cur={
            "guesses_backup": self._clone_guesses(),
            "attempts": self.attempts,
            "used_letters_backup": self._clone_used_letters()
        }
        # ============================================
        
        self.undo_stack.push(cur)
        nxt=self.redo_stack.pop()
        
        # ========== THAY HASHMAP BẰNG DICT ==========
        self.guesses=nxt["guesses_backup"]
        self.attempts=nxt["attempts"]
        self.used_letters=nxt["used_letters_backup"]
        # ============================================
        
        self.redo_count+=1
        
        if self.attempts>=self.max_attempts:
            self.game_over=True
            
        if self.guesses.length()>0:
            last=self.guesses.get(self.guesses.length()-1)
            # ========== THAY HASHMAP BẰNG DICT ==========
            if last["word"]==self.target_word:
                self.won=True
                self.game_over=True
            # ============================================
                
        return {
            "success": True,
            "message": f"Đã làm lại!({self.max_undo_redo-self.redo_count} lượt redo còn lại)",
            "attempts": self.attempts,
            "guesses": self._guesses_to_list(),
            "used_letters": self._used_letters_to_dict(),
            "game_over": self.game_over,
            "won": self.won,
            "can_undo": not self.undo_stack.is_empty() and self.undo_count<self.max_undo_redo,
            "can_redo": not self.redo_stack.is_empty() and self.redo_count<self.max_undo_redo,
            "undo_remaining": self.max_undo_redo-self.undo_count,
            "redo_remaining": self.max_undo_redo-self.redo_count,
            "cost": self.redo_cost
        }
        
    def _clone_guesses(self):
        new=LinkedList()
        cur=self.guesses.head
        while cur:
            new.append(cur.data)
            cur=cur.next
        return new
        
    def _clone_used_letters(self):
        # ========== THAY HASHMAP BẰNG DICT ==========
        new_map={
            "correct": LinkedList(),
            "present": LinkedList(),
            "absent": LinkedList()
        }
        
        for key in ["correct","present","absent"]:
            cur=self.used_letters[key].head
            while cur:
                new_map[key].append(cur.data)
                cur=cur.next
        return new_map
        # ============================================
        
    def _guesses_to_list(self):
        result=[]
        cur=self.guesses.head
        while cur:
            # ========== THAY HASHMAP BẰNG DICT ==========
            result.append({
                "word": cur.data["word"],
                "result": cur.data["result"],
                "timestamp": cur.data["timestamp"]
            })
            # ============================================
            cur=cur.next
        return result
        
    def _used_letters_to_dict(self):
        # ========== THAY HASHMAP BẰNG DICT ==========
        return {
            "correct": self.used_letters["correct"].to_array(),
            "present": self.used_letters["present"].to_array(),
            "absent": self.used_letters["absent"].to_array()
        }
        # ============================================

    def get_state(self):
        # ========== THAY HASHMAP BẰNG DICT ==========
        return {
            "mode": self.mode,
            "max_attempts": self.max_attempts,
            "target_word": self.target_word,
            "word_length": self.word_length,
            "guesses": self._guesses_to_list(),
            "attempts": self.attempts,
            "used_letters": self._used_letters_to_dict(),
            "start_time": self.start_time.isoformat(),
            "game_over": self.game_over,
            "won": self.won,
            "time_elapsed": self.time_elapsed,
            "undo_count": self.undo_count,
            "hints_remaining": self.hints_remaining,
            "blind_mode": self.blind_mode,
            "redo_count": self.redo_count
        }
        # ============================================
        
    @classmethod
    def from_state(cls,state):
        game=cls.__new__(cls)
        game.mode=state["mode"]
        game.max_attempts=state["max_attempts"]
        game.target_word=state["target_word"]
        game.word_length=state.get("word_length",len(state["target_word"]))
        game.attempts=state["attempts"]
        game.start_time=datetime.fromisoformat(state["start_time"])
        game.game_over=state["game_over"]
        game.won=state["won"]
        game.time_elapsed=state.get("time_elapsed",0)
        game.blind_mode=state.get("blind_mode",False)
        
        game.guesses=LinkedList()
        for g in state["guesses"]:
            # ========== THAY HASHMAP BẰNG DICT ==========
            guess_data={
                "word": g["word"],
                "result": g["result"],
                "timestamp": g["timestamp"]
            }
            # ============================================
            game.guesses.append(guess_data)
            
        # ========== THAY HASHMAP BẰNG DICT ==========
        game.used_letters={
            "correct": LinkedList(),
            "present": LinkedList(),
            "absent": LinkedList()
        }
        
        for key in ["correct","present","absent"]:
            for letter in state["used_letters"].get(key,[]):
                game.used_letters[key].append(letter)
        # ============================================
        
        game.undo_stack=Stack()
        game.redo_stack=Stack()
        game.max_undo_redo=3
        game.undo_count=state.get("undo_count",0)
        game.redo_count=state.get("redo_count",0)
        game.hints_remaining=state.get("hints_remaining",3)
        game.hints_used=state.get("hints_used",[])
        
        # Khởi tạo cost
        game.undo_cost = 3
        game.redo_cost = 3
        game.hint_costs = {0: 2, 1: 2, 2: 2}
        
        return game