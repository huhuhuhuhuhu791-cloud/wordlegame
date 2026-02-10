class Node:
    def __init__(self,data):
        self.next=None
        self.data=data 
class LinkedList:
    def __init__(self):
        self.head=None
        self.size=0
    def append(self,data):  #Thêm phần tử vào cuối
        new_node=Node(data)
        if self.head is None:
            self.head=new_node
        else:
            current=self.head
            while current.next is not None:
                current=current.next
            current.next=new_node
        self.size+=1
    def prepend(self,data):  #Thêm phần tử vào đầu
        new_node=Node(data)
        new_node.next=self.head
        self.head=new_node
        self.size+=1
    def delete(self,data):  #Xóa phần tử đầu tiên có giá trị là data
        if self.head is None:
            return False
        if self.head.data==data:
            self.head=self.head.next
            self.size-=1
            return True
        current=self.head
        while current.next is not None:
            if current.next.data==data:
                current.next=current.next.next
                self.size-=1
                return True
            current=current.next
        return False
    def delete_at(self,index):  #Xóa ở vị trí index
        if index<0 or index>=self.size:
            raise IndexError("Index out of range")
        if index==0:
            self.head=self.head.next
            self.size-=1
            return
        current=self.head
        for i in range(index-1):
            current=current.next
        current.next=current.next.next
        self.size-=1
    def get(self,index):  #Lấy phần tử ở vị trí index
        if index<0 or index>=self.size:
            raise IndexError("Index out of range")
        current=self.head
        for i in range(index):
            current=current.next
        return current.data
    def contains(self,data):  #Kiểm tra có chứa data hay không
        current=self.head
        while current is not None:
            if current.data==data:
                return True
            current=current.next
        return False
    def is_empty(self):  #Kiểm tra xem có rỗng hay không
        return self.head is None
    def length(self):  #Lấy độ dài của list
        return self.size
    def to_array(self):  #Chuyển sang array
        result=[]
        current=self.head
        while current is not None:
            result.append(current.data)
            current=current.next
        return result
class Stack:
    def __init__(self):
        self.items=LinkedList()
    def push(self,data):  #Thêm vào stack
        self.items.prepend(data)
    def pop(self):  #Lấy ra khỏi stack
        data=self.items.get(0)
        self.items.delete_at(0)
        return data
    def peek(self):  #Xem đỉnh stack
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.get(0)
    def is_empty(self):
        return self.items.is_empty()
    def size(self):
        return self.items.length()
    def clear(self):  # Xóa hết stack
        self.items.head=None
        self.items.size=0