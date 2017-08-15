# C-with-Awesome-Syntax (CAS)
CAS converts to C++ in the same way SASS converts to CSS 

1. Indentation is used for scoping rather than {}'s
2. No more ;'s as delimiters



# Example 

CAS file named hello_world.cas:
```
    #include <iostream>
    using namespace std
    int main()
        cout << "Hello World\n"
        return 0
```
The equivlent C++ code:
```C++
    #include <iostream>
    using namespace std;
    int main() {
        cout << "Hello World\n;
        return 0;
    }
```

# How to use 
If you have a file hello_world.cas

to print the C++ code, run:
```
python CAS.py print hello_world.cas
```

to create a C++ file, run:
```
python CAS.py compile hello_world.cas hello_world.cpp
```

to create and run a C++ file, run:
```
python CAS.py run hello_world.cas
```
    
    
    
    
# Special cases 

1. Some things like classes/structs need ```};``` at the end. So in CAS put ; at the end of their line, for example:
```
    class my_class;
        int stuff_in_my_class
```

2. Code + //Comment on the same line = problems. For example:
```
        int a = 5 + 2 // im a comment
```
    that^ would end up in C++ as:
```
        int a = 5 + 2 // im a comment;
```
Which won't run. 
Currently working on a way to fix this. The best alternative right now is /* comment */


3. If you really want to split up a line, you can. Just put a \ at the end of the line. Example:
```C++
        cout << "hello world\n" + \
            "this is a really long line" + \
            "so I used a \\ to fit it on multiple lines"
```

