
words = input("Enter String to test: ")

chars = {" ": "\ ",
        "(": "\(",
        ")": "\)",
        "'": "\\'"}
final = ""
for i, letter in enumerate(words):
    for char in chars:
        if letter == char:
            letter = chars[char]
            print("Replacing {} with {}".format(letter, chars[char]))

    final = final + letter

print(final)

