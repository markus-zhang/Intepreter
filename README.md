## Exercises for the book Writing Intepreters and compilers for the RPi using Python

### Difficulties in following through the textbook

After tampering with the code and inevitably deciding to figure out a lot of stuffs by my own, I have stuck in certain topics and unstuck myself eventually. The following is a list of all such topics that might bring frustration to people (like me) who are uninitiated in the Conjuration magic of Compiler Design:

#### Break

This is the most difficult one:

1. In the tokenizer, the `DEDENT` tokens must have the correct columns (check bookmark `rm00` in `tokenizer.py`)

2. In the parser, whenever a `break` occurs, the program should perform the following:
    - in break(), it must consume all DEDENT, including the one usually reserved for the parent codeblock() -- the one within while loop (`parser.py`, bookmark `rm01`)

    - in break(), a flag must be set to pass to all its parent caller functions (`parser.py`, bookmark `rm01`)

    - `while` loops must set another flag to indicate that the code breaks out of the `while` loop, everything in the loop has been skipped (including the said `DEDENT` reserved for the `codeblock` within the `while` loop), see `codeblock()` for why we need a second flag (`parser.py`, bookmark `rm02`) (`parser.py`, bookmark `rm03`)

    - Now `while` loops can have two kinds of call stacks, one is `whilestmt()`<-`compoundstmt()`<-`codeblock()`, this is when the `while` loop is wrapped inside of a `codeblock`, and the other is `whilestmt()`<-`compoundstmt()`->`stmt()`, this is when the `while` loop is at the outmost layer, i.e. NOT wrapped within a `codeblock`

        - For situation 1, the parent `codeblock()` should clear the two flags -- but we need to make sure that it IS the right one, e.g. this `codeblock` actually wraps an `if` which has a `break`, and both are within a `while` loop, so you have a call stack that looks like:
        
        `break()`<-`simplestmt()`<-`stmt()`<-`codeblock()`<-`ifstmt()`<-`compoundstmt()`<-`stmt()`<-`codeblock()`<-`whilestmt()`<-`compoundstmt()`<-`stmt()`<-`codeblock()`<-..., 
        
        and only the last one is the correct one to reset the two flags -- we need to make sure that the second flag has been set by the `while` loop -- which means this `codeblock` is indeed the grandparent of the while loop

        - For situation 2, it's the same stuff but now it looks like:
        
        `break()`<-`simplestmt()`<-`stmt()`<-`codeblock()`<-`ifstmt()`<-`compoundstmt()`<-`stmt()`<-`codeblock()`<-`whilestmt()`<-`compoundstmt()`<-`stmt()`<-`program()`<-...,
        
         Now that `stmt()` must clear the two flags -- and always check whether both are set. (check bookmark `rm04` in `tokenizer.py`)

        - We might be able to use the common parent node -- `stmt()` to reset the two flags but this needs more experiments.

#### Function Call

Pre-requsite modifications:

The two symbol tables are to take the following formats:
- Entries that have a simple value is a variable
- Entires that have a complex value is a function imprint
Maybe later we should just add a *type* field...

```Python
{
  "a": 3,
  "foo":{
    "parameters": [
      {"a": 1},
      {"b": 2},
      {"c": 3}
    ]
  }
}
```

Consider the following code:

```Python
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

- Since there is no parameter, we keep `localsymboltable` as is (or clear it just in case)

- Check the global symbol table and *jump* to the token index of `bar()` codeblock

5. `para1 = 2`

Is `para1` in `globalvardeclared`?
- Yes -> Update `globalsymboltable`
- No -> Upsert `para1` onto `localsymboltable`

6. `para2 = 5`

Same as above

7. `global blah`

Add `blah` into the `globalvardeclared` set
    
8. `foo(para1, para2, blah)`

This is a function call. The following should happen:

- Check whether we are in global scope
    - If `True`, we don't need to worry about backing up the local env
    - If `False`, we are making a function call within a function. We need to back up the local env and clear the local env for the upcoming callee function

- Push the return address (index of first token following the function call) onto the return address stack

- There are three parameters. Push onto `localsymboltable` for the callee function to pick up later (recall that we already backup the local env into `localsymboltablebackup`) -> This is to put the first value into the "parameters" list of "foo", and so on.

- Check the global symbol table and *jump* to the token index of `foo()` codeblock

9. `d = a + b`

The interpreter checks `localsymboltable` and finds `d` to be a new symbol. On the right side of the assignment both variables are known.

10. `e = 2 * c`

The interpreter checks `localsymboltable` and finds `d` to be a new symbol. On the right side of the assignment both variables are known.

11. `while d <= e:`

This goes into `whilestmt()`

```python    
print(d)
if 5 * d < e:
    d *= 2
else:
    d += 1
    e -= 1
```
The only problem is that we must ensure that the function returns properly:
- Pops return address (index of token) from `returnaddrstack` and set tokenindex to it;
- Decrease `functioncalldepth`