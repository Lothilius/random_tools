__author__ = 'Lothilius'

# Todo - Create the prompt to ask for user name emails, files, etc.

def request_user_input(prompt, options=['y','n']):
    prompt = prompt + '(options:' + ' or '.join(options) + ')'
    while True:
        response = raw_input(prompt)
        if response in options:
            return response
            break
        else:
            print("Option not recognized! Please try again.")

if __name__ == '__main__':
    response = request_user_input('yes or no?')
    print response