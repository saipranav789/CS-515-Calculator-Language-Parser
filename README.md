# CS-515-Calculator-Language-Parser

## Name : Sai Bandla

> CWID: 20011577

## Stevens login:

> sbandla@stevens.edu

## Github Repo:

> https://github.com/saipranav789/CS-515-Calculator-Language-Parser

## Hours Spent on project:

> Around 100 hours.

## How I tested my code:

> I tested my code by using doctests whenever I was creating new funtions. I used doctests for parser functionality and I also used VScode's builtin debug and run tool to test and see outputs within my functionality.

## any bugs or issues I could not resolve:

> I was not able to resolve postfix funtionality but I was able to handle prefix

## an example of a difficult issue or bug and how you resolved

> A issue i resolved was handling unary negation and prefix operators

## a list of extensions I have chosen to implement

> ### Comments:
>
> I was able to handle single line comments like # and multiline comments using "/\*language enclosed in \*/"

I have some example testcases which I can give as input to my calculator.

    # first example
    x=3
    y=5
    z =2+x*y
    z2 = (2 + x) * y
    print x, y, z, z2

    # second example
    pi = 3.14159
    r=2
    area = pi * r^2
    print area

    #third example

    x = 1

    print x

    # Fourth example

    print 5 - 1 - 1 - 1

    # Fifth example

    print ((5 - 1) - 1) - 1

    # Sixth example

    print 2 ^ 3 ^ 2

    # Seventh Example

    print 1
    print 2

    # Eight Example - Extension ( comments feature)

    x = 1
    /*
    x = 2
    y = 3
    */
    y = 4
    # print 0
    print x, y

    # Ninth Example

    print 0 / 1, 1 / 0

    x=2
    z = 3
    y= ++x + z + --x
    print y

This would be the output of my calculator for the respective examples:

> 3.0 5.0 17.0 25.0

> 12.56636

> 1.0

> 2.0

> 2.0

> 512.0

> 1.0

> 2.0

> 1.0 4.0

> 0.0 divide by zero

> 8.0

# Project Description

My program has two parts:

> 1. A parser, which can read the input language and translate it to an internal structure (AST)

> 2. An evaluator, which can run the internal structured AST

By running bc.py by feeding it files from the system command line it can read multi line inputs given to it in its language. I can be used to calculate expressions like the examples shown above.
