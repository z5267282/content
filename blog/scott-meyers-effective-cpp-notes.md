---
title: Scott Meyers Effective CPP Notes
date: 2026-10-07
description: Interesting notes from reading Scott Meyer's book on CPP best practices
---

Notes from reading Scott Meyer's "Effective Modern C++". It was a great book and a lot can be learnt from the text, largely in part due to Scott's helpful and clear writing style.

## Emplacement vs insertion in containers

Use emplacement when you need to call a constructor to create a `T`. If you already have a `T`, emplacement is usually the same as regular insertion. Emplacement uses direct initialisation which can use constructors marked as `explicit`.

```cpp
// in std::vector header

auto data = std::vector<std::string>{};

// 2 ctor calls: std::string(char const*) + std::string(std::string&&)
data.push_back(std::string{"hey"})
/**
    in std::vector header:
    void push_back(std::string&& item); // item needs to be move constructed
*/

// 1 ctor call: std::string(char const*)
data.emplace_back("hey");
```

## Using init capturing in lambdas

Init capturing allows you to write an expression that initialises captured data. This means we can move-construct captured data.

```cpp
auto m = std::make_unique<int>(10);
// capture m, name it data in the lambda and move-construct it
auto work = [data=std::move(m)]() { std::cout << *data << '\n'; };
work();
```

## Avoid default capture modes

Default capturing is when a lambda capture is either `[&]` or `[=]`. These should be avoided as they can only capture non-static local variables: i.e. parameters and locals. You can't gain access to data members

```cpp
struct Data {
    int n;
    auto job() -> void {
        // all three of these won't work
        auto bad1 = []() { std::cout << n << '\n'; };
        auto bad2 = [&]() { std::cout << n << '\n'; };
        auto bad3 = [=]() { std::cout << n << '\n'; };
        // none have access to this->n which is what the compiler eventually inserts

        // solution
        auto good = [n_copy=n]() { std::cout << n_copy << '\n'; };
    }
```

## Declaration-only integral static-const and constexpr data members

This was a subpoint made in item 30 about the shortcomings of perfect forwarding. If you have data that is only declared but not defined as either `static const` or `constexpr`, the compiler performs `const`-propogation. This means that these variables are not given any memory and are placed by value where they are used. Hence you can't take the memory address of these.

```cpp
// data.h
struct Data {
    static constexpr int N = 7;
    auto work(int i) -> void {
        // 7 is replaced with N here
        auto ans = i + N;
        // this is not okay - failure at link time
        &N;
    }
```

Provide definitions of these in the implementation file to fix this.
This is also discussed in item 15: Use `constexpr` whenever possible.

```cpp
// data.cpp
constexpr auto Data::N;
```

This goes to a broader point: the difference between declaration and definition.

- declaration: write the name and type of a variable
- definition: allocate memory for it

## Moves are not always cheaper

There are certain edge cases like `std::array` where a move runs in linear time. This is because they don't use pointers to store data: all data is stored in the instance itself.

## Benefits of make\_ functions for smart pointers

Using `make_(unique|shared)` has benefits over directly creating smart pointers.

1. Avoid manually managing heap resources with `new`
2. Exception safety can be managed - if you run out of memory or throw an exception in constructing your heap resource,`make_` will run the destructor for the heap resource and free it

## Benefits of unique_ptr

`std::unique_ptr` has the ability to capture whether its resource is a singleton or array via type generic. For example `std::unique_ptr<int[]>` has an underlying array of integers and has `operator[]` but no `operator*`. You can easily convert from `std::unique_ptr` to `shd:shared_ptr` using a constructor.

## Why noexcept?

Noexcept means that an exception does not escape the body of a function. It enables optimisations, particularly for move operations. For example, `std::vector` will use move operations during reallocation if they are marked as `noexcept`. This can be checked using type traits - `std::is_nothrow_move_constructible`. Most functions however, are exception neutral - a function they call may throw an exception. Essentially, the exception is intended to be passed up the call chain.

## Use scoped enums (or enum classes)

Regular C-style enums suffer from issues like visibility and variable pollution. For example, you can't name a variable that shares a name with an enum variant.

```cpp
enum Color { red, white };
auto white = 27; // can't do this
```

Instead, use a scoped enum via the `enum class` keywords.

```cpp
enum class Color { red, white };
auto white = 27;         // okay
auto clr = Color::white; // okay
```

## Braces vs parentheses in constructors

If a class has constructors that take integral parameters, using braces will call the initialiser list constructor. For this reason, prefer parentheses when calling constructors.

```cpp
auto v1 = std::vector<int>(10, 20) // create vec with 10 elems, each with value 20
auto v2 = std::vector<int>{10, 20} // create vec with initialiser list elements {10, 20}
```

The exception to this rule, is that empty braces means the default (no-arg) constructor, not an empty initialiser list.

```cpp
auto v1 = std::vector<int>{}   // default ctor
auto v2 = std::vector<int>({}) // initialiser list ctor with no elems
```

### Most vexing parse - pains of braces (and AAA)

The "most vexing parse" is when a certain type of initialisation is interpreted as a function declaration. Annoyingly, writing this code is not a function call, but a declaration. For this reason, braces are associated with object creation.

```cpp
Data d1(); // declaration
Data d2{}; // creating a Data object
```

### How to initialise a std::size_t with auto

Another interesting side-note is that AAA and braces prevent narrowing conversions that parentheses would let slip. For example, this is the idiomatic way to create a `std::size_t` with AAA, that will fail compilation if a narrowing conversion is performed.

```cpp
auto bad = std::size_t{10.25}  // won't compile because of narrowing conversion
auto good = std::size_t{10}    // compiles

auto bad2 = std::size_t(10.25) // compiles and narrowing conversion is performed
```

## (Aside) Funny quotes

Scott has a great sense of dry humour and he made sure to sprinkle a few gems throughout the book.

> It's been said that the truth shall set you free, but under the right circumstances, a well-chosen lie can be quite liverating. ... Because we're dealing with software, however, let's eschew the word "lie" and instead say this Item comprises an "abstraction"

> Poets and songwriters have a thing bout love. And sometimes about counting ... we might try to enumerate the reasons why a raw pointer is hard to love
