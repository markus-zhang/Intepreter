## Exercises for the book Writing Intepreters and compilers for the RPi using Python

### Difficulties in following through the textbook

After tampering with the code and inevitably deciding to figure out a lot of stuffs by my own, I have stuck in certain topics and unstuck myself eventually. The following is a list of all such topics that might bring frustration to people (like me) who are uninitiated in the Conjuration magic of Compiler Design:

#### Function Call

Consider the following code:

```
blah = 100
# Whatever before foo()

def foo(a, b, c):
    d = a + b
    e = 2 * c

    while d <= e:
        print(d)
        if 5 * d < e:
            d *= 2
        else:
            d += 1
        e -= 1

def bar():
    para1 = 2
    para2 = 5
    global blah
    foo(para1, para2, blah)

# Whatever to be executed before
bar()
```

So imagine how the interpreter should behave when running this part of the code

1. `blah = 100`

Interpreter first check whether `functioncalldepth` is 0:
- If `0` then we are in global, business usual
- If not `0` then we are in local, check `localsymboltable` and upsert properly

2. `def foo(a, b, c):`

Interpreter should call `defstmt()` which stores the following information into `globalsymboltable` (right now functions can only be defined in global scope):

`"foo": <value of tokenindex>`

And of course if "foo" is already being defined it raises a RuntimeError (However, why shouldn't we allow same name for variable and function?). Then whenever there is a function call to `foo()` the interpreter can move `tokenindex` to this place, after saving the return address of course.

Then the interpreter should skip all tokens until it hits a token that:
- Is of column 1 (back to global scope)
- Is not of `INDENT` or `DEDENT`

3. `def bar():`

Same story as point 2

4. `bar()`

This is a function call. The following should happen:

- Check whether we are in global scope
    - If `True`, we don't need to worry about backing up the local env
    - If `False`, we are making a function call within a function. We need to back up the local env and clear the local env for the upcoming callee function

- Push the return address (index of first token following the function call) onto the return address stack

- 