class Node:
    def __init__(self,data):
        self.next=None
        self.data=data 
class LinkedList:
    def __init__(self):
        self.head=None
        self.size=0
    def append(self,data):#thêm phần tử vào cuối
        new_node=Node(data)
        if self.head is None:
            self.head=new_node
        else:
            current=self.head
            while current.next is not None:
                current=current.next
            current.next=new_node
        self.size+=1
    def prepend(self,data):#thêm phần tử vào đầu
        new_node=Node(data)
        new_node.next=self.head
        self.head=new_node
        self.size+=1
    def insert(self,index,data):#thêm phần tử vào một index bất kỳ
        if index<0 or index>self.size:
            raise IndexError("Index out of range")
        if index==0:
            self.prepend(data)
        new_node=Node(data)
        current=self.head
        for i in range(index-1):
            current=current.next
        new_node.next=current.next
        current.next=new_node
        self.size+=1
    def delete(self,data):#xóa phần tử đầu tiên trong Linkedlist có giá trị là data
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
    def delete_at(self,index):
        if index<0 or index>self.size:
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
    def get(self,index):
        if index<0 or index>=self.size:
            raise IndexError("Index out of range")
        current=self.head
        for i in range(index):
            current=current.next
        return current.data
    def find(self,data): #tìm phần tử đầu tiên có giá trị bằng data
        current=self.head
        index=0
        while current is not None:
            if current.data==data:
                return index
            current=current.next
            index+=1
        return -1
    def contains(self,data):#kiểm tra có chứa data hay không
        return self.find(data)!=-1
    def is_empty(self):
        return self.head is None
    def length(self):
        return self.size
    def clear(self):
        self.head=None
        self.size=0
    def to_array(self):
        result=[]
        current=self.head
        while current is not None:
            result.append(current.data)
            current=current.next
        return result
    def __str__(self):
        return str(self.to_array())
class Stack:
    def __init__(self):
        self.items=LinkedList()
    def push(self,data):
        self.items.prepend(data) #push vào đầu stack(do dùng linkedlist)
    def pop(self):
        data=self.items.get(0)
        self.items.delete_at(0)
        return data
    def peek(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.get(0)
    def is_empty(self):
        return self.items.is_empty()
    def size(self):
        return self.items.length()
    def clear(self):
        self.items.clear()
    def __str__(self):
        return f"Stack({self.items})"
class Queue:
    def __init__(self):
        self.items=LinkedList()
    def enqueue(self,data):
        self.items.append(data)
    def dequeue(self):
        data=self.items.get(0)
        self.items.delete_at(0)
        return data
    def front(self):
        return self.items.get(0)
    def is_empty(self):
        return self.items.is_empty()
    def size(self):
        return self.items.length()
    def clear(self):
        self.items.clear()
    def __str__(self):
        return f"Queue({self.items})"
#Hashmap(dictionary)
class KeyValuePair:         
    def __init__(self,key,value):
        self.key=key 
        self.value=value
class HashMap():
    def __init__(self,capacity=16):
        self.capacity=capacity
        self.size=0
        self.buckets=[]#Mảng chứa các linkedList
        for i in range(capacity):
            self.buckets.append(LinkedList())
    def _hash(self,key):#Hàm băm biến key thành index
        if isinstance(key,str):
            has_value=0
            for chr in key:
                has_value=(has_value*31+ord(chr))%self.capacity
            return has_value
        else:
            return hash(key)%(self.capacity)
    def set(self,key,value):
        index=self._hash(key)
        bucket=self.buckets[index]
        current=bucket.head
        while current is not None:
            if current.data.key==key:
                current.data.value=value
                return 
            current=current.next
        bucket.append(KeyValuePair(key,value))
        self.size+=1
    def get(self,key,default=None):
        index=self._hash(key)
        bucket=self.buckets[index]
        current=bucket.head
        while current is not None:
            if current.data.key==key:
                return current.data.value
            current=current.next
        return default
    def delete(self,key):
        index=self._hash(key)
        bucket=self.buckets[index]
        current=bucket.head
        while current is not None:
            if current.data.key==key:
                bucket.delete(current.data)
                self.size-=1
                return True
            current=current.next
        return False
    def contains(self,key):
        index=self._hash(key)
        bucket=self.buckets[index]
        current=bucket.head
        while current is not None:
            if current.data.key==key:
                return True
            current=current.next 
        return False
    def keys(self):
        keys_list=LinkedList()
        for bucket in self.buckets:
            current=bucket.head
            while current is not None:
                keys_list.append(current.data.key)
                current=current.next
        return keys_list
    def values(self):
        values_list=LinkedList()
        for bucket in self.buckets:
            current=bucket.head
            while current is not None:
                values_list.append(current.data.value)
                current=current.next 
        return values_list
    def items(self):#lấy các cặp key-value;
        item_list=LinkedList()
        for bucket in self.buckets:
            current=bucket.head
            while current is not None:
                item_list.append((current.data.key,current.data.value))
                current=current.next
        return item_list
    def length(self):
        return self.size
    def is_empty(self):
        return self.size==0
    def clear(self):
        for i in range(self.capacity):
            self.buckets.append(LinkedList())
        self.size=0
    def to_dict(self):
        result={}
        for bucket in self.buckets:
            current=bucket.head
            while current is not None:
                result[current.data.key]=current.data.value
                current=current.next 
        return result
#----Mảng động---#
class DynamicArray:
    def __init__(self,capacity=10):
        self.capacity=capacity
        self.size=0
        self.data=[None]*capacity

    def _ensure_capacity(self):
        if self.size>=self.capacity:
            self.capacity*=2
            new_data=[None]*self.capacity
            for i in range(self.size):
                new_data[i]=self.data[i]
            self.data=new_data

    def append(self, item):
        self._ensure_capacity()
        self.data[self.size]=item
        self.size+=1

    def insert(self, index, item):
        self._ensure_capacity()
        for i in range(self.size,index,-1):
            self.data[i]=self.data[i-1]
        self.data[index]=item
        self.size+=1

    def delete(self, index):
        for i in range(index,self.size-1):
            self.data[i]=self.data[i+1]
        self.data[self.size-1]=None
        self.size-=1
    def get(self, index):
        return self.data[index]
    def set_value(self, index, item):
        self.data[index]=item
    def find(self, item):
        for i in range(self.size):
            if self.data[i]==item:
                return i
        return -1
    def contains(self, item):
        return self.find(item)!=-1

    def length(self):
        return self.size

    def is_empty(self):
        return self.size==0

    def clear(self):
        self.data=[None]*self.capacity
        self.size=0
    def to_list(self):
        result=[]
        for i in range(self.size):
            result.append(self.data[i])
        return result
    def __str__(self):
        return str(self.to_list())