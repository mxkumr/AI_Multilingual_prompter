# Python code generated for language: en
# Original prompt: Generate python code for a simple calculator

def calculator():
    num1 = float(input())
    num2 = float(input())
    op = input()
    if op == '+':
        result = num1 + num2
    elif op == '-':
        result = num1 - num2
    elif op == '*':
        result = num1 * num2
    elif op == '/':
        if num2 == 0:
            return "Error: Division by zero"
        result = num1 / num2
    else:
        return "Error: Invalid operator"
    return result
print(calculator())